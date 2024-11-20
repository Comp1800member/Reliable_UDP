import select
import socket
import os
import argparse
import threading
import ipaddress

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
    #note to self, changed to DGRAM for UDP
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


if __name__ == "__main__":
    args = parse_arguments()
    port = args.listen_port
    ip_addr = args.listen_ip
    socket = create_socket()

    bind_socket(socket, ip_addr, port)

    print(f"Server listening on {port}")
    timeout = 2
    try:
        while True:
            ready, _, _ = select.select([socket], [], [], 2)
            if not ready:
                print(f"Nothing received in last {timeout} seconds")
            #currently only socket we are listening for is the server's socket,
            #so not really handling anything else, just getting data and stuff for that.
            for sock in ready:
                    data, client_addr = receive_data(socket)
                    print(f"Received '{data.decode()} from {client_addr}")

                    response = f"Hello, {data.decode()}"
                    socket.sendto(response.encode(), client_addr)

    except KeyboardInterrupt:
        print("\nKeyboard Interrupt: Server shutting down.")
        exit(-1)
    finally:
        close_socket(socket)
