import socket
import threading
import time

# server_ready = threading.Event()
# client_ready = threading.Event()

def handle_client(client_socket):
    try:
        while True:
            global data 
            data = client_socket.recv(1024)
            if not data:
                break
            print(f"Received: {data.decode('utf-8')}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()

def getRecv():
    return data

def start_server(address):
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((address, 9000))
        server_socket.listen(5)
        # print(f"Server listening on port 9000")
        # server_ready.set()  # Indicate that the server is ready
        while True:
            client_socket, addr = server_socket.accept()
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
        # client_ready.set()  # Indicate that the client is ready
        client_socket.send(message.encode('utf-8'))
            # while True:
            #     # current_second = time.localtime().tm_sec
            #     # if current_second % 2 == 1:
            #     #     message = "Detik Angka ganjil"
                
            #     time.sleep(1)
    except Exception as e:
        print(f"Error cannot connect to the server: {e}")
        # time.sleep(5)  # Wait for 5 seconds before reconnecting
    finally:
        client_socket.close()

# def run_server_and_client():
#     server_thread = threading.Thread(target=start_server, args=('0.0.0.0',))
#     server_thread.start()
    
#     client_thread = threading.Thread(target=start_client, args=('172.16.28.37',))  # or use ('127.0.0.1',)
#     client_thread.start()

#     server_ready.wait()
#     client_ready.wait()

# if __name__ == "__main__":
#     run_server_and_client()
