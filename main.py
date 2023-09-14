import socket
import os
import time
from LocalHost import LocalHost
import os

def cetak():
    artwork = """
    __   __                              
    \ \ / /                              
    \ v /  _   ______  ___  _  __ _   _ 
    > <  | | (  __  )/ __)| |/ /( \ / )
    / ^ \ | |  | || | > _) | / /  \ v / 
    /_/ \_\ \_) |_||_| \___)|__/    | |  
                                    | |  
                                    |_|  
    """
    print(artwork)

def get_network_interfaces():
# Mendapatkan daftar nama antarmuka jaringan
    interfaces = os.listdir('/sys/class/net/')
    return interfaces

def main():
    # Mendapatkan dan mencetak daftar nama antarmuka
    interface_names = get_network_interfaces()
    lhost = LocalHost("")
    cetak()
    print("Welcome to file synhcronization")
    print(f"Hostname : {lhost._hostname}")
    for name in interface_names:
        get_ip = lhost.getIp(name)
        print(f"interfaces {name} : {get_ip}")
    
    local_direktori = input("Masukkan direktori anda : ")
    lhost.localFolder = local_direktori
    
    
    
    

if __name__ == "__main__":
    main()
