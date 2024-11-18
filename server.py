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

def socket_create():
    #note to self, changed to DGRAM for UDP
    return socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def socket_bind(server_socket, ip_addr, port):
    try:
        server_socket.bind((ip_addr, port))
    except OSError as e:
        print(f"Binding failed: {e}")
        exit(-1)

def socket_close(socket):
    try:
        socket.close()
    except OSError as e:
        print(e)
        exit(-1)

if __name__ == "__main__":
    args = parse_arguments()
    port = args.listen_port
    ip_addr = args.listen_ip
    socket = socket_create()

    socket_bind(socket, ip_addr, port)

    print(f"Server listening on {port}")

    try:
        while True:
            ready, _, _ = select.select([socket], [], [], 2)

            if not ready:
                print("nothing received in last 2 seconds")
                continue

            for sock in ready:
                if sock == socket:
                    # Receive data from client
                    data, client_address = socket.recvfrom(1024)
                    print(f"Received '{data.decode()}' from {client_address}")

                    # Send response back to client
                    response = f"Hello, {data.decode()}!"
                    socket.sendto(response.encode(), client_address)
    except KeyboardInterrupt:
        print("\nKeyboard Interrupt: Server shutting down.")
        exit(-1)
    finally:
        socket_close(socket)
