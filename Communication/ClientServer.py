import socket
import threading
import time

def handle_client(client_socket):
    # This function handles communication with a specific client
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

def start_client(address, message):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((address, 9000))
        client_socket.send(message.encode('utf-8'))

    except Exception as e:
        print(f"Error cannot connect to the server: {e}")
    finally:
        client_socket.close()

# def run_server_and_client():
#     # Start the server in a new thread
#     server_thread = threading.Thread(target=start_server, args=('0.0.0.0', 9999))
#     server_thread.start()

#     # Give some time for the server to start before starting the client
#     # You may need to adjust this based on the actual server startup time
#     time.sleep(2)

#     # Start the client in another thread
#     client_thread = threading.Thread(target=start_client, args=('127.0.0.1', 9999, 'Hello server!'))
#     client_thread.start()

# if __name__ == "__main__":
#     run_server_and_client()
    
