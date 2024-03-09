import time
import os
import concurrent.futures
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from SSH.ssh_manager import SSHManager
from Host.host import Host
from Compare.compare import compare_md5, calculate_md5, is_same_filename, is_same_dirname, is_same_inode, get_absolute_path

LOG = 'log.txt'
host_info = Host.read_host_info("hostname.txt")
ssh_manager = SSHManager(host_info.hostname, host_info.port, host_info.username, host_info.password)
observer = Observer()


class MyHandler(FileSystemEventHandler):
    def __init__(self, folderlocal, ssh_manager, max_workers):
        self.folderlocal = folderlocal
        self.ssh_manager = ssh_manager
        self.total_create = 0
        self.total_delete = 0
        self.total_moved = 0
        self.total_modif = 0
        self.total_files_synced = 0
        self.total_bytes_synced = 0
        self.active = True
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)

        
    def calculate_send_speed_mbps(self,total_bytes_sent, start_time):
        current_time = time.time()
        elapsed_time = current_time - start_time
        total_bits_sent = total_bytes_sent * 8  # Mengonversi total byte menjadi bit
        total_mbps = (total_bits_sent / 1000000) / elapsed_time if elapsed_time > 0 else 0  # Menghitung total megabit per detik
        return round(total_mbps, 1), round(elapsed_time, 2) # Memanggil round() dengan parameter 1 untuk satu angka di belakang koma

    def setActive(self,data):
        self.active = data
    
    def getActive(self):
        return self.active
    
    def resetTotalFile(self):
        self.resetDelete()
        self.resetModif()
        self.resetMoved()
        self.resetCreated()
        
    def resetDelete(self):
        self.total_delete = 0
        
    def resetModif(self):
        self.total_modif =0 
    
    def resetMoved(self):
        self.total_moved = 0
    
    def resetCreated(self):
        self.total_create = 0
        
    def get_file_synced(self):
        self.total_files_synced = self.total_create + self.total_delete + self.total_modif + self.total_moved
        return self.total_files_synced
    
    def get_fileSync_realtime(self):
        total = self.get_file_synced()
        if total:    
            while True:
                return total
        time.sleep(1)
        
    def print_synced_files(self):
        while True:
            print(f"Total Modified Files: {self.get_file_synced()}", end='\r')
            time.sleep(1)

    def log(self, message):
        now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        with open(LOG, 'a') as f:
            f.write('[' + now + ']' + message + '\n')

    def folder_enum(self, direktori, remote_folder):
        dirs = direktori.split('/')
        newfolder_parts= []
        start_adding = False
        for dir_part in dirs:
            if dir_part == os.path.basename(self.folderlocal):
                start_adding = True
            elif start_adding:
                newfolder_parts.append(dir_part)
        new_folder_fix = os.path.join(remote_folder, *newfolder_parts)
        return new_folder_fix
    
    def getServerFullPath(self, path_server):
        folder = os.path.dirname(path_server)
        defFolder = self.folder_enum(folder, host_info.direktori)
        ujung = os.path.basename(path_server)
        full_path = os.path.join(defFolder, ujung)
        return full_path
    
    def process_event(self, event):
        try:
            if event.event_type == 'deleted':
                self.on_deleted(event)
            elif event.event_type == 'moved':
                self.on_moved(event)
            elif event.event_type == 'created':
                self.on_created(event)
            elif event.event_type == 'modified':
                self.on_modified(event)
        except Exception as e:
            print(f"[!] Error: {str(e)}")

    def ignore_tempfile(self, path):
        ignore_patterns = ['.swp', '.temp', '.tmp']
        if '.goutputstream-' in os.path.basename(path):
            return True
        filename, file_extension = os.path.splitext(os.path.basename(path))
        if file_extension.lower() in ignore_patterns:
            return True
        return False

    def on_modified(self, event):
        self.executor.submit(self.process_modified, event)
        
    def process_modified(self, event):
        try:
            server1_path = event.src_path
            server2_path = self.getServerFullPath(server1_path)
            if self.active:
                if event.is_directory:
                    pass
                elif not event.is_directory:    
                    if not server1_path.startswith('.') or not server2_path.startswith('.'):
                        if not self.ignore_tempfile(server1_path):
                            if is_same_filename(server1_path,server2_path):
                                file_existence = ssh_manager.check_existence(server2_path)
                                if file_existence:
                                    local_modified_time = os.path.getmtime(server1_path)
                                    remote_modified_time = ssh_manager.get_file_mtime(server2_path)
                                    if local_modified_time > remote_modified_time: 
                                        if calculate_md5(server1_path)!= ssh_manager.calculate_remote_md5(server2_path):
                                            ssh_manager.send_changed_file_parts(server1_path, server2_path)
                                            if file_existence == True and calculate_md5(server1_path)== ssh_manager.calculate_remote_md5(server2_path):
                                                # self.total_files_synced +=1
                                                print(f'[*] Modified file on: {host_info.hostname}:{server2_path}')
                                                self.total_modif += 1
            else:
                if event.is_directory:
                    pass
                elif not event.is_directory:
                    print(f'[*] Modified local file on: {server1_path}')
                                            
        except Exception as e:
            print('[!] Failed to handle modified event: {}'.format(e))

    def on_created(self, event):
        self.executor.submit(self.process_created, event)

    def process_created(self, event):
        try:
            server1_path = event.src_path
            server2_path = self.getServerFullPath(server1_path)
            if self.active:
                if os.path.basename(server1_path).startswith('.') == False:
                    if not self.ignore_tempfile(server1_path) or not self.ignore_tempfile(server2_path):
                        define_folder = self.folder_enum(server1_path, host_info.direktori)
                        if event.is_directory:
                            if not ssh_manager.check_existence(define_folder):
                                ssh_manager.create_folder(define_folder)
                                if ssh_manager.check_existence(define_folder): 
                                    self.log(f"[*] Created folder: {host_info.hostname}:{define_folder}")
                                    print(f"[*] Created folder: {host_info.hostname}:{define_folder}")
                                    self.total_create += 1
                            else:
                                print(f"[+] Folder already created ")
                        elif not event.is_directory:
                            file_existence = ssh_manager.check_existence(server2_path)
                            if not file_existence:
                                start = time.time()
                                ssh_manager.send_file(server1_path, server2_path)
                                total_bytes = os.path.getsize(server1_path)
                                send_speed , timeSpend= self.calculate_send_speed_mbps(total_bytes, start)

                                if calculate_md5(server1_path) == ssh_manager.calculate_remote_md5(server2_path):
                                    send_speed , timeSpend= self.calculate_send_speed_mbps(total_bytes, start)
                                    self.log(f"[*] Created file: {host_info.hostname}:{server2_path}")
                                    print(f"[*] File Created: {host_info.hostname}:{server2_path} : {send_speed} mb/sec : {timeSpend} seconds")
                                    self.total_create += 1

        except Exception as e:
            print(f"[!] Error in on_created: {str(e)}")

    def on_deleted(self, event):
        
        self.executor.submit(self.process_deleted, event)

    def process_deleted(self, event):
        try:
            path = event.src_path
            remote_path = self.folder_enum(path, host_info.direktori)
            if self.active:
                if not path.startswith('.') or not remote_path.startswith('.'):
                    if not self.ignore_tempfile(path) or not self.ignore_tempfile(remote_path):
                        if event.is_directory:
                            if ssh_manager.check_existence(remote_path):
                                ssh_manager.delete_folder(remote_path)
                                self.log(f"[*] Deleted folder: {host_info.hostname}:{remote_path}")
                                print(f"[*] Deleted folder: {host_info.hostname}:{remote_path}")
                                self.total_delete += 1
                        elif not event.is_directory:
                            if ssh_manager.check_existence(remote_path):
                                ssh_manager.delete_file(remote_path)
                                self.log(f"[*] Deleted file: {host_info.hostname}:{remote_path}")
                                print(f"[*] Deleted file: {host_info.hostname}:{remote_path}")
                                self.total_delete += 1
                            else:
                                self.log(f"[!] {remote_path} cannot be deleted as it doesn't exist on the server.")
                                print(f"[!] {remote_path} cannot be deleted as it doesn't exist on the server.")
            else:
                print(f'[*] Deleted local file on: {path}')
        except Exception as e:
            print(f"[!] Error during deletion of {remote_path}: {e}")

    def on_moved(self, event):
        self.executor.submit(self.process_moved, event)

    def process_moved(self, event):
        try:
            src_path_server1 = event.src_path
            dest_path_server1 = event.dest_path
            if self.active:
                if event.is_directory:
                    def_folder1 = self.getServerFullPath(src_path_server1)
                    def_folder2 = self.getServerFullPath(dest_path_server1)
                    if not is_same_dirname(def_folder1, def_folder2):
                        ssh_manager.rename_folder(def_folder1, def_folder2)
                        self.log(f"[*] Renamed folder: {host_info.hostname}:{def_folder2}")
                        print(f"[*] Renamed folder: {host_info.hostname}:{def_folder2}")
                        self.total_moved += 1
                    if src_path_server1 != dest_path_server1:
                        ssh_manager.move(def_folder1, def_folder2)
                        self.log(f"[*] Moved folder to: {host_info.hostname}:{def_folder2}")
                        print(f"[*] Moved folder to: {host_info.hostname}:{def_folder2}")
                        self.total_moved += 1

                elif not event.is_directory:
                    src_full_path_server2 = self.getServerFullPath(src_path_server1)
                    dest_full_path_server2 = self.getServerFullPath(dest_path_server1)
                    if not src_path_server1.startswith('.') or not src_full_path_server2.startswith('.'):
                        if self.ignore_tempfile(src_path_server1) or self.ignore_tempfile(src_full_path_server2):
                            if is_same_filename(dest_path_server1, dest_full_path_server2) and calculate_md5(
                                    dest_path_server1) != ssh_manager.calculate_remote_md5(dest_full_path_server2):
                                ssh_manager.send_changed_file_parts(dest_path_server1, dest_full_path_server2)
                                print(f'[*] Modified file on: {host_info.hostname}:{dest_full_path_server2}')
                                self.total_moved += 1
                        elif not (self.ignore_tempfile(src_path_server1) or self.ignore_tempfile(dest_path_server1)):
                            if not is_same_filename(dest_path_server1,
                                                     src_full_path_server2) and calculate_md5(
                                dest_path_server1) == ssh_manager.calculate_remote_md5(src_full_path_server2):
                                ssh_manager.rename_file(src_full_path_server2, dest_full_path_server2)
                                print(f"[*] Rename file Success: {host_info.hostname}:{src_full_path_server2} => {host_info.hostname}:{dest_full_path_server2}")
                                self.total_moved += 1
                            elif src_path_server1 != dest_path_server1:
                                ssh_manager.move(src_full_path_server2, dest_full_path_server2)
                                self.log(f"[*] Moved file to: {host_info.hostname}:{dest_full_path_server2}")
                                print(f"[*] Moved file to: {host_info.hostname}:{dest_full_path_server2}")
                                self.total_moved += 1
                            else:
                                print("TES")
                                ssh_manager.send_and_replace_file(dest_path_server1, dest_full_path_server2)
                                self.total_moved += 1
            else:
                print(f'[*] Modified local file on: {src_path_server1}')
        except Exception as e:
            print(f"[!] Error in on_moved: {str(e)}")

