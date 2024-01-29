import os
from Host.host import Host

host_info = Host.read_host_info("hostname.txt")

class GetFileManager:
    def __init__(self, ssh_manager, local_path):
        self.ssh_manager = ssh_manager
        self.remote_path = host_info.direktori
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
                        print(f"[*] Downloaded: {item}")
                    else:
                        print(f"[-] Skipped: {item} (Already up to date)")
                elif self.ssh_manager.is_directory(remote_item_path):
                    if not os.path.exists(local_item_path):
                        os.makedirs(local_item_path)
                        print(f"[*] Created folder: {item}")
                    self.download_files_from_server(remote_item_path, local_item_path)

        except Exception as e:
            print(f"Error: {str(e)}")

