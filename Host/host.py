class Host:
    def __init__(self, hostname, port, username, password, direktori):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.direktori = direktori

    @classmethod
    def read_host_info(cls, filename):
        host_info = {}
        try:
            with open(filename, "r") as file:
                lines = file.readlines()
            for line in lines:
                parts = line.strip().split("=")
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip()
                    host_info[key] = value
        except Exception as e:
            print(f"Gagal membaca file {filename}: {str(e)}")
            return None

        return cls(
            hostname=host_info.get("hostname"),
            port=int(host_info.get("port", 22)),  # Port default adalah 22 jika tidak ada nilai yang diberikan
            username=host_info.get("username"),
            password=host_info.get("password"),
            direktori=host_info.get("direktori")
        )

