import os
from ssh_manager import SSHManager

class Host:
    def __init__(self, hostname, port, username, password, direktori):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.direktori = direktori

    def read_host_info(filename):
        try:
            with open(filename, "r") as file:
                lines = file.readlines()

            host_info = {}
            # Loop melalui setiap baris dalam file
            for line in lines:
                parts = line.strip().split("=")
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip()
                    host_info[key] = value

            return host_info
        except Exception as e:
            print(f"Gagal membaca file {filename}: {str(e)}")
            return None
        
# host_info = Host.read_host_info("hostname.txt")
# if host_info:
#     hostname = host_info.get("hostname", "")
#     port = int(host_info.get("port",))
#     username = host_info.get("username", "")
#     password = host_info.get("password", "")
#     print(hostname)
#     print(port)
#     print(username)
#     print(password)

