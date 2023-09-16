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
    
    def getHostName(self):
        return self._hostname

    def setLocalFolder(self, value):
        self.localFolder = value




