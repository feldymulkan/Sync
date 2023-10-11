import socket
import ssl

ssl_session = None  # Variabel global untuk menyimpan sesi SSL

def send_message(certfile, keyfile, server_address, server_hostname, directory):
    global ssl_session
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile, keyfile)

    with socket.create_connection(server_address) as client_socket:
        with context.wrap_socket(client_socket, server_hostname=server_hostname,
                                session=ssl_session, server_side=False) as secure_socket:
            if not ssl_session:
                # Jika tidak ada sesi SSL yang digunakan kembali, simpan sesi saat ini
                ssl_session = secure_socket.session

            message = directory
            secure_socket.sendall(message.encode())
            print("Message sent to server:", message)