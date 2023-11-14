import os
from SSH.ssh_manager import SSHManager

class GetFileManager:
    def __init__(self, ssh_manager, remote_path, local_path):
        self.ssh_manager = ssh_manager
        self.remote_path = remote_path
        self.local_path = local_path

    def download_files_from_server(self, remote_path=None, local_path=None):
        if remote_path is None:
            remote_path = self.remote_path
        if local_path is None:
            local_path = self.local_path

        try:
            files_and_folders = self.ssh_manager.list_files_and_folders(remote_path)
            for item in files_and_folders:
                remote_item_path = os.path.join(remote_path, item)
                local_item_path = os.path.join(local_path, item)
                
                if self.ssh_manager.is_file(remote_item_path):
                    if not os.path.exists(local_item_path) or os.path.getmtime(local_item_path) < self.ssh_manager.get_file_mtime(remote_item_path):
                        self.ssh_manager.download_file(remote_item_path, local_item_path)
                        print(f"Downloaded: {item}")
                    else:
                        print(f"Skipped: {item} (Already up to date)")
                elif self.ssh_manager.is_directory(remote_item_path):
                    if not os.path.exists(local_item_path):
                        os.makedirs(local_item_path)
                        print(f"Created folder: {item}")
                    self.download_files_from_server(remote_item_path, local_item_path)

        except Exception as e:
            print(f"Error: {str(e)}")

def main():
    # Informasi koneksi SSH
    hostname = 'hostname_server'
    port = 22
    username = 'username_ssh'
    password = 'password_ssh'
    
    # Path di server dan lokal
    remote_path = '/path/to/remote/directory'
    local_path = '/path/to/local/directory'

    # Membuat objek SSHManager
    ssh_manager = SSHManager(hostname, port, username, password)
    
    # Membuat objek GetFileManager
    file_manager = GetFileManager(ssh_manager, remote_path, local_path)
    
    # Mendownload file dan subfolder dari server
    file_manager.download_files_from_server()

    # Menutup koneksi SSH
    ssh_manager.close()

if __name__ == "__main__":
    main()
