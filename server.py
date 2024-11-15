import socket

# Define the IP address and port for the server
server_ip = "127.0.0.1"  # Localhost
server_port = 12345

# Create a UDP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the IP address and port
server_socket.bind((server_ip, server_port))

print(f"UDP server is up and listening on {server_ip}:{server_port}")

while True:
    # Wait for a message from a client
    data, client_address = server_socket.recvfrom(1024)  # Buffer size of 1024 bytes
    print(f"Received message: {data.decode()} from {client_address}")

    # Send a response back to the client
    response = f"Server received \"{data.decode()}\""
    server_socket.sendto(response.encode(), client_address)
