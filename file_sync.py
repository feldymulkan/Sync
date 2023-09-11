import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from ssh_manager import SSHManager

LOG = 'log.txt'
# Folder lokal untuk sinkronisasi
local_folder1 = "/home/kali/server1"
class MyHandler(FileSystemEventHandler):
    def __init__(self, folder1, ssh_manager):
        self.folder1 = folder1
        self.ssh_manager = ssh_manager
        self.total_files_sent = 0
        self.total_bytes_sent = 0

    def list_files_and_folders(directory):
        files_and_folders = set()
        for root, dirs, files in os.walk(directory):
            for file in files:
                files_and_folders.add(os.path.join(root, file))
            for dir in dirs:
                files_and_folders.add(os.path.join(root, dir))
        return files_and_folders

    def log(self, message):
        now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        with open(LOG, 'a') as f:
            f.write('[' + now + ']' + message + '\n')

    def on_created(self, event):
        remote_folder = "/home/osboxes/server2/"
        listFolder1 = os.listdir(self.folder1)
        if event.is_directory:
            print(f"Directory created: {event.src_path}")
            folder = event.src_path
            dirs = folder.split('/')
            newfolder_parts= []
            start_adding = False
            for dir_part in dirs:
                if dir_part == os.path.basename(local_folder1):
                    start_adding = True
                elif start_adding:
                    newfolder_parts.append(dir_part)
            new_folder_fix = os.path.join(remote_folder, *newfolder_parts)
            
            ssh_manager.create_folder(new_folder_fix)
            # ssh_manager.create_folder()
        else:
            print(f"File created: {event.src_path}")
            for item in listFolder1:
                folder1Item = os.path.join(self.folder1, item)
                if os.path.isfile(folder1Item):
                    start_time = time.time()
                    self.log(f"Copying {item} to remote server")
                    remote_path = os.path.join(remote_folder, item)
                    self.ssh_manager.send_file(folder1Item, remote_path)
                    end_time = time.time()

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

# Informasi koneksi SSH
hostname = "192.168.1.28"
port = 22
username = "osboxes"
password = "osboxes.org"

# Inisialisasi SSHManager
ssh_manager = SSHManager(hostname, port, username, password)

event_handler = MyHandler(local_folder1, ssh_manager)
observer = Observer()
observer.schedule(event_handler, path=local_folder1, recursive=True)
observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()

observer.join()

# Tutup koneksi SSH setelah selesai
ssh_manager.close()

# Menampilkan hasil pengukuran
print("Total Files Sent:", event_handler.total_files_sent)
print("Total Bytes Sent:", event_handler.total_bytes_sent)
