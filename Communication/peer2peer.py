import socket
import threading
import time

def handle_connection(peer_socket, address):
    try:
        while True:
            # Pesan statis yang akan dikirim sebagai respons
            response = "This is a static response."
            
            # Kirim pesan statis
            peer_socket.send(response.encode('utf-8'))

            # Break dari loop untuk menutup koneksi
            break
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print(f"Connection with {address} closed.")

def start_peer(ip, port):
    try:
        peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peer_socket.bind((ip, port))
        peer_socket.listen(5)
        print(f"Peer listening on {ip}:{port}")

        while True:
            client_socket, addr = peer_socket.accept()
            print(f"Accepted connection from {addr}")
            client_handler = threading.Thread(target=handle_connection, args=(client_socket, addr))
            client_handler.start()
    except Exception as e:
        print(f"Peer error: {e}")
    finally:
        peer_socket.close()

def connect_to_peer(peer_ip, peer_port):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((peer_ip, peer_port))

        # Kirim pesan statis dari client ke peer lainnya
        user_input = "This is a static message."
        client_socket.send(user_input.encode('utf-8'))
        
    except Exception as e:
        print(f"Error connecting to peer: {e}")
    finally:
        client_socket.close()

if __name__ == "__main__":
    # Define the IP address and port for the local peer
    local_peer_info = {'ip': '0.0.0.0', 'port': 9002}

    # Start the local peer in a separate thread
    local_peer_thread = threading.Thread(target=start_peer, args=(local_peer_info['ip'], local_peer_info['port']))
    local_peer_thread.start()

    # Allow time for the local peer to start listening
    time.sleep(2)

    # Connect the local peer to another peer
    remote_peer_info = {'ip': '172.16.28.37', 'port': 9002}
    remote_peer_thread = threading.Thread(target=connect_to_peer, args=(remote_peer_info['ip'], remote_peer_info['port']))
    remote_peer_thread.start()

    # Join threads to wait for their completion
    local_peer_thread.join()
    remote_peer_thread.join()
