import psutil
import time

def print_usage():
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_cores = psutil.cpu_count(logical=False)
    ram = psutil.virtual_memory()
    ram_percent = ram.percent
    ram_mb = ram.used / 1024 / 1024  # Memori RAM dalam MB
    print(f"\rCPU Usage: {cpu_percent:.2f}% ({cpu_cores} cores) | RAM Usage: {ram_percent:.2f}% ({ram_mb:.2f} MB)", end='', flush=True)

while True:
    print_usage()
    time.sleep(1)
