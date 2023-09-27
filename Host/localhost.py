import socket
from Host.host import host

class localhost(host):
    def __init__(self, localFolder):
        self._hostname = socket.gethostname()
        self.localFolder = localFolder
    
    def getLocalFolder(self):
        return self.localFolder
    
    def getHostName(self):
        return self._hostname

    def setLocalFolder(self, value):
        self.localFolder = value




