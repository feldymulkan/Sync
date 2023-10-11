import socket
import psutil

class localhost():
    def __init__(self, localFolder):
        self._hostname = socket.gethostname()
        self.localFolder = localFolder
    
    def getLocalFolder(self):
        return self.localFolder
    
    def getHostName(self):
        return self._hostname

    def setLocalFolder(self, value):
        self.localFolder = value

    def getIP(self, interface_name):
        try:
            interface = psutil.net_if_addrs()[interface_name]
            for ip in interface:
                if ip.family == socket.AF_INET:
                    return ip.address
        except KeyError as e:
            print("Interface tidak ada : " + e)
            return None

