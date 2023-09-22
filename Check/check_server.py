import subprocess
import time

def check_server_availability(hostname):
    while True:
        try:
            result = subprocess.run(['ping', '-c', '1', '-W', '1', hostname], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            if "1 packets transmitted, 1 received" in result.stdout:
                print(f"{hostname} is online")
            else:
                print(f"{hostname} is offline")
        except subprocess.CalledProcessError:
            print(f"Unable to connect to {hostname}")
        time.sleep(10)

