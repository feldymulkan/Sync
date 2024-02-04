import socket
import threading
import time

def start_client(address):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((address, 9000))

        for _ in range(30):  # Send and receive messages 5 times (you can adjust the number)
            message = f"Hello server 2, from client vivapanturas at {time.time()}"
            
            # Send a message to the server
            client_socket.send(message.encode('utf-8'))
            
            # Receive the echoed message from the server
            data = client_socket.recv(1024)
            print(f"Received from server: {data.decode('utf-8')}")
            
            time.sleep(1)  # Optional: Add a delay between messages

    except Exception as e:
        print(f"Error cannot connect to the server: {e}")
    finally:
        client_socket.close()

def run_client():
    start_client('172.16.28.37')  # Replace with the server's IP address

if __name__ == "__main__":
    # Run the client in a separate thread
    client_thread = threading.Thread(target=run_client)
    client_thread.start()
