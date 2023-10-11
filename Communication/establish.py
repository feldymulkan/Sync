import socket
import ssl

ssl_session = None  # Variabel global untuk menyimpan sesi SSL

def start_ssl_server(certfile, keyfile, address, port):
    global ssl_session

    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile=certfile, keyfile=keyfile)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((address, port))
        server_socket.listen(1)
        print(f"Server listening on {address}:{port}")

        while True:
            with context.wrap_socket(server_socket, server_side=True, session=ssl_session) as secure_socket:
                connection, client_address = secure_socket.accept()
                print("Connected to", client_address)
                data = connection.recv(1024)
                print("Received data:", data.decode())

                # Simpan sesi SSL untuk session resumption
                ssl_session = secure_socket.session

                connection.close()
