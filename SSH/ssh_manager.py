import paramiko
import hashlib

class SSHManager:
    def __init__(self, hostname, port, username, password):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.client = self._create_ssh_client()

    def _create_ssh_client(self):
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(self.hostname, port=self.port, username=self.username, password=self.password)
        return ssh_client

    def is_host_online(self):
        try:
            transport = self.client.get_transport()
            
            if transport and transport.is_active():
                return True
            else:
                return False
        except Exception as e:
            print(f"Error when checking host status: {str(e)}")
            return False
        
    def send_file(self, local_path, remote_path):
        try:
            sftp = self.client.open_sftp()
            sftp.put(local_path, remote_path)
            sftp.close()
        except Exception as e:
            print(f"Error when sending file: {str(e)}")

    def download_file(self, remote_path, local_path):
        try:
            sftp = self.client.open_sftp()
            sftp.get(remote_path, local_path)
            sftp.close()
            print(f"File {remote_path} has been downloaded to {local_path}")
        except Exception as e:
            print(f"Error when downloading file: {str(e)}")

    def delete_file(self, remote_path):
        try:
            sftp = self.client.open_sftp()
            sftp.remove(remote_path)
            sftp.close()
            # print(f"File deleted on {self.hostname}:{remote_path}")
        except Exception as e:
            print(f"Error deleting file: {str(e)}")

    def delete_folder(self, remote_path):
        try:
            command = f'rm -r {remote_path}'

            stdin, stdout, stderr = self.client.exec_command(command)
            exit_status = stdout.channel.recv_exit_status()

            # if exit_status == 0:
            #     print(f"Folder deleted on {self.hostname}:{remote_path}")
            # else:
            #     error_message = stderr.read().decode()
            #     print(f"Failed to delete folder on {self.hostname}:{remote_path}: {error_message}")

        except paramiko.SSHException as e:
            print(f"SSH Error: {str(e)}")

        except Exception as e:
            print(f"Error deleting folder: {str(e)}")

    def send_and_replace_file(self, local_path, remote_path):
        try:
            # Cek apakah file di remote_path sudah ada
            if self.check_existence(remote_path):
                # Hapus file yang sudah ada di remote_path
                self.delete_file(remote_path)

            # Kirim file baru
            self.send_file(local_path, remote_path)
            
            # print(f"File sent and replaced on {self.hostname}:{remote_path}")
        except Exception as e:
            print(f"Error sending and replacing file: {str(e)}")
    
    def create_folder(self, remote_path):
        try:
            command = f'mkdir -p {remote_path}'
            
            stdin, stdout, stderr = self.client.exec_command(command)
            exit_status = stdout.channel.recv_exit_status()

            # if exit_status == 0:
            #     print(f"Created folder on {self.hostname}:{remote_path}")
            # else:
            #     error_message = stderr.read().decode()
            #     print(f"Failed to create folder on {self.hostname}:{remote_path}: {error_message}")
        except paramiko.SSHException as e:
            print(f"SSH Error: {str(e)}")
        except Exception as e:
            print(f"Error: {str(e)}")

    def rename_folder(self, src_path, dest_path):
        if not self.client:
            self.connect()

        try:
            sftp = self.client.open_sftp()
            sftp.rename(src_path, dest_path)
            sftp.close()
        except Exception as e:
            print(f"Error renaming folder: {str(e)}")
            
    def rename_file(self, src_path, dest_path):
        try:
            sftp = self.client.open_sftp()
            sftp.rename(src_path, dest_path)
            sftp.close()
        except Exception as e:
            print(f"Error renaming file: {str(e)}")
            
    def check_existence(self, remote_path):
        try:
            sftp = self.client.open_sftp()
            sftp.stat(remote_path)  # Mencoba mendapatkan informasi metadata file
            sftp.close()
            return True
        except FileNotFoundError:
            return False
        except Exception as e:
            print(f"Error when checking file existence: {str(e)}")
            return False 
     
    def calculate_remote_md5(self, remote_file_path):
        try:
            sftp = self.client.open_sftp()

            with sftp.file(remote_file_path, 'rb') as remote_file:
                md5 = hashlib.md5()
                while True:
                    data = remote_file.read(4096)
                    if not data:
                        break
                    md5.update(data)

                md5_hash = md5.hexdigest()

                sftp.close()

                return md5_hash

        except Exception as e:
            print(f"Error calculating remote MD5 hash,file has been deleted: {str(e)}")
            return None

    def list_files_and_folders(self, remote_path):
        try:
            sftp = self.client.open_sftp()
            file_list = sftp.listdir(remote_path)
            sftp.close()
            return file_list
        except Exception as e:
            print(f"Error listing files and folders: {str(e)}")
            return []

    def is_file(self, remote_path):
        try:
            sftp = self.client.open_sftp()
            # Cek apakah path adalah file (bukan direktori)
            is_file = sftp.stat(remote_path).st_mode and not sftp.stat(remote_path).st_mode & 0o040000
            sftp.close()
            return is_file
        except Exception as e:
            print(f"Error checking if file: {str(e)}")
            return False

    def is_directory(self, remote_path):
        try:
            sftp = self.client.open_sftp()
            # Cek apakah path adalah direktori
            is_directory = sftp.stat(remote_path).st_mode and sftp.stat(remote_path).st_mode & 0o040000
            sftp.close()
            return is_directory
        except Exception as e:
            print(f"Error checking if directory: {str(e)}")
            return False

    def get_file_mtime(self, remote_path):
        try:
            sftp = self.client.open_sftp()
            mtime = sftp.stat(remote_path).st_mtime
            sftp.close()
            return mtime
        except Exception as e:
            print(f"Error getting file modification time: {str(e)}")
            return 0

    def move(self, src_path, dest_path):
        try:
            # Buat perintah SSH untuk memindahkan folder
            command = f"mv {src_path} {dest_path}"

            # Jalankan perintah SSH
            stdin, stdout, stderr = self.client.exec_command(command)
            exit_status = stdout.channel.recv_exit_status()

            if exit_status == 0:
                # print(f"Folder moved from {src_path} to {dest_path}")
                pass
            else:
                error_message = stderr.read().decode()
                print(f"Failed to move folder: {error_message}")

        except paramiko.SSHException as e:
            print(f"SSH Error: {str(e)}")
        except Exception as e:
            print(f"Error moving folder: {str(e)}")

    def close(self):
        self.client.close()
    
    
        

