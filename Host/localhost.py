import socket
import psutil

class localhost():
    def __init__(self, localFolder, interface, port):
        self._hostname = socket.gethostname()
        self._localFolder = localFolder
        self._interface = interface
        self._port = port
    
    @classmethod
    def read_localhost_info(cls, filename):
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
            localFolder=host_info.get("localdir"),
            interface=host_info.get("interface"),
            port=host_info.get("port")
        )
    
    def getLocalFolder(self):
        return self._localFolder
    
    def getHostName(self):
        return self._hostname

    def getInterface(self):
        return self._interface
    
    def getPort(self):
        return self._port
    
    def setLocalFolder(self, value):
        self._localFolder = value

    def getActiveInterfaceIP(self):
        try:
            # Dapatkan semua antarmuka jaringan yang aktif
            active_interfaces = [self.getIP(_interface) for _interface, addrs in psutil.net_if_addrs().items() if addrs]

            return active_interfaces

        except Exception as e:
            print("Error:", e)
        return []

    def printActiveInterfaces(self):
        active_interfaces = psutil.net_if_addrs()
        if active_interfaces:
            print("Antarmuka jaringan yang aktif:")
            for interface_name, addrs in active_interfaces.items():
                print(f"- {interface_name}:")
                for addr in addrs:
                    print(f"  {addr.family.name}: {addr.address}")
        else:
            print("Tidak ada antarmuka jaringan yang aktif.")
    
    def getIP(self, interface_name):
        try:
            _interface = psutil.net_if_addrs().get(interface_name)
            if _interface:
                for ip in _interface:
                    if ip.family == socket.AF_INET:
                        return ip.address
        except Exception as e:
            print(f"Error: {e}")
        return None
