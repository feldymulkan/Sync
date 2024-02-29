import time
from Host.localhost import localhost
from file_sync import MyHandler, ssh_manager, observer
from Communication.ClientServer import ServerClientCommunication
import threading
import ctypes
import signal
from getfile import GetFileManager


status = True

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
def download_files_periodically(downFile):
    while True:
        downFile.download_files_from_server()
        time.sleep(3600)

def start_watchdog(folderlocal, target):
    comm = ServerClientCommunication()
    handler = MyHandler(folderlocal, ssh_manager)
    observer.schedule(handler, path=folderlocal, recursive=True)
    status = True
    server_thread = threading.Thread(target=comm.start_server, args=('0.0.0.0',))
    # isOnlineThread = threading.Thread(target=ssh_manager.is_host_online)
    
    try:
        server_thread.start() 
        observer.start()
        if ssh_manager.is_host_online():
            comm.start_client(target,{'command': 'START'})
        else:
            pass
        while status:
            total_synced_files = handler.get_file_synced()
            print(f"Total Modified: {total_synced_files}", end='\r')
            time.sleep(1)
            
            message = comm.get_received_data()
            if ssh_manager.is_host_online():
                if total_synced_files >= 5:
                    print("Kondisi1 :" + str(ssh_manager.is_host_online()))
                    handler.setActive(False)
                    comm.start_client(target, {'command': 'START'})
                    handler.resetTotalFile()
                    continue
                elif message:
                    print("Kondisi2 :" + str(ssh_manager.is_host_online()))
                    command = message['command']
                    if command == 'START':
                        handler.setActive(True)
                        comm.start_client(target, {'command': 'STOP'})
                        continue
                    elif command == 'STOP':
                        handler.setActive(False)
                        comm.start_client(target, {'command': 'START'})
                        handler.resetTotalFile()
                        continue
            elif not ssh_manager.is_host_online():
                handler.setActive(False)
                continue
                
    except Exception as e:
        print(f"Error: {str(e)}")
    except KeyboardInterrupt:
        observer.stop()
        server_thread.join()
    finally:
        server_thread.join()
        observer.join()
        observer.stop()



def stop_watchdog():
    observer.stop()
    observer.join()
    observer.unschedule_all()
    
def main():
    comm = ServerClientCommunication()
    lhost = localhost.read_localhost_info("lhost.txt")
    local_ip = lhost.getIP(lhost.getInterface())
    local_port = int(lhost.getPort())
    local_dir = str(lhost.getLocalFolder())
    downFile = GetFileManager(ssh_manager, local_dir)
    ip_target = ssh_manager.hostname
    signal.signal(signal.SIGINT, cetak_stopped_signal)
    cetak()
    print("-- Welcome to file synchronization -- ")
    print(f"[#] Hostname: {lhost.getHostName()}")
    print(f"[#] Active IP: {lhost.getActiveInterfaceIP()}")
    
    download_thread = threading.Thread(target=download_files_periodically, args=(downFile,))
    download_thread.start()
    watchdogThread = threading.Thread(target=start_watchdog, args=(local_dir,ip_target))
    watchdogThread.start()

    download_thread.join()
    watchdogThread.join()

if __name__ == "__main__":
    main()
