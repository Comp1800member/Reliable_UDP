import argparse
import math
import sys
import socket
import select
from math import remainder
from socket import send_fds

import utils

IP = ""
PORT = 0
TIMEOUT = 2
BUFFER_SIZE = 1009  # in bytes, excluding 15 bytes = packet_size (4 bytes) + sequence_number (4 bytes) + acknowledgement_number (4 bytes) + 3 * ";" (1 byte)

RECEIVED_PACKET = ""

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

def handle_send(fd, encoded_message):
    num_segments = math.ceil(len(encoded_message) / BUFFER_SIZE)
    # if remainder(num_segments, BUFFER_SIZE) != 0:
    #     num_segments += 1

    segments = [
        encoded_message[i * BUFFER_SIZE:(i + 1) * BUFFER_SIZE] for i in range(num_segments)
    ]

    decoded_segments = [segment.decode("utf-8") for segment in segments]
    print("Number of segments:", num_segments)
    print("Segments:", decoded_segments)

    for segment in segments:
        send_packet(fd, segment)
        ready_sockets, _, _ = select.select([fd], [], [], TIMEOUT)
        if ready_sockets:
            receive_ack(fd)
        else:
            print("Client - Received no acknowledgements, timed out.")
            print("Client - Resending packet.")
            # TODO - Billy: Compile packet here
            send_packet(fd, segment)

def start_transmission(fd):
    while True:
        message = input("Message to send to the server (type 'exit' to quit):\n")
        if message.lower() == "exit":
            print("Client - Exiting...")
            return

        handle_send(fd, message.encode())

def send_packet(fd, encoded_message):
    fd.sendto(encoded_message, (IP, PORT))

def receive_ack(fd):
    global RECEIVED_PACKET
    response, server_address = fd.recvfrom(BUFFER_SIZE)

    # Handling duplicated ACK
    while response == RECEIVED_PACKET:
        print("Client - Duplicated acknowledgement.")
        response, server_address = fd.recvfrom(BUFFER_SIZE)

        if response != RECEIVED_PACKET:
            print("Client - New acknowledgement.")
            break

    RECEIVED_PACKET = response
    print(f"Response from Server: {response.decode()}")

if __name__ == "__main__":
    parse_arguments()
    client_socket = create_socket()
    start_transmission(client_socket)
    print("Client - Closing socket")
    client_socket.close()

    # message = "Hello World"
    # packet = compile_packet(message)
    # print(f"Packet: {packet}")