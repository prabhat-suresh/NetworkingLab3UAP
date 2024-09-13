import socket
import threading

# Dictionary to keep track of active sessions
sessions = {}
sessions_lock = threading.Lock()


def handle_client(data, client_address, session_id):
    # Process the received data
    print(f"Session {session_id} received from {client_address}: {data}")
    response = f"Session {session_id} received: {data}"

    # Send a response back to the client
    return response


def start_server(host="127.0.0.1", port=65432):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, port))

    print(f"Server started on {host}:{port}")

    while True:
        data, client_address = server_socket.recvfrom(1024)
        data = data.decode("utf-8")

        # Extract session ID from the packet
        session_id, message = data.split(":", 1)

        # Check if the session already exists
        with sessions_lock:
            if session_id in sessions:
                # If session exists, use the existing session
                response = handle_client(message, client_address, session_id)
            else:
                # If session does not exist, create a new one
                response = handle_client(message, client_address, session_id)
                sessions[session_id] = client_address

        # Send the response back to the client
        server_socket.sendto(response.encode("utf-8"), client_address)


if __name__ == "__main__":
    start_server()
