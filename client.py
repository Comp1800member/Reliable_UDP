import argparse
import math
import sys
import socket

from utils import compile_packet, get_fields, INIT_PACKET, PAYLOAD_SIZE

IP = ""
PORT = 0
TIMEOUT = 2.0
BUFFER_SIZE = 4096

ACK_PACKET = None
MAX_RETRIES = 3

# TODO - Billy: Make client handle packet max size and segmentation

def parse_arguments():
    global IP, PORT, TIMEOUT
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--target-ip", type=str, required=True, help="IP address of the server")
    parser.add_argument("-p", "--target-port", type=int, required=True, help="Port number of the server")
    parser.add_argument("-t", "--timeout", type=int, help="Timeout (in seconds) for waiting for acknowledgements")

    try:
        args = parser.parse_args()

    except SystemExit as e:
        parser.print_help()
        sys.exit()

    IP = args.target_ip
    PORT = args.target_port

    if args.timeout is not None:
        TIMEOUT = args.timeout

def create_socket():
    print("Client - Creating socket...")
    try:
        fd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    except socket.error as e:
        print("Client - Error creating socket: {}".format(e))
        sys.exit()

    return fd

def segment_payload(payload):
    num_segments = math.ceil(len(payload) / PAYLOAD_SIZE)
    print("Number of segments:", num_segments)

    segments = [
        payload[i * PAYLOAD_SIZE:(i + 1) * PAYLOAD_SIZE] for i in range(num_segments)
    ]

    return [segment.decode("utf-8") for segment in segments]

def start_transmission(fd):
    while True:
        message = input("Message to send to the server (type 'exit' or ctrl+D to quit):\n")
        if message.lower() == "exit":
            print("Client - Exiting...")
            return

        handle_send(fd, message.encode())

def send_packet(fd, encoded_packet):
    try:
        print(f"Client - Sending packet {encoded_packet}. Starting timer...")
        fd.sendto(encoded_packet, (IP, PORT))
        fd.settimeout(TIMEOUT)
    except socket.error as e:
        print(f"Client - Error sending packet: {format(e)}. Try again.")

def is_duplicated_packet(received_packet):
    global ACK_PACKET
    return ACK_PACKET == received_packet

def receive_ack(fd):
    global ACK_PACKET
    received_packet = None
    try:
        while True:
            print("Client - Waiting for acknowledgement...")
            received_packet, server_address = fd.recvfrom(BUFFER_SIZE)

            # Handling duplicated ACK
            if not is_duplicated_packet(received_packet):
                print("Client - New acknowledgement.")
                ACK_PACKET = received_packet
                break

            print("Client - Duplicated acknowledgement.")
            print(f"Client - Received packet {received_packet}")

    except socket.timeout as e:
        print("Client - Received no acknowledgements, timed out.")
        ACK_PACKET = received_packet
        return False

    except socket.error as e:
        print(f"Client - Error receiving ACK: {format(e)}. Try again.")
        sys.exit()

    return True

def handle_send(fd, encoded_message):
    retries = 0
    seq_num = INIT_PACKET
    received_seq_num = INIT_PACKET
    received_payload_size = 0

    decoded_segments = segment_payload(encoded_message)
    print("Segments to send:", decoded_segments)

    for segment in decoded_segments:
        packet_to_send = compile_packet(seq_num, received_seq_num, received_payload_size, segment)

        # Send packet
        send_packet(fd, packet_to_send)

        # Receive ack
        while retries < MAX_RETRIES:
            # Re-transmit packet
            if not receive_ack(fd):
                retries += 1
                print(f"Client - Resending packet. Retry #{retries}")
                send_packet(fd, packet_to_send)
            else:
                break

        if retries >= MAX_RETRIES:
            print("Client - Maximum retries exceeded. Try again.")
            sys.exit()

        _, received_seq_num, received_ack_num, payload = get_fields(ACK_PACKET)
        received_payload_size = len(payload)
        seq_num = received_ack_num

if __name__ == "__main__":
    parse_arguments()
    client_socket = create_socket()
    start_transmission(client_socket)
    print("Client - Closing socket")
    client_socket.close()

    # Sample: How to use utils
    # message = "Hello World"
    # Compiling a packet
    # packet = compile_packet(1, 1, 0, message)
    # print(f"Packet: {packet}")

    # Getting fields from a packet
    # BUFFER_SIZE, seq_num, ack_num, payload = get_fields(packet)
    # print(f"Packet size: {BUFFER_SIZE}")
    # print(f"Sequence number: {seq_num}")
    # print(f"Ack number: {ack_num}")
    # print(f"Payload: {payload}")
