import argparse
import math
import sys
import socket
import ipaddress
import random
from rich import print as rprint
from utils import graphing, compile_packet, get_fields, INIT_PACKET, PAYLOAD_SIZE

IP = "0.0.0.0"
PORT = 5000
TIMEOUT = 2.0
MAX_TIMEOUT = 10.0
BUFFER_SIZE = 4096

ACK_PACKET = None
RECV_PACKET = None
MAX_RETRIES = 3

client_graphing = graphing()

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

    if ipaddress.ip_address(args.target_ip):
        IP = args.target_ip
    else:
        rprint("[red]Error: Invalid IP address.[red]")
        sys.exit(-1)

    if 1 <= args.target_port <= 65535:
        PORT = args.target_port
    else:
        rprint("[red]Error: Invalid port number. (1 <= PORT <= 65535)[red]")
        sys.exit(-1)

    if args.timeout is not None:
        if args.timeout < 0 or args.timeout > MAX_TIMEOUT:
            rprint("[red]Error: Invalid timeout value. (0 <= TIMEOUT <= 10)[red]")
            sys.exit(-1)
        TIMEOUT = args.timeout

    print("[CLIENT CONFIGURATIONS]")
    print(f"IP Address: {IP}")
    print(f"Port: {PORT}")
    print(f"Timeout (seconds): {TIMEOUT}")
    print("=============================================")


def create_socket():
    rprint("Creating socket...")
    try:
        fd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    except socket.error as e:
        rprint("[red]Error creating socket: {}[red]".format(e))
        sys.exit(-1)

    return fd

def segment_packet(payload):
    num_segments = math.ceil(len(payload) / PAYLOAD_SIZE)

    segments = [
        payload[i * PAYLOAD_SIZE:(i + 1) * PAYLOAD_SIZE] for i in range(num_segments)
    ]

    return [segment.decode("utf-8") for segment in segments]

def start_transmission(fd):
    while True:
        rprint("[green bold]Message to send to the server (type 'exit' or ctrl+D to quit):[green bold]")
        message = input()
        if message.lower() == "exit":
            rprint("[yellow]Exiting...[yellow]")
            return
        rprint("=============================================")
        handle_send(fd, message.encode())

def send_packet(fd, encoded_packet):
    try:
        rprint(f"Sending packet {encoded_packet}.")
        client_graphing.log_packet_sent("client")
        fd.sendto(encoded_packet, (IP, PORT))
        fd.settimeout(TIMEOUT)
    except socket.error as e:
        rprint(f"[red]Error sending packet: {format(e)}. Try again.[red]")
        fd.close()
        sys.exit()

def is_duplicated_packet(received_packet):
    global ACK_PACKET
    return ACK_PACKET == received_packet

def receive_ack(fd):
    global ACK_PACKET, RECV_PACKET
    try:
        while True:
            rprint("Waiting for acknowledgement...")
            RECV_PACKET, server_address = fd.recvfrom(BUFFER_SIZE)
            rprint(f"Received packet: {RECV_PACKET}")
            client_graphing.log_packet_received("client")

            # Handling duplicated ACK
            if not is_duplicated_packet(RECV_PACKET):
                rprint("[green bold]New acknowledgement found:[green bold]")
                packet_size, seq_num, ack_num, payload = get_fields(RECV_PACKET)
                print(f"\tPacket size: {packet_size}")
                print(f"\tSequence number: {seq_num}")
                print(f"\tAcknowledgement number: {ack_num}")
                print(f"\tPayload: {payload if not payload == "" else "N/A"}")
                ACK_PACKET = RECV_PACKET
                rprint("=============================================")
                break

            rprint("[yellow]Duplicated acknowledgement found.[yellow]")

    except socket.timeout as e:
        rprint("[red]Received no acknowledgements, timed out.[red]")
        ACK_PACKET = RECV_PACKET
        return False

    except socket.error as e:
        rprint(f"[red]Error receiving ACK: {format(e)}. Try again.[red]")
        fd.close()
        sys.exit()

    return True

def handle_send(fd, encoded_message):
    retries = 0
    seq_num = random.randint(1, 9999 - BUFFER_SIZE) # Leave extra rooms in case of segmentation
    received_seq_num = INIT_PACKET
    received_payload_size = 0

    decoded_segments = segment_packet(encoded_message)

    for segment in decoded_segments:
        packet_to_send = compile_packet(seq_num, received_seq_num, received_payload_size, segment)

        # Send packet
        send_packet(fd, packet_to_send)

        # Receive ack
        while retries < MAX_RETRIES:
            # Re-transmit packet
            if not receive_ack(fd):
                retries += 1
                rprint(f"[yellow]Resending packet. Retry #{retries}[yellow]")
                send_packet(fd, packet_to_send)
                client_graphing.log_packet_retransmitted()
            else:
                break

        if retries >= MAX_RETRIES:
            rprint("[red]Maximum retries exceeded. Try again.[red]")
            fd.close()
            client_graphing.plot_client_metrics()
            sys.exit(-1)

        _, received_seq_num, received_ack_num, payload = get_fields(ACK_PACKET)
        received_payload_size = len(payload)
        seq_num = received_ack_num

if __name__ == "__main__":
    parse_arguments()
    client_socket = create_socket()

    try:
        start_transmission(client_socket)
    except KeyboardInterrupt:
        rprint("[red]Keyboard interrupt. Closing[red]")
        client_socket.close()
        client_graphing.plot_client_metrics()
        exit(0)
