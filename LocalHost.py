import os
import socket
from Host import Host
import psutil

class LocalHost(Host):
    def __init__(self, localFolder):
        self._hostname = socket.gethostname()
        self.localFolder = localFolder
    
    def getLocalFolder(self):
        return self.localFolder

    def getIp(self, interface_name):
        try:
            addrs = psutil.net_if_addrs()
            if interface_name in addrs:
                ip_address = addrs[interface_name][0].address
                return ip_address
            else:
                return None
        except Exception as e:
            print(f"Terjadi kesalahan: {e}")
            return None


