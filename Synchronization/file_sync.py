import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from SSH.ssh_manager import SSHManager
from Host.Host import Host
from Compare.compare import compare_files

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
    
    def on_deleted(self, event):
        try:
            path = event.src_path
            remote_path = self.folder_enum(path, host_info.direktori)
            if event.is_directory:
                print(f"Directory deleted: {path}")
                # Hapus direktori di server menggunakan SSHManager
                ssh_manager.delete_folder(remote_path)
                self.log(f"Deleted folder on {host_info.hostname}:{remote_path}")
            else:
                print(f"File deleted: {path}")
                # Hapus file di server menggunakan SSHManager
                ssh_manager.delete_file(remote_path)
                self.log(f"Deleted file on {host_info.hostname}:{remote_path}")
        except Exception as e:
            print(f"Error: {str(e)}")

    def on_modified(self, event):
        try:
            path = event.src_path
            remote_path = self.folder_enum(path, host_info.direktori)

            if event.is_directory:
                print(f"Directory modified: {path}")
                # You can add your logic here for handling modified directories, if needed.
            else:
                print(f"File modified: {path}")
                folderFile = os.path.dirname(path)
                defFolder = self.folder_enum(folderFile, host_info.direktori)
                ujung = os.path.basename(path)
                full_path = os.path.join(defFolder, ujung)
                if ssh_manager.file_exists(full_path):
                    ssh_manager.send_file(path, full_path, overwrite=True)
                    self.log(f"Overwritten file on {host_info.hostname}:{full_path}")
        except Exception as e:
            print(f"Error: {str(e)}")

    def on_created(self, event):
        try:
            folder = event.src_path
            define_folder = self.folder_enum(folder, host_info.direktori)
            if event.is_directory:
                print(f"Directory created: {folder}")
                ssh_manager.create_folder(define_folder)
                self.log(f"Created folder on {host_info.hostname}:{define_folder}")
            else:
                print(f"File created: {folder}")
                folderFile = os.path.dirname(folder)
                defFolder = self.folder_enum(folderFile, host_info.direktori)
                ujung = os.path.basename(folder)
                full_path = os.path.join(defFolder, ujung)
                ssh_manager.send_file(folder, full_path)
                self.log(f"Created file on {host_info.hostname}:{full_path}")
        except Exception as e:
            print(f"Error: {str(e)}")