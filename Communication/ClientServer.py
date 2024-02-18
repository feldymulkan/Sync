import socket
import threading
import time

class ServerClientCommunication:
    def __init__(self):
        self.data = None
        self.lock = threading.Lock()

    def handle_client(self, client_socket):
        try:
            while True:
                new_data = client_socket.recv(1024)
                if not new_data:
                    break
                with self.lock:
                    self.data = new_data.decode('utf-8')
                # print(f"Received: {self.data}")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            client_socket.close()

    def start_server(self, address):
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind((address, 9000))
            server_socket.listen(5)
            while True:
                client_socket, addr = server_socket.accept()
                client_handler = threading.Thread(target=self.handle_client, args=(client_socket,))
                client_handler.start()
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            server_socket.close()

    def start_client(self, address, message):
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((address, 9000))
            client_socket.send(message.encode('utf-8'))
        except Exception as e:
            print(f"Error cannot connect to the server: {e}")
        finally:
            client_socket.close()

    def get_received_data(self):
        with self.lock:
            return self.data

# if __name__ == "__main__":
#     communication = ServerClientCommunication()

#     # Start server in a separate thread
#     server_thread = threading.Thread(target=communication.start_server, args=('0.0.0.0',))
#     server_thread.start()

#     # Start client
#     communication.start_client('172.16.28.37', 'Hello from client!')

#     # Wait for the server thread to finish
#     server_thread.join()

#     # Now, you can continuously monitor the received data
#     while True:
#         received_data = communication.get_received_data()
#         if received_data:
#             print("Received data:",
