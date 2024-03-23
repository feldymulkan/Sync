import paramiko
import hashlib
import subprocess
import socket
from Compare import compare



class SSHManager:
    def __init__(self, hostname, port, username, password):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.client = None  # Client akan dibuat saat koneksi pertama kali
        self.connect()  # Panggil fungsi untuk membuat koneksi

    def connect(self):
        try:
            self.client = self._create_ssh_client()
        except Exception as e:
            print(f"Error connecting to host: {str(e)}")
            self.client = None

    def _create_ssh_client(self):
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(self.hostname, port=self.port, username=self.username, password=self.password)
        return ssh_client

    def is_host_online(self):
        try:
            # Membuat objek socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Mengatur timeout koneksi
            sock.settimeout(1)
            # Mencoba melakukan koneksi ke host
            result = sock.connect_ex((self.hostname, self.port))
            # Menutup socket
            sock.close()

            # Jika hasilnya 0, artinya koneksi berhasil
            if result == 0:
                return True
            else:
                return False
        except Exception as e:
            print(f"Error when checking host status: {str(e)}")
            return False

    def send_file(self, local_path, remote_path):
        try:
            if not self.client:
                self.connect()  # Coba membuat koneksi jika belum ada
            sftp = self.client.open_sftp()
            sftp.put(local_path, remote_path)
            result=sftp.put(local_path, remote_path)
            
            if result is None:
                return True
                
            else: 
                return False
            
            
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
            command = f"rm -r '{remote_path}'"

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
            command = f"mkdir -p '{remote_path}'"
            
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
            file_size = sftp.stat(remote_file_path).st_size
            md5 = hashlib.md5()
            with sftp.file(remote_file_path, 'rb') as remote_file:
                bytes_read = 0
                while True:
                    # Read data in chunks
                    data = remote_file.read(4096)
                    if not data:
                        break
                    md5.update(data)
                    bytes_read += len(data)
            sftp.close()
            md5_hash = md5.hexdigest()
            return md5_hash

        except FileNotFoundError:
            print("File not found.")
            return None
        except Exception as e:
            print(f"Error calculating remote MD5 hash: {str(e)}")
            return None

    def check_remote_md5(self, remote_file_path):
        try:
            if not self.client:
                self.connect()

            stdin, stdout, stderr = self.client.exec_command(f"md5sum {remote_file_path}")
            md5_hash = stdout.read().decode().split()[0]

            return md5_hash.strip()
        except Exception as e:
            print(f"Error calculating remote MD5 hash: {str(e)}")
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
            is_file = sftp.stat(remote_path).st_mode and not sftp.stat(remote_path).st_mode & 0o040000
            sftp.close()
            return is_file
        except Exception as e:
            print(f"Error checking if file: {str(e)}")
            return False

    def send_changed_file_parts(self, local_path, remote_path):
        try:
            local_checksum = compare.calculate_md5(local_path)
            remote_checksum = self.calculate_remote_md5(remote_path)
            if local_checksum != remote_checksum:
                sftp = self.client.open_sftp()
                with open(local_path, 'rb') as local_file:
                    with sftp.file(remote_path, 'wb') as remote_file:
                        while True:
                            chunk = local_file.read(4096)
                            if not chunk:
                                break
                            remote_file.write(chunk)
                sftp.close()

                # print(f"Changed file parts transferred successfully from {local_path} to {remote_path}")

                return True
            else:
                print("File checksums match. No need to transfer.")

                return False

        except Exception as e:
            print(f"Error transferring changed file parts: {str(e)}")
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
            command = f"mv -f '{src_path}' '{dest_path}'"

            # Jalankan perintah SSH
            stdin, stdout, stderr = self.client.exec_command(command)
            exit_status = stdout.channel.recv_exit_status()

            if exit_status == 0:
                print(f"Folder moved from {src_path} to {dest_path}")
                pass
            else:
                error_message = stderr.read().decode()
                print(f"Failed moved from {src_path} to {dest_path}")
                print(f"Failed to move folder: {error_message}")

        except paramiko.SSHException as e:
            print(f"SSH Error: {str(e)}")
        except Exception as e:
            print(f"Error moving folder: {str(e)}")
            
    def reconnect(self):
        print("Reconnecting SSH...")
        self.close()  # Tutup koneksi yang ada
        self.connect()  # Coba membuat koneksi baru
        if self.client is not None:
            print("SSH reconnected successfully.")
        else:
            print("Failed to reconnect SSH.")


    # def compare_local_remote_metadata(self, local_path, remote_path):
    #     try:
    #         local_mtime = os.path.getmtime(local_path)
    #         local_checksum = compare.calculate_md5(local_path)

    #         remote_mtime, remote_checksum = self.get_remote_metadata(remote_path)

    #         return local_mtime, local_checksum, remote_mtime, remote_checksum

    #     except Exception as e:
    #         print(f"Error comparing file metadata: {str(e)}")
    #         return 0, "", 0, ""

    # def handle_metadata_comparison(self, local_path, remote_path):
    #     try:
    #         local_mtime, local_checksum, remote_mtime, remote_checksum = self.compare_local_remote_metadata(local_path, remote_path)

    #         if local_mtime != remote_mtime and local_checksum == remote_checksum:
    #             return True
    #         elif local_mtime == remote_mtime and local_checksum == remote_checksum:
    #             return True
    #         elif local_mtime != remote_mtime and local_checksum != remote_checksum:
    #             return False

    #     except Exception as e:
    #         print(f"Error handling metadata comparison: {str(e)}")
    #         return "Error in metadata comparison."

    # def calculate_checksum(self, file_path, algorithm="sha256"):
    #     hasher = hashlib.new(algorithm)
    #     with open(file_path, "rb") as file:
    #         while chunk := file.read(8192):
    #             hasher.update(chunk)
    #     return hasher.hexdigest()

    # def get_remote_metadata(self, remote_file_path):
    #     try:
    #         sftp = self.client.open_sftp()
    #         remote_mtime = sftp.stat(remote_file_path).st_mtime
    #         with sftp.file(remote_file_path, "rb") as remote_file:
    #             remote_checksum = self.calculate_checksum_from_file(remote_file)
    #         sftp.close()
    #         return remote_mtime, remote_checksum
    #     except Exception as e:
    #         print(f"Error getting remote file metadata: {str(e)}")
    #         return 0, ""

    # def calculate_checksum_from_file(self, file):
    #     hasher = hashlib.sha256()
    #     while chunk := file.read(8192):
    #         hasher.update(chunk)
    #     return hasher.hexdigest()

    def close(self):
        if self.client:
            self.client.close()
            self.client = None

    def __del__(self):
        self.close()
    
    
        

