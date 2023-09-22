import socket
import ssl

# Informasi server tujuan
server_address = ('192.168.1.13', 12345)  # Ganti dengan alamat dan port tujuan
directory_path = '/path/to/directory'  # Ganti dengan direktori yang ingin Anda kirimkan

# Inisialisasi koneksi socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Inisialisasi koneksi SSL
context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
ssl_sock = context.wrap_socket(s, server_hostname='192.168.1.13')

try:
    # Terhubung ke server
    ssl_sock.connect(server_address)

    # Kirim informasi direktori path ke server
    ssl_sock.send(directory_path.encode('utf-8'))

finally:
    # Tutup koneksi SSL
    ssl_sock.close()
