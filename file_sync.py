import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from ssh_manager import SSHManager
from LocalHost import LocalHost
from Host import Host


LOG = 'log.txt'
# local_folder = LocalHost.getLocalFolder
# # Folder lokal untuk sinkronisasi

host_info = Host.read_host_info("hostname.txt")
ssh_manager = SSHManager(host_info.hostname, host_info.port, host_info.username, host_info.password)
observer = Observer()
class MyHandler(FileSystemEventHandler):
    def __init__(self, folderlocal, ssh_manager):
        self.folderlocal = folderlocal
        self.ssh_manager = ssh_manager
        self.total_files_sent = 0
        self.total_bytes_sent = 0

    # def list_files_and_folders(directory):
    #     files_and_folders = set()
    #     for root, dirs, files in os.walk(directory):
    #         for file in files:
    #             files_and_folders.add(os.path.join(root, file))
    #         for dir in dirs:
    #             files_and_folders.add(os.path.join(root, dir))
    #     return files_and_folders

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
        
    def on_created(self, event):
        try:
            # listFolderlocal = os.listdir(self.folderlocal)
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
                print(defFolder)
                ujung = os.path.basename(folder)
                print(os.path.join(defFolder, ujung))
        except Exception as e:
            print(f"Error: {str(e)}")
                    # end_time = time.time()

                    # # Menghitung response time
                    # response_time = end_time - start_time
                    # self.log(f"Response Time: {response_time:.4f} seconds")

                    # # Menghitung throughput (asumsi data yang dikirim dalam bytes)
                    # file_size = os.path.getsize(folder1Item)
                    # self.total_bytes_sent += file_size
                    # throughput = file_size / response_time
                    # self.log(f"Throughput: {throughput:.2f} bytes/s")

                    # # Menghitung kecepatan transfer (dalam MB/s)
                    # transfer_speed = throughput / (1024 * 1024)
                    # self.log(f"Transfer Speed: {transfer_speed:.2f} MB/s")

                    # # Menghitung data loss
                    # original_file_path = os.path.join(self.folder1, item)
                    # with open(original_file_path, 'rb') as original_file:
                    #     original_data = original_file.read()

                    # remote_file_path = os.path.join("/home/osboxes/server2", item)
                    # with self.ssh_manager.client.open_sftp().file(remote_file_path, 'rb') as remote_file:
                    #     remote_data = remote_file.read()

                    # if original_data == remote_data:
                    #     self.log("Data Loss: No")
                    # else:
                    #     self.log("Data Loss: Yes")

                    # self.total_files_sent += 1

# Menampilkan hasil pengukuran
# print("Total Files Sent:", event_handler.total_files_sent)
# print("Total Bytes Sent:", event_handler.total_bytes_sent)
