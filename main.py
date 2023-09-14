import socket
import os
import time
from LocalHost import LocalHost
import os


def get_network_interfaces():
# Mendapatkan daftar nama antarmuka jaringan
    interfaces = os.listdir('/sys/class/net/')
    return interfaces

def main():
    # Mendapatkan dan mencetak daftar nama antarmuka
    interface_names = get_network_interfaces()
    lhost = LocalHost("")
    print(f"Hostname : {lhost._hostname}")
    for name in interface_names:
        get_ip = lhost.getIp(name)
        print(f"interfaces {name} : {get_ip}")
    print("Welcome to file synhcronization")
    local_direktori = input("Masukkan direktori anda : ")
    lhost.localFolder = local_direktori
    
    
    
    

if __name__ == "__main__":
    main()
