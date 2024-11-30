import argparse
import math
import sys
import socket
import select
import time

from utils import compile_packet, get_fields, INIT_PACKET

IP = ""
PORT = 0
TIMEOUT = 2
BUFFER_SIZE = 2048

ACK_PACKET = None
MAX_RETRIES = 3
start_time = 0.0

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
        # fd.setblocking(False)

    except socket.error as e:
        print("Client - Error creating socket: {}".format(e))
        sys.exit()

    return fd

def handle_send(fd, encoded_message):
    global start_time
    retries = 0
    seq_num = INIT_PACKET
    received_payload_size = 0

    # TODO Billy: Re-calculate payload size to send (must exclude the first 3 lengths)
    num_segments = math.ceil(len(encoded_message) / 2048)
    # if remainder(num_segments, 2048) != 0:
    #     num_segments += 1

    segments = [
        encoded_message[i * BUFFER_SIZE:(i + 1) * BUFFER_SIZE] for i in range(num_segments)
    ]
    
    decoded_segments = [segment.decode("utf-8") for segment in segments]
    print("Number of segments:", num_segments)
    print("Segments:", decoded_segments)

    for segment in decoded_segments:
        packet_to_send = compile_packet(seq_num, received_payload_size, segment)

        # ready_sockets, _, _  = select.select([fd], [], [])

        # Send packet
        # if fd in write_list:
        send_packet(fd, packet_to_send)

        while retries < MAX_RETRIES:
            print("Client - Waiting for acknowledgement...")
            # Receive ack
            if fd:
                print("Client - Receiving ACK")
                receive_ack(fd)

                # client's seq_num == server's ack_num
                _, _, seq_num, payload = get_fields(ACK_PACKET)
                received_payload_size = len(payload)
                break

            # Re-transmit packet
            if time.time() - start_time < TIMEOUT:
                print("Client - Received no acknowledgements, timed out.")
                retries += 1
                print(f"Client - Resending packet. Retry #{retries}")
                send_packet(fd, packet_to_send)

            # if fd in error_list:
            #     print("Client - Socket error occurred. Try again.")
            #     sys.exit()

        if retries >= MAX_RETRIES:
            print("Client - Maximum retries exceeded. Try again.")
            sys.exit()

def start_transmission(fd):
    while True:
        message = input("Message to send to the server (type 'exit' to quit):\n")
        if message.lower() == "exit":
            print("Client - Exiting...")
            return

        handle_send(fd, message.encode())

def send_packet(fd, encoded_packet):
    global start_time
    try:
        print(f"Client - Sending packet {encoded_packet}. Starting timer...")
        fd.sendto(encoded_packet, (IP, PORT))
        start_time = time.time()
    except socket.error as e:
        print(f"Client - Error sending packet: {format(e)}. Try again.")

def is_duplicated_packet(last_packet):
    global ACK_PACKET
    return last_packet == ACK_PACKET

def receive_ack(fd):
    global ACK_PACKET
    try:
        last_packet = None
        # Handling duplicated ACK
        while True:
            ACK_PACKET, server_address = fd.recvfrom(BUFFER_SIZE)

            if not is_duplicated_packet(last_packet):
                print("Client - New acknowledgement.")
                break
            else:
                print("Client - Duplicated acknowledgement.")

            last_packet = ACK_PACKET

    except socket.error as e:
        print(f"Client - Error receiving ACK: {format(e)}. Try again.")
        sys.exit()

    print(f"Response from Server: {ACK_PACKET.decode()}")

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
