import socket
import threading

def handle_client(client_socket):
    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            print(f"Received from client: {data.decode('utf-8')}")
            
            # Echo the received data back to the client
            client_socket.send(data)
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

def run_server():
    start_server('0.0.0.0')

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_server)
    server_thread.start()
