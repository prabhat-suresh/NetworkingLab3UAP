import socket


def start_client(server_host="127.0.0.1", server_port=65432, session_id="default"):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        while True:
            message = input("Enter message to send to server: ")
            if message.lower() == "exit":
                break

            # Create packet with session ID and message
            packet = f"{session_id}:{message}"

            # Send packet to the server
            client_socket.sendto(packet.encode("utf-8"), (server_host, server_port))

            # Receive response from the server
            response, _ = client_socket.recvfrom(1024)
            print(f"Received from server: {response.decode('utf-8')}")

    finally:
        client_socket.close()


if __name__ == "__main__":
    # Example usage: provide a unique session ID
    start_client(session_id="12345")
