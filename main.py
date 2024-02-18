import time
from Host.localhost import localhost
from file_sync import MyHandler, ssh_manager, observer
from getfile import GetFileManager
import threading
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
    
    
    try:
        observer.start()
        while True:
            total_synced_files = handler.get_file_synced()
            print(f"Total Modified Files: {total_synced_files}", end='\r')
            time.sleep(1)
            if total_synced_files > 3:
                observer.stop()
                break
        start_client(ip_target, "STOP")
    except KeyboardInterrupt:
        observer.stop()
    finally:
        observer.join()
        observer.stop()

def get_total_file(folderlocal, ssh_manager):
    handler = MyHandler(folderlocal, ssh_manager)
    return handler.get_file_synced()

# def run_prog(folder_path, ssh_manager):
#     with ThreadPoolExecutor() as executor:
#         executor.submit(start_watchdog, folder_path, ssh_manager)
        
def main():
    #localhost
    lhost = localhost.read_localhost_info("lhost.txt")
    local_ip = lhost.getIP(lhost.getInterface())
    local_port = int(lhost.getPort())
    local_dir = str(lhost.getLocalFolder())
    total_file = get_total_file(local_dir, ssh_manager)
    # #Host SSH
    ip_target = ssh_manager.hostname
    signal.signal(signal.SIGINT, cetak_stopped_signal)
    cetak()
    print("-- Welcome to file synchronization -- ")
    print(f"[#] Hostname: {lhost.getHostName()}")
    print(f"[#] Active IP: {lhost.getActiveInterfaceIP()}")
    # start_server(local_ip)
    # start_watchdog(local_dir, ssh_manager, ip_target)
    thread1 = threading.Thread(target=start_server, args=(local_ip,))
    
    # Membuat thread untuk menjalankan fungsi start_watchdog
    thread2 = threading.Thread(target=start_watchdog, args=(local_dir, ssh_manager, ip_target))

    # Memulai kedua thread secara bersamaan
    thread1.start()
    thread2.start()

    # Menunggu kedua thread selesai
    thread1.join()
    thread2.join()
    # active_interface_ip = lhost.getActiveInterfaceIP()
    # getFile = GetFileManager(ssh_manager, local_dir)
    # getFile.download_files_from_server()
    # start_watchdog
    # start_client(ip_target, 'local_message')
    
    # Mendapatkan informasi jumlah file yang sudah di-sinkronisasi
    
    
    
    
if __name__ == "__main__":
    main()