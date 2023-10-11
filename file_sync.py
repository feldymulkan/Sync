import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from SSH.ssh_manager import SSHManager
from Host.host import Host
from Host.localhost import localhost
from Compare.compare import compare_files, calculate_md5
# from Communication.establish import start_ssl_server
from Communication.client import send_message

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
                print(f"Directory deleted: {path}")
                # Hapus direktori di server menggunakan SSHManager
                ssh_manager.delete_folder(remote_path)
                self.log(f"Deleted folder on {host_info.hostname}:{remote_path}")
            elif not event.is_directory:
                print(f"File deleted: {path}")
                # Hapus file di server menggunakan SSHManager
                ssh_manager.delete_file(remote_path)
                self.log(f"Deleted file on {host_info.hostname}:{remote_path}")
        except Exception as e:
            print(f"Error: {str(e)}")

    def on_moved(self, event):
        try:
            src_path = event.src_path
            dest_path = event.dest_path
            if event.is_directory:
                print(f"Directory moved: {src_path} -> {dest_path}")
                def_folder1 = self.getServerFullPath(src_path)
                def_folder2 = self.getServerFullPath(dest_path)
                
                ssh_manager.rename_folder(def_folder1, def_folder2)
            elif not event.is_directory:
                print(f"File moved: {src_path} -> {dest_path}")
                # Logika untuk file yang diubah namanya, jika diperlukan.
                src_full_path = self.getServerFullPath(src_path)
                dest_full_path = self.getServerFullPath(dest_path)
                ssh_manager.delete_file(src_full_path)
                ssh_manager.send_file(dest_path, dest_full_path)
                if compare_files(dest_path, dest_full_path) == True:
                    self.log(f"Modified file on {host_info.hostname}:{dest_full_path}")
                else:
                   ssh_manager.delete_file(dest_full_path)
                   print("Failed to rename")
        except Exception as e:
            print(f"Error: {str(e)}")

    def on_created(self, event):
        try:
            # start ssl server untuk menerima pesan perubahan
            # start_ssl_server("server-cert.pem", "server-key.pem", lhost.getIP("wlo1"), 1024)
            folder = event.src_path
            define_folder = self.folder_enum(folder, host_info.direktori)
            if event.is_directory:
                print(f"Directory created: {folder}")
                ssh_manager.create_folder(define_folder)
                self.log(f"Created folder on {host_info.hostname}:{define_folder}")
            else:
        #         print(f"File created: {folder}")
        #         start_time = time.time()

        #         calculate_md5(folder)
        #         full_path = self.getServerFullPath(folder)
        #         server_add = (host_info.hostname, 1024)
        #         # send_message("server-cert.pem", "server-key.pem", server_add, "server2", full_path)
        #         if not ssh_manager.file_exists(full_path):
        #             ssh_manager.send_file(folder, full_path)
        #             end_time = time.time()
        #             transfer_time = end_time - start_time
        #             file_size = os.path.getsize(folder)
        #             transfer_speed = file_size / transfer_time  # Kecepatan transfer dalam bytes per detik

        #             # Format waktu kirim
        #             transfer_time_str = "{:.2f} seconds".format(transfer_time)
                    
        #             print(f"File transferred successfully: {full_path}")
        #             print(f"Transfer time: {transfer_time_str}")
        #             print(f"Transfer speed: {transfer_speed:.2f} bytes/second")
        #             self.log(f"Created file on {host_info.hostname}:{full_path} - Transfer time: {transfer_time_str}")
        #         else:
        #             print(f"File already exists on the server: {full_path}")
        # except Exception as e:
        #     print(f"Error: {str(e)}")

                # Kirim Direktori ke server 2
                
                print(f"File created: {folder}")
                calculate_md5(folder)
                full_path = self.getServerFullPath(folder)
                server_add = (host_info.hostname, 1024)
                # send_message("server-cert.pem", "server-key.pem", server_add, "server2", full_path)
                if not ssh_manager.file_exists(full_path):
                    ssh_manager.send_file(folder, full_path)
                    self.log(f"Created file on {host_info.hostname}:{full_path}")
                else:
                    print(f"File already exists on the server: {full_path}")
        except Exception as e:
            print(f"Error: {str(e)}")

