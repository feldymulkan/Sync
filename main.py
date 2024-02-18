import time
from Host.localhost import localhost
from file_sync import MyHandler, ssh_manager, observer
from getfile import GetFileManager
from Communication.ClientServer import ServerClientCommunication
from concurrent.futures import ThreadPoolExecutor
import threading
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

def start_watchdog(folderlocal, ssh_manager, ip_target, ip_local):
    comm = ServerClientCommunication()
    handler = MyHandler(folderlocal, ssh_manager)
    observer.schedule(handler, path=folderlocal, recursive=True)
    status = 'START'

    try:
        while status == 'START':  # Ubah menjadi loop while
            with ThreadPoolExecutor(max_workers=3) as executor:
                executor.submit(observer.start)
                executor.submit(comm.start_server, ip_local)

                # Check for total_synced_files and wait for it to exceed 3
                while True:
                    total_synced_files = handler.get_file_synced()
                    print(f"Total Modified Files: {total_synced_files}", end='\r')
                    time.sleep(1)
                    if total_synced_files > 3:
                        observer.stop()
                        total_synced_files = 0
                        status = 'STOP'
                        comm.start_client(ip_target, 'START')
                        status = comm.get_received_data()
                        print("Received status:", status)
                        break
                
    except KeyboardInterrupt:
        observer.stop()
    finally:
        observer.join()
        observer.stop()




def get_total_file(folderlocal, ssh_manager):
    handler = MyHandler(folderlocal, ssh_manager)
    return handler.get_file_synced()

def main():
    comm = ServerClientCommunication()
    lhost = localhost.read_localhost_info("lhost.txt")
    local_ip = lhost.getIP(lhost.getInterface())
    local_port = int(lhost.getPort())
    local_dir = str(lhost.getLocalFolder())
    total_file = get_total_file(local_dir, ssh_manager)
    # status = comm.get_received_data()
    ip_target = ssh_manager.hostname
    signal.signal(signal.SIGINT, cetak_stopped_signal)
    cetak()
    print("-- Welcome to file synchronization -- ")
    print(f"[#] Hostname: {lhost.getHostName()}")
    print(f"[#] Active IP: {lhost.getActiveInterfaceIP()}")

    start_watchdog(local_dir, ssh_manager, ip_target, local_ip)

if __name__ == "__main__":
    main()
