import socket
import ssl

def start_ssl_server(certfile, keyfile, address, port):
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile=certfile, keyfile=keyfile)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((address, port))
        server_socket.listen(1)
        print(f"Server listening on {address}:{port}")

        with context.wrap_socket(server_socket, server_side=True) as secure_socket:
            connection, client_address = secure_socket.accept()
            print("Connected to", client_address)
            data = connection.recv(1024)
            print("Received data:", data.decode())
            connection.close()

# Panggil fungsi untuk memulai server SSL
certfile = 'server-cert.pem'
keyfile = 'server-key.pem'
server_address = ('192.168.1.38', 1024)
start_ssl_server(certfile, keyfile, *server_address)
