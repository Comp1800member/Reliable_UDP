import socket
import time
from utils import compile_packet, get_fields, INIT_PACKET

# Define the IP address and port for the server
server_ip = "127.0.0.1"  # Localhost
server_port = 12345

# Create a UDP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the IP address and port
server_socket.bind((server_ip, server_port))

print(f"UDP server is up and listening on {server_ip}:{server_port}")

set_delay = False
seq_num = INIT_PACKET

while True:
    # Wait for a message from a client
    data, client_address = server_socket.recvfrom(1024)  # Buffer size of 1024 bytes
    print(f"Received message: {data.decode()} from {client_address}")

    # Test: delay scenario
    if not set_delay:
        print("Delaying...")
        time.sleep(5)
        set_delay = True

    _, received_seq_num, received_ack_num, received_payload = get_fields(data)
    seq_num = received_ack_num
    print(f"Payload from Client: {received_payload}")
    packet_to_send = compile_packet(seq_num, received_seq_num, len(received_payload), "")
    server_socket.sendto(packet_to_send, client_address)
    print(f"Sent message \"{packet_to_send}\" to {client_address}")
