import time
from Host.localhost import localhost
from file_sync import MyHandler, ssh_manager, observer
from getfile import GetFileManager
from Communication.ClientServer import start_server, start_client
from concurrent.futures import ThreadPoolExecutor

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

def start_watchdog(folderlocal, ssh_manager, ip_target):
    handler = MyHandler(folderlocal, ssh_manager)
    observer.schedule(handler, path=folderlocal, recursive=True)
    
    observer_running = True
    try:
        observer.start()
        while observer_running:
            # Mendapatkan jumlah file yang dimodifikasi secara langsung dari handler
            total_synced_files = handler.get_file_synced()
            print(f"Total Modified Files: {total_synced_files}", end='\r')
            time.sleep(1)
            if total_synced_files >= 10:
                observer_running = False 
                observer.stop()
                observer.join()
                # observer_running = False 
                break
            
            
        start_client(ip_target, 'Start')
    except KeyboardInterrupt:
        observer.stop()
    finally:
        observer.join()
        observer.stop()

def get_total_file(folderlocal, ssh_manager):
    handler = MyHandler(folderlocal, ssh_manager)
    return handler.get_file_synced()

def run_prog(folder_path, ssh_manager, target):
    with ThreadPoolExecutor() as executor:
        executor.submit(start_watchdog, folder_path, ssh_manager, target)
        
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
    run_prog(str(lhost.getLocalFolder()), ssh_manager, ip_target)
    # Mendapatkan informasi jumlah file yang sudah di-sinkronisasi
    
    
    
if __name__ == "__main__":
    main()