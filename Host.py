class Host:
    def __init__(self, hostname, port, username, password, direktori):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.direktori = direktori

    @classmethod
    def read_host_info(cls, filename):
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

            # Membaca nilai-nilai yang dibaca dari file dan membuat instance Host
            return cls(
                hostname=host_info.get("hostname"),
                port=int(host_info.get("port")),
                username=host_info.get("username"),
                password=host_info.get("password"),
                direktori=host_info.get("direktori")
            )
        except Exception as e:
            print(f"Gagal membaca file {filename}: {str(e)}")
            return None

