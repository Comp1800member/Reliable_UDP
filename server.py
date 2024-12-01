import socket, select, os, argparse, threading, ipaddress
import time
import random
from utils import compile_packet, get_fields, INIT_PACKET

def handle_arguments(args):
    ip = args.listen_ip
    if args.listen_port < 1 or args.listen_port > 65535:
        print('port must be between 1 and 65535')
        exit(-1)
    try:
        ipaddress.ip_address(ip)
    except ValueError:
        print("Invalid IP address")


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--listen-ip", type=str, help="IP address of the server")
    parser.add_argument("--listen-port", type=int, help="The port number")
    args = parser.parse_args()
    print(args)
    handle_arguments(args)
    return args


def create_socket():
    # note to self, changed to DGRAM for UDP
    return socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def bind_socket(server_socket, ip_addr, port):
    try:
        server_socket.bind((ip_addr, port))
    except OSError as e:
        print(f"Binding failed: {e}")
        exit(-1)


def close_socket(sock_to_close):
    try:
        sock_to_close.close()
    except OSError as e:
        print(e)
        exit(-1)


def receive_data(server_socket):
    try:
        data, client_address = server_socket.recvfrom(1024)
    except Exception as e:
        print(e)
        exit(-1)
    return data, client_address


def send_ack():
    pass


set_delay = False
seq_num = INIT_PACKET

if __name__ == '__main__':


    args = parse_arguments()
    port = args.listen_port
    ip_addr = args.listen_ip
    server_socket = create_socket()

    bind_socket(server_socket, ip_addr, port)

    try:
        while True:
            ready, _, _ = select.select([server_socket], [], [])
            for sock in ready:
                data, client_addr = receive_data(sock)  # Buffer size of 1024 bytes
                print(f"Received '{data.decode()} from {client_addr}")

                # Test: delay scenario
                if not set_delay:
                    time.sleep(5)
                    set_delay = True

                _, received_seq_number, received_ack_num, payload = get_fields(data)
                print(f"PAYLOAD FROM CLIENT: {payload}")
                packet_to_send = compile_packet(received_ack_num, received_seq_number, len(payload), "")
                server_socket.sendto(packet_to_send, client_addr)
                print(f"Sent message \"{packet_to_send}\" to {client_addr}")

    except KeyboardInterrupt:
        print("\nKeyboard Interrupt: Server shutting down.")
        exit(-1)
    finally:
        close_socket(server_socket)