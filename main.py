import time
from Host.localhost import localhost
from file_sync import MyHandler, ssh_manager, observer
from Communication.ClientServer import ServerClientCommunication
import threading
import ctypes
import signal
from getfile import GetFileManager
import argparse


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
def download_files_periodically(downFile, period):
    while True:
        downFile.download_files_from_server()
        time.sleep(period)

 
def start_failover(folderlocal, workers):
    handler = MyHandler(folderlocal, ssh_manager, workers)
    observer.schedule(handler, path=folderlocal, recursive=True)

    try:
        observer.start()

        while True:
            total_synced_files = handler.get_file_synced()
            print(f"Total Modified: {total_synced_files}", end='\r')
            time.sleep(1)
            if ssh_manager.is_host_online():
                handler.setActive(True)
                continue
            else:
                handler.setActive(False)    
                ssh_manager.reconnect()
                print("hello")
                continue
                    
               
    except Exception as e:
        print(f"Error: {str(e)}")
    except KeyboardInterrupt:
        observer.stop()
    finally:
        observer.join()
        observer.stop()

        
def start_watchdog(folderlocal, target, worker, limit):
    comm = ServerClientCommunication()
    handler = MyHandler(folderlocal, ssh_manager, worker)
    observer.schedule(handler, path=folderlocal, recursive=True)
    status = True
    server_thread = threading.Thread(target=comm.start_server, args=('0.0.0.0',))
    # isOnlineThread = threading.Thread(target=ssh_manager.is_host_online)
    handler.setActive(True)
    try:
        server_thread.start() 
        observer.start()
        
        if ssh_manager.is_host_online():
            handler.setActive(False)
            comm.start_client(target,{'command': 'START'})
        else:
            handler.setActive(True)
        while status:
            total_synced_files = handler.get_file_synced()
            print(f"Total Modified: {total_synced_files}", end='\r')
            time.sleep(1)
            
            message = comm.get_received_data()
            if ssh_manager.is_host_online():
                if total_synced_files >= limit+1:
                    # print("Kondisi1 :" + str(ssh_manager.is_host_online()))
                    handler.resetTotalFile()
                    handler.setActive(False)
                    comm.start_client(target, {'command': 'START'})
                    continue
                elif message:
                    # print("Kondisi2 :" + str(ssh_manager.is_host_online()))
                    command = message['command']
                    if command == 'START':
                        handler.setActive(True)
                        comm.start_client(target, {'command': 'STOP'})
                        continue
                    elif command == 'STOP':
                        handler.setActive(False)
                        comm.start_client(target, {'command': 'START'})
                        # handler.resetTotalFile()
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
    lhost = localhost.read_localhost_info("lhost.txt")
    local_dir = str(lhost.getLocalFolder())
    
    ip_target = ssh_manager.hostname
    signal.signal(signal.SIGINT, cetak_stopped_signal)
    cetak()
    print("-- Welcome to file synchronization -- ")
    print(f"[#] Hostname: {lhost.getHostName()}")
    print(f"[#] Active IP: {lhost.getActiveInterfaceIP()}")
    parser = argparse.ArgumentParser(description="--File Sync SFTP--")
    parser.add_argument("--mode", type=str, default='fo', help="mode (2w/fo) default mode fo ,Example: main.py fo/2w")
    parser.add_argument("--threads", type=int, default=1, help="Number of threads to use (default: 1)")
    parser.add_argument("--limit", type=int, default=10, help="File sync cycle limit (default 10) only 2w mode")
    parser.add_argument("--period", type=int, default=3600, help="Time period File Downloads (in Second) only 2w mode")
    args = parser.parse_args()
    downFile = GetFileManager(ssh_manager, local_dir,args.threads)
    
    if not args.mode:
        parser.error("mode is required.")
    elif args.mode == "2w":
        download_thread = threading.Thread(target=download_files_periodically, args=(downFile,args.period))
        download_thread.start()
        watchdogThread = threading.Thread(target=start_watchdog, args=(local_dir,ip_target,args.threads, args.limit))
        watchdogThread.start()

        download_thread.join()
        watchdogThread.join()
    elif args.mode == "fo":

        failThread = threading.Thread(target=start_failover, args=(local_dir,args.threads))
        failThread.start()
        
        failThread.join()

if __name__ == "__main__":
    main()
