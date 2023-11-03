import paramiko

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
            command = "whoami" 
            stdin, stdout, stderr = self.client.exec_command(command)

            stdout.channel.recv_exit_status()
            return True
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
            print(f"File deleted on {self.hostname}:{remote_path}")
        except Exception as e:
            print(f"Error deleting file: {str(e)}")

    def delete_folder(self, remote_path):
        try:
            ssh = self.client.invoke_shell()
            ssh.send(f'rm -r {remote_path}\n')
            while not ssh.recv_ready():
                pass
            response = ssh.recv(1024).decode()
            ssh.close()
            
            if "No such file or directory" in response:
                print(f"Folder does not exist on {self.hostname}:{remote_path}")
            else:
                print(f"Folder deleted on {self.hostname}:{remote_path}")
        except Exception as e:
            print(f"Error deleting folder: {str(e)}")

    def create_folder(self, remote_path):
        try:
            command = f'mkdir -p {remote_path}'
            
            stdin, stdout, stderr = self.client.exec_command(command)
            exit_status = stdout.channel.recv_exit_status()

            if exit_status == 0:
                print(f"Created folder on {self.hostname}:{remote_path}")
            else:
                error_message = stderr.read().decode()
                print(f"Failed to create folder on {self.hostname}:{remote_path}: {error_message}")
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

    def file_exists(self, remote_path):
            try:
                sftp = self.client.open_sftp()
                sftp.stat(remote_path)  # Coba mengambil informasi tentang remote_path
                sftp.close()
                return True
            except FileNotFoundError:
                return False  # Jika file tidak ditemukan
            except Exception as e:
                print(f"Error checking file existence: {str(e)}")
                return False

    def close(self):
        self.client.close()

