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
    
    def on_deleted(self, event):
        try:
            path = event.src_path
            remote_path = self.folder_enum(path, host_info.direktori)
            if event.is_directory:
                try:
                    if ssh_manager.check_existence(remote_path) == True:
                        ssh_manager.delete_folder(remote_path)
                        self.log(f"Deleted folder on {host_info.hostname}:{remote_path}")
                except Exception as e:
                    self.log(f"{remote_path} cannot deleting this folder")
                    print("Cannot deleting this folder" + e)
                
            elif not event.is_directory:
                try:
                    if ssh_manager.check_existence(remote_path) == True:
                        ssh_manager.delete_file(remote_path)
                        self.log(f"Deleted file on {host_info.hostname}:{remote_path}")
                    else:
                        self.log(f"{remote_path} cannot deleting this file")
                except Exception as e:
                    self.log(f"{remote_path} cannot deleting this folder")
                    print("Cannot deleting this file" + e)
        except Exception as e:
            print(f"Error: {str(e)}")
            
    def on_moved(self, event):
        try:
            src_path_server1 = event.src_path
            dest_path_server1 = event.dest_path
            if event.is_directory:
                def_folder1 = self.getServerFullPath(src_path_server1)
                def_folder2 = self.getServerFullPath(dest_path_server1)
                ssh_manager.rename_folder(def_folder1, def_folder2)
                self.log(f"Folder Modified on {host_info.hostname}:{def_folder2}")
            elif not event.is_directory:
                src_full_path_server2 = self.getServerFullPath(src_path_server1)
                dest_full_path_server2 = self.getServerFullPath(dest_path_server1)
                if is_same_filename(dest_path_server1, dest_full_path_server2) == True:
                    if calculate_md5(dest_path_server1) == ssh_manager.calculate_remote_md5(dest_full_path_server2):
                        ssh_manager.delete_file(dest_full_path_server2)
                        ssh_manager.send_file(dest_path_server1, dest_full_path_server2)
                
                if is_same_filename(dest_path_server1, src_full_path_server2) == False and calculate_md5(dest_path_server1) == ssh_manager.calculate_remote_md5(src_full_path_server2):
                    ssh_manager.rename_file(src_full_path_server2, dest_full_path_server2)
                    print("Rename file Success")
                else:
                    ssh_manager.delete_file(src_full_path_server2)
                    ssh_manager.send_file(dest_path_server1, dest_full_path_server2)
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
                    print(f"Folder already created ")
            elif not event.is_directory:
                server2_path = self.getServerFullPath(server1_path)
                file_existance = ssh_manager.check_existence(server2_path)
                if file_existance == False:
                    ssh_manager.send_file(server1_path, server2_path)
                    if calculate_md5(server1_path) == ssh_manager.calculate_remote_md5(server2_path):
                        print(f"File Created {server2_path}")
                        self.log(f"Created file on {host_info.hostname}:{server2_path}")
                    
        except Exception as e:
            print(f"Error: {str(e)}")
