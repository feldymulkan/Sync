import sys
sys.path.append('/home/cipeng/Skripsi/Sync')
import socket
import threading
from Host.host import Host

host_info = Host.read_host_info("hostname.txt")
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 12345))  # Ganti port sesuai kebutuhan
    server_socket.listen(5)

    print("Server: Menunggu koneksi...")
    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Server: Terhubung ke {client_address}")

        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

def handle_client(client_socket):
    while True:
        message = client_socket.recv(1024).decode('utf-8')
        if not message:
            break
        print(f"Server: Pesan dari klien: {message}")

        response = input("Server: Masukkan balasan untuk klien: ")
        client_socket.sendall(response.encode('utf-8'))

        if response.lower() == 'exit':
            break

    print("Server: Menutup koneksi dengan klien")
    client_socket.close()

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 12345)  # Ganti dengan alamat IP atau nama host server
    client_socket.connect(server_address)

    while True:
        message = input("Client: Masukkan pesan untuk server (ketik 'exit' untuk keluar): ")
        client_socket.sendall(message.encode('utf-8'))
        if message.lower() == 'exit':
            break

        server_response = client_socket.recv(1024).decode('utf-8')
        print(f"Client: Balasan dari server: {server_response}")

    print("Client: Menutup koneksi")
    client_socket.close()

if __name__ == "__main__":
    server_thread = threading.Thread(target=start_server)
    server_thread.start()

    client_thread = threading.Thread(target=start_client)
    client_thread.start()