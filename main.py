import time
from Host.localhost import localhost
from file_sync import MyHandler, ssh_manager, run_prog
from getfile import GetFileManager
from Communication.ClientServer import start_server, start_client

import signal

def cetak_stopped_signal(signum, frame):
    print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n[-] Stopped")
    exit()
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

def main():
    #localhost
    lhost = localhost.read_localhost_info("lhost.txt")
    local_ip = lhost.getIP(lhost.getInterface())
    local_port = int(lhost.getPort())
    
    #Host SSH
    ip_target = ssh_manager.hostname
    signal.signal(signal.SIGINT, cetak_stopped_signal)
    cetak()
    print("-- Welcome to file synchronization -- ")
    print(f"[#] Hostname: {lhost.getHostName()}")
    print(f"[#] Active IP: {lhost.getActiveInterfaceIP()}")

    
    # local_message= "Hello"
    # start_client(ip_target, local_message)
    # time.sleep(2)
    # start_server(local_ip)

    
    
    active_interface_ip = lhost.getActiveInterfaceIP()
    getFile = GetFileManager(ssh_manager, lhost.getLocalFolder())
    getFile.download_files_from_server()
    run_prog(str(lhost.getLocalFolder()), ssh_manager)
    
if __name__ == "__main__":
    main()