import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from concurrent.futures import ThreadPoolExecutor
from SSH.ssh_manager import SSHManager
from Host.host import Host
from Compare.compare import compare_md5, calculate_md5, is_same_filename, is_same_dirname, is_same_inode, get_absolute_path

LOG = 'log.txt'
host_info = Host.read_host_info("hostname.txt")
ssh_manager = SSHManager(host_info.hostname, host_info.port, host_info.username, host_info.password)
observer = Observer()

class MyHandler(FileSystemEventHandler):
    def __init__(self, folderlocal, ssh_manager):
        self.folderlocal = folderlocal
        self.ssh_manager = ssh_manager
        self.total_files_sent = 0
        self.total_bytes_sent = 0

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
        try:
            server1_path = event.src_path
            server2_path = self.getServerFullPath(server1_path)
            if ssh_manager.handle_metadata_comparison(server1_path, server2_path) == False:
                if event.is_directory:
                    pass
                elif not event.is_directory:    
                    if not self.ignore_tempfile(server1_path):
                        if is_same_filename(server1_path,server2_path):
                            file_existence = ssh_manager.check_existence(server2_path)
                            if file_existence:
                                local_modified_time = os.path.getmtime(server1_path)
                                remote_modified_time = ssh_manager.get_file_mtime(server2_path)
                                if local_modified_time > remote_modified_time: 
                                    if calculate_md5(server1_path)!= ssh_manager.calculate_remote_md5(server2_path):
                                        ssh_manager.send_and_replace_file(server1_path, server2_path)
                                        if file_existence == True and calculate_md5(server1_path)== ssh_manager.calculate_remote_md5(server2_path):
                                            print(f'[*] Modified file on: {host_info.hostname}:{server2_path}')
        except Exception as e:
            print('[!] Failed to handle modified event: {}'.format(e))

    def on_created(self, event):
        try:
            server1_path = event.src_path
            server2_path = self.getServerFullPath(server1_path)
            
            if not self.ignore_tempfile(server1_path) and not self.ignore_tempfile(server2_path):
                define_folder = self.folder_enum(server1_path, host_info.direktori)
                if event.is_directory:
                    if not ssh_manager.check_existence(define_folder):
                        ssh_manager.create_folder(define_folder)
                        if ssh_manager.check_existence(define_folder): 
                            self.log(f"[*] Created folder: {host_info.hostname}:{define_folder}")
                            print(f"[*] Created folder: {host_info.hostname}:{define_folder}")
                    else:
                        print(f"[+] Folder already created ")
                elif not event.is_directory:
                    file_existence = ssh_manager.check_existence(server2_path)
                    if not file_existence:
                        ssh_manager.send_file(server1_path, server2_path)
                        if calculate_md5(server1_path) == ssh_manager.calculate_remote_md5(server2_path):
                            print(f"[*] File Created: {server2_path}")
                            self.log(f"[*] Created file: {host_info.hostname}:{server2_path}")
        except Exception as e:
            print(f"[!] Error in on_created: {str(e)}")

    def on_deleted(self, event):
        try:
            path = event.src_path
            remote_path = self.folder_enum(path, host_info.direktori)
            if not self.ignore_tempfile(path) and not self.ignore_tempfile(remote_path):
                if event.is_directory:
                    if ssh_manager.check_existence(remote_path):
                        ssh_manager.delete_folder(remote_path)
                        self.log(f"[*] Deleted folder: {host_info.hostname}:{remote_path}")
                        print(f"[*] Deleted folder: {host_info.hostname}:{remote_path}")
                elif not event.is_directory:
                    if ssh_manager.check_existence(remote_path):
                        ssh_manager.delete_file(remote_path)
                        self.log(f"[*] Deleted file: {host_info.hostname}:{remote_path}")
                        print(f"[*] Deleted file: {host_info.hostname}:{remote_path}")
                    else:
                        self.log(f"[!] {remote_path} cannot be deleted as it doesn't exist on the server.")
                        print(f"[!] {remote_path} cannot be deleted as it doesn't exist on the server.")
        except Exception as e:
            print(f"[!] Error during deletion of {remote_path}: {e}")

    def on_moved(self, event):
        try:
            src_path_server1 = event.src_path
            dest_path_server1 = event.dest_path
            if event.is_directory:
                def_folder1 = self.getServerFullPath(src_path_server1)
                def_folder2 = self.getServerFullPath(dest_path_server1)
                if not is_same_dirname(def_folder1, def_folder2):
                    ssh_manager.rename_folder(def_folder1, def_folder2)
                    self.log(f"[*] Renamed folder: {host_info.hostname}:{def_folder2}")
                    print(f"[*] Renamed folder: {host_info.hostname}:{def_folder2}")
                if src_path_server1 != dest_path_server1:
                    ssh_manager.move(def_folder1, def_folder2)
                    self.log(f"[*] Moved folder to: {host_info.hostname}:{def_folder2}")
                    print(f"[*] Moved folder to: {host_info.hostname}:{def_folder2}")
                
            elif not event.is_directory:
                
                src_full_path_server2 = self.getServerFullPath(src_path_server1)
                dest_full_path_server2 = self.getServerFullPath(dest_path_server1)
                if ssh_manager.handle_metadata_comparison(dest_path_server1, dest_full_path_server2) == False:
                    if self.ignore_tempfile(src_path_server1) and self.ignore_tempfile(src_full_path_server2):
                        if is_same_filename(dest_path_server1, dest_full_path_server2) and calculate_md5(dest_path_server1) != ssh_manager.calculate_remote_md5(dest_full_path_server2):
                            ssh_manager.send_and_replace_file(dest_path_server1, dest_full_path_server2)
                            print(f'[*] Modified file on: {host_info.hostname}:{dest_full_path_server2}')
                    elif not (self.ignore_tempfile(src_path_server1) and self.ignore_tempfile(dest_path_server1)):
                        if not is_same_filename(dest_path_server1, src_full_path_server2) and calculate_md5(dest_path_server1) == ssh_manager.calculate_remote_md5(src_full_path_server2):
                            ssh_manager.rename_file(src_full_path_server2, dest_full_path_server2)
                            print(f"[*] Rename file Success: {src_full_path_server2} => {dest_full_path_server2}")
                        elif src_path_server1 != dest_path_server1:
                            ssh_manager.move(src_full_path_server2, dest_full_path_server2)
                            self.log(f"[*] Moved file to: {host_info.hostname}:{dest_full_path_server2}")
                            print(f"[*] Moved file to: {host_info.hostname}:{dest_full_path_server2}")
                        else:
                            ssh_manager.send_and_replace_file(dest_path_server1, dest_full_path_server2)
        except Exception as e:
            print(f"[!] Error in on_moved: {str(e)}")
def start_watchdog(folderlocal, ssh_manager):
    observer = Observer()
    handler = MyHandler(folderlocal, ssh_manager)
    observer.schedule(handler, path=folderlocal, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    finally:
        observer.join()
        observer.stop()

def run_prog(folder_path, ssh_manager):
    with ThreadPoolExecutor() as executor:
        executor.submit(start_watchdog, folder_path, ssh_manager)



# if __name__ == "__main__":
#     with ThreadPoolExecutor() as executor:
#         executor.submit(start_watchdog, '/home/cipeng/server1', ssh_manager)
