import socket
import ssl

def connect_to_ssl_server(certfile, keyfile, server_address, server_hostname, directory):
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=certfile)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    context.load_cert_chain(certfile=certfile, keyfile=keyfile, password="server")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        with context.wrap_socket(client_socket, server_side=False, server_hostname=server_hostname) as secure_socket:
            secure_socket.connect(server_address)
            message = directory
            secure_socket.sendall(message.encode())
            print("Message sent to server:", message)

# Contoh penggunaan fungsi connect_to_ssl_server
# certfile = "server-cert.pem"
# keyfile = "server-key.pem"
# server_address = ("192.168.20.2", 5000)  # Ganti dengan alamat IP atau nama host server dan port yang sesuai
# server_hostname = "server2jarkom"
# message = "/home/cipeng/server1"

# connect_to_ssl_server(certfile, keyfile, server_address, server_hostname, message)