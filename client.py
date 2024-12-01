import argparse
import sys
import socket

IP = ""
PORT = 0
TIMEOUT = 2
BUFFER_SIZE = 1024

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

def start_transmission(fd):
    while True:
        message = input("Message to send to the server (type 'exit' to quit):\n")
        if message.lower() == "exit":
            print("Client - Exiting...")
            return

        send_packet(fd, message)

def send_packet(fd, message):
    fd.sendto(message.encode(), (IP, PORT))
    receive_ack(fd)

def receive_ack(fd):
    response, server_address = fd.recvfrom(BUFFER_SIZE)
    print(f"Response from Server: {response.decode()}")

if __name__ == "__main__":
    parse_arguments()
    client_socket = create_socket()
    start_transmission(client_socket)
    print("Client - Closing socket")
    client_socket.close()