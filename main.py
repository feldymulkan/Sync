import time
from Host.localhost import localhost
from file_sync import MyHandler, ssh_manager, observer
from Communication.ClientServer import ServerClientCommunication
import threading
import ctypes
import signal


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

def stop_thread(thread):
    """Stop a thread from running."""
    exc = ctypes.py_object(SystemExit)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        ctypes.c_long(thread.ident), exc)
    if res == 0:
        raise ValueError("nonexistent thread id")
    elif res > 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(thread.ident, None)

def restart_thread(thread, target, args):
    """Restart a stopped thread with new target and args."""
    stop_thread(thread)
    time.sleep(0.1)  # Allow some time for the thread to stop
    new_thread = threading.Thread(target=target, args=args)
    new_thread.start()
    return new_thread

def start_watchdog(folderlocal, target):
    comm = ServerClientCommunication()
    handler = MyHandler(folderlocal, ssh_manager)
    observer.schedule(handler, path=folderlocal, recursive=True)
    status = True
    server_thread = threading.Thread(target=comm.start_server, args=('0.0.0.0',))
    
    try:
        server_thread.start() 
        observer.start()
        while status:


            total_synced_files = handler.get_file_synced()
            print(f"Total Modified: {total_synced_files}", end='\r')
            time.sleep(1)
            message = comm.get_received_data()
            if message:
                command = message['command']
                if total_synced_files >= 5 or command == 'STOP':
                    handler.setActive(False)
                    comm.start_client(target, {'command': 'START'})
                    handler.resetTotalFile()
                    continue
                elif command == 'START':
                    handler.setActive(True)
                    comm.start_client(target, {'command': 'STOP'})
                    continue
        
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

    ip_target = ssh_manager.hostname
    signal.signal(signal.SIGINT, cetak_stopped_signal)
    cetak()
    print("-- Welcome to file synchronization -- ")
    print(f"[#] Hostname: {lhost.getHostName()}")
    print(f"[#] Active IP: {lhost.getActiveInterfaceIP()}")

    

    # watchdog_thread = threading.Thread(target=start_watchdog, args=(local_dir, ip_target))

    # server_thread.start()
    # watchdog_thread.start()
    # # stop_watchdog(watchdog_thread)
    # # restart_thread(watchdog_thread)
    start_watchdog(local_dir, ip_target)
    # server_thread.join()
    # watchdog_thread.join()


if __name__ == "__main__":
    main()
