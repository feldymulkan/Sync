import zmq
import threading

def handle_client(socket):
    while True:
        message = socket[0].decode('utf-8')
        print(f"Received from client: {message}")

        # Process the received data (add your logic here)

        # Send a response back to the client
        response = f"Server received: {message}"
        socket[0].send_string(response)

def start_server():
    context = zmq.Context()
    server_socket = context.socket(zmq.REP)
    server_socket.bind("tcp://*:5555")

    print("Server listening on port 5555")

    while True:
        client_socket = server_socket.recv_multipart()
        print("Client connected!")

        # Notify the server about the new client
        response = "Hello, client! You are connected to the server."
        client_socket[0].send_string(response)

        # Start a new thread to handle the client
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()

if __name__ == "__main__":
    start_server()
