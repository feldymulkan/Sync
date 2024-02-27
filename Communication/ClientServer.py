import socket
import time
import json
import threading

class ServerClientCommunication:
    def __init__(self):
        self.data_queue = []  # Menggunakan list sederhana sebagai mekanisme antar-thread
        self.start_time = time.time()  # Menyimpan waktu mulai server atau klien berjalan

    def handle_client(self, client_socket):
        try:
            while True:
                # Menerima data dari klien
                received_data = client_socket.recv(1024)
                if not received_data:
                    break
                decoded_data = json.loads(received_data.decode('utf-8'))
                self.data_queue.append(decoded_data)
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

            # Mengirim data JSON ke server
            json_message = json.dumps(message)  # Mengkonversi data ke JSON
            client_socket.send(json_message.encode('utf-8'))
        except Exception as e:
            print(f"Error cannot connect to the server: {e}")
        finally:
            client_socket.close()

    def get_received_data(self):
        if self.data_queue:
            return self.data_queue.pop(0)
        return None

    def get_received_data_realtime(self):
        while True:
            data = self.get_received_data()
            if data:
                return data
            time.sleep(1)
    
    def get_uptime(self):
        return time.time() - self.start_time


# Contoh penggunaan kelas ServerClientCommunication
# if __name__ == "__main__":
#     # Inisialisasi objek ServerClientCommunication
#     server_client = ServerClientCommunication()

#     # Memulai server pada alamat localhost
#     server_client.start_server('0.0.0.0')

#     # Tambahkan loop untuk membiarkan server berjalan terus menerima pesan
#     while True:
#         # Mengambil data yang diterima dari server
#         received_data = server_client.get_received_data()
#         if received_data:
#             print("Received data:", received_data.get('command'))

#         # Mengambil waktu up-time dari server
#         uptime = server_client.get_uptime()
#         print("Server uptime:", uptime)
