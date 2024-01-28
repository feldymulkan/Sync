import zmq

def start_client():
    context = zmq.Context()
    client_socket = context.socket(zmq.REQ)
    client_socket.connect("tcp://127.0.0.1:5555")

    while True:
        message = input("Enter message (type 'exit' to quit): ")
        if message.lower() == 'exit':
            break
        client_socket.send_multipart([message.encode('utf-8')])

        # Receive and print the response from the server
        response = client_socket.recv_string()
        print(f"Server response: {response}")

    client_socket.close()

if __name__ == "__main__":
    start_client()
