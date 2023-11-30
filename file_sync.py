import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from SSH.ssh_manager import SSHManager
from Host.host import Host
from Host.localhost import localhost
from Compare.compare import compare_md5, calculate_md5, is_same_filename

LOG = 'log.txt'

host_info = Host.read_host_info("hostname.txt")
ssh_manager = SSHManager(host_info.hostname, host_info.port, host_info.username, host_info.password)
observer = Observer()
lhost = localhost("")
status_modif = False 


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
    
    def modified(self, dir1, dir2):
        try:
            self.ssh_manager.send_file(dir1, dir2)
            if self.ssh_manager.check_existence(dir2):
                if compare_md5(dir1, self.ssh_manager.calculate_remote_md5(dir2)):
                    print(f"File Modified")
        except Exception as e:
            print(f"Modified Error: {str(e)}")

    def on_deleted(self, event):
            try:
                path = event.src_path
                remote_path = self.folder_enum(path, host_info.direktori)

                # Implementasi mekanisme konfirmasi (gunakan variabel atau logika yang sesuai)
                status_modif = False  # Gantilah dengan logika atau variabel yang sesuai

                if not status_modif:
                    if event.is_directory:
                        try:
                            if ssh_manager.check_existence(remote_path):
                                ssh_manager.delete_folder(remote_path)
                                self.log(f"Deleted folder on {host_info.hostname}:{remote_path}")
                        except Exception as e:
                            self.log(f"{remote_path} cannot be deleted: {str(e)}")
                    elif not event.is_directory:
                        try:
                            if ssh_manager.check_existence(remote_path) == True:
                                if compare_md5(calculate_md5(path), ssh_manager.calculate_remote_md5(remote_path)) == False:
                                # Bandingkan berdasarkan getmtime
                                    local_mtime = os.path.getmtime(path)
                                    remote_mtime = ssh_manager.get_file_mtime(remote_path)
                                    if local_mtime > remote_mtime:
                                        ssh_manager.delete_file(remote_path)
                                        self.log(f"Deleted older file on {host_info.hostname}:{remote_path}")
                                    else:
                                        print(f"File on {host_info.hostname}:{remote_path} is not older, not deleted")
                            else:
                                print(f"{remote_path} cannot be deleted")
                                self.log(f"{remote_path} cannot be deleted")
                        except Exception as e:
                            self.log(f"{remote_path} cannot be deleted: {str(e)}")
                else:
                    print("Deleted Cannot Be Undone")
            except Exception as e:
                print(f"Error: {str(e)}")
    
    def on_moved(self, event):
        try:
            status_modif = True
            src_path_server1 = event.src_path
            dest_path_server1 = event.dest_path
            if status_modif == True:
                if event.is_directory:
                    def_folder1 = self.getServerFullPath(src_path_server1)
                    def_folder2 = self.getServerFullPath(dest_path_server1)
                    ssh_manager.rename_folder(def_folder1, def_folder2)
                    self.log(f"Folder Modified on {host_info.hostname}:{def_folder2}")
                elif not event.is_directory:
                    src_full_path_server2 = self.getServerFullPath(src_path_server1)
                    dest_full_path_server2 = self.getServerFullPath(dest_path_server1)
                    if is_same_filename(dest_path_server1, dest_full_path_server2) == True:
                        if compare_md5(calculate_md5(dest_path_server1), ssh_manager.calculate_remote_md5(dest_full_path_server2)):
                            ssh_manager.delete_file(dest_full_path_server2)
                            self.modified(dest_path_server1, dest_full_path_server2)
                            # ssh_manager.send_file(dest_path_server1, dest_full_path_server2)
                    
                    if is_same_filename(dest_path_server1, src_full_path_server2) == False and calculate_md5(dest_path_server1) == ssh_manager.calculate_remote_md5(src_full_path_server2):
                        ssh_manager.rename_file(src_full_path_server2, dest_full_path_server2)
                        print("Rename file Success")
            else:
                print("Modified Error")
        except Exception as e:
            print(f"Error: {str(e)}")
    
    def on_created(self, event):
        try:
            server1_path = event.src_path
            define_folder = self.folder_enum(server1_path, host_info.direktori)
            if event.is_directory:
                if ssh_manager.check_existence(define_folder) == False:
                    ssh_manager.create_folder(define_folder)
                    if ssh_manager.check_existence(define_folder) == True: 
                        self.log(f"Created folder on {host_info.hostname}:{define_folder}")
                else:
                    print(f"Directory {define_folder} already created ")
            elif not event.is_directory:
                server2_path = self.getServerFullPath(server1_path)
                file_existance = ssh_manager.check_existence(server2_path)
                if file_existance == False:
                    ssh_manager.send_file(server1_path, server2_path)
                    if compare_md5(calculate_md5(server1_path),ssh_manager.calculate_remote_md5(server2_path)):
                        print(f"File Created {server2_path}")
                        self.log(f"Created file on {host_info.hostname}:{server2_path}")
                elif file_existance == True:
                    if calculate_md5(server1_path) == ssh_manager.calculate_remote_md5(server2_path):
                        print(f"{server2_path} already syncrhonized")
                    
        except Exception as e:
            print(f"Error: {str(e)}")

