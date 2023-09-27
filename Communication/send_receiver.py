import socket

def send_directory(server_address, directory_path):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.connect(server_address)
        s.send(directory_path.encode('utf-8'))
    finally:
        s.close()

def receive_directory(server_address):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(server_address)
    s.listen(1)
    print("Menunggu koneksi dari client...")
    try:
        connection, client_address = s.accept()
        print("Terhubung dengan", client_address)
        directory_path = connection.recv(1024).decode('utf-8')
        print("Menerima direktori path:", directory_path)
    finally:
        connection.close()
        s.close()


