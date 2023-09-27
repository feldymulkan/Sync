import os
import time
from Host.localhost import localhost
import psutil
from file_sync import MyHandler, ssh_manager, observer

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

def getIp(interface_name):
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

def main():
    # Mendapatkan dan mencetak daftar nama antarmuka
    interface_names = get_network_interfaces()
    lhost = localhost("")
    cetak()
    print("Welcome to file synhcronization")
    print(f"Hostname : {lhost.getHostName()}")
    for name in interface_names:
        get_ip = getIp(name)
        print(f"interfaces {name} : {get_ip}")
    
    # local_direktori = input("Masukkan direktori anda : ")
    local_direktori = "/home/cipeng/server1"
    lhost.setLocalFolder(local_direktori)
    lhost_direktori = lhost.getLocalFolder()
    print (lhost_direktori)
    event_handler = MyHandler(lhost_direktori, ssh_manager)
    
    observer.schedule(event_handler, path=lhost_direktori, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    ssh_manager.close()

if __name__ == "__main__":
    main()
