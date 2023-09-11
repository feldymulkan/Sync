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

    def send_file(self, local_path, remote_path):
        sftp = self.client.open_sftp()
        sftp.put(local_path, remote_path)
        sftp.close()

    def create_folder(self, remote_path):
        print(remote_path)
        command = f'mkdir -p {remote_path}'
        stdin, stdout, stderr = self.client.exec_command(command)
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            print(f"Created folder on {self.hostname}:{remote_path}")
        else:
            error_message = stderr.read().decode()
            print(f"Failed to create folder on {self.hostname}:{remote_path}: {error_message}")

    def close(self):
        self.client.close()

# # Contoh penggunaan:
# if __name__ == "__main__":
#     ssh_manager = SSHManager('192.168.1.28', 22, 'osboxes', 'osboxes.org')
#     remote_folder_path = '/home/osboxes/server2/'
#     dirs = remote_folder_path.split('/')

#     ssh_manager.create_folder(remote_folder_path+dirs[0])
#     ssh_manager.close()
