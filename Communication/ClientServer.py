import socket
import threading
import time

def handle_client(client_socket):
    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            print(f"Received: {data.decode('utf-8')}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()

def start_server(address):
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((address, 9000))
        server_socket.listen(5)
        print(f"Server listening on port 9000")
        while True:
            client_socket, addr = server_socket.accept()
            print(f"Accepted connection from {addr}")
            client_handler = threading.Thread(target=handle_client, args=(client_socket,))
            client_handler.start()
    except Exception as e:
        print(f"Server error: {e}")
    finally:
        server_socket.close()

def start_client(address):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((address, 9000))

        for _ in range(5):  # Send the same message 5 times (you can adjust the number)
            message = "Hello server"
            client_socket.send(message.encode('utf-8'))
            time.sleep(1)  # Optional: Add a delay between messages

    except Exception as e:
        print(f"Error cannot connect to the server: {e}")
    finally:
        client_socket.close()

def run_server_and_client():
    server_thread = threading.Thread(target=start_server, args=('0.0.0.0',))
    server_thread.start()
    
    time.sleep(2)  # Allow server to start before the client
    client_thread = threading.Thread(target=start_client, args=('172.16.28.37',))
    client_thread.start()

if __name__ == "__main__":
    run_server_and_client()
