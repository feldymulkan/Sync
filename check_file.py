import paramiko

def check_file_existence(hostname, port, username, password, remote_path):
    try:
        # Membuat koneksi SSH
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=hostname, port=port, username=username, password=password)
        
        # Menggunakan SFTP untuk mengecek keberadaan file
        sftp = ssh_client.open_sftp()
        try:
            # Mencoba membuka file di remote_path
            sftp.stat(remote_path)
            print(f"File {remote_path} exists on the server.")
        except FileNotFoundError:
            print(f"File {remote_path} does not exist on the server.")
        finally:
            sftp.close()
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        ssh_client.close()

# Contoh penggunaan
hostname = "192.168.20.2"
port = 22
username = "server2"
password = "jarkom123"
remote_path = "/home/server2/file.txt"

check_file_existence(hostname, port, username, password, remote_path)
