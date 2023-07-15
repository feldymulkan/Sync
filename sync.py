import os
import time
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Informasi Server 1
server1_directory = "/var/www/html"
server1_ip = "192.168.125.136"

# Informasi Server 2
server2_directory = "/var/www/html"
server2_ip = "192.168.125.137"

# Informasi Endpoint untuk Sinkronisasi File
server1_sync_endpoint = f"http://{server1_ip}/sync"
server2_sync_endpoint = f"http://{server2_ip}/sync"

class FileSyncHandler(FileSystemEventHandler):
    def __init__(self, server_directory, sync_endpoint):
        self.server_directory = server_directory
        self.sync_endpoint = sync_endpoint

    def on_created(self, event):
        if not event.is_directory:
            file_path = event.src_path
            self.sync_file(file_path)

    def sync_file(self, file_path):
        try:
            with open(file_path, 'rb') as file:
                files = {'file': file}
                response = requests.post(self.sync_endpoint, files=files)
                if response.status_code == 200:
                    print(f"File synced: {file_path}")
                else:
                    print(f"Error syncing file: {file_path}")
        except requests.exceptions.RequestException as e:
            print(f"Error syncing file: {e}")

def start_file_sync(server_directory, sync_endpoint):
    event_handler = FileSyncHandler(server_directory, sync_endpoint)
    observer = Observer()
    observer.schedule(event_handler, server_directory, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def main():
    # Memulai sinkronisasi file dari Server 1 ke Server 2
    start_file_sync(server1_directory, server2_sync_endpoint)

    # Memulai sinkronisasi file dari Server 2 ke Server 1
    start_file_sync(server2_directory, server1_sync_endpoint)

if __name__ == "__main__":
    main()
