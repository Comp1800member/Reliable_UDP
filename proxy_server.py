import socket, select, os, argparse, threading, ipaddress
import sys
import random
import time

from server import bind_socket, create_socket, close_socket, receive_data

# TODO: Clean up

def handle_arguments(args):
    listen_ip = args.listen_ip
    listen_port = args.listen_port
    target_ip = args.target_ip
    target_port = args.target_port
    client_drop = args.client_drop
    server_drop = args.server_drop
    client_delay = args.client_delay
    server_delay = args.server_delay

    #--listen port + ip
    if listen_port < 1 or listen_port > 65535:
        print('port must be between 1 and 65535')
        exit(-1)
    try:
        ipaddress.ip_address(listen_ip)
    except ValueError:
        print("Invalid listen IP address")
        exit(-1)

    #target port and ip
    if target_port < 1 or target_port > 65535:
        print('port must be between 1 and 65535')
        exit(-1)
    try:
        ipaddress.ip_address(target_ip)
    except ValueError:
        print("Invalid target IP address")
        exit(-1)

    #drops
    if client_drop > 100 or client_drop < 0:
        print('client drop must be between 0 and 100')
        exit(-1)
    if server_drop > 100 or server_drop < 0:
        print('server drop must be between 0 and 100')
        exit(-1)


    #delays
    if client_delay > 100 or client_delay < 0:
        print('client delay must be between 0 and 100')
        exit(-1)
    if server_delay > 100 or server_delay < 0:
        print('server delay must be between 0 and 100')
        exit(-1)

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--listen-ip", type=str, required=True, help="IP address for proxy server")
    parser.add_argument("--listen-port", type=int, required=True, help="The port number to listen for client")
    parser.add_argument("--target-ip", type=str, required=True, help="IP address of server to forward packets to")
    parser.add_argument("--target-port", type=int, required=True, help="The port number of the server")
    parser.add_argument("--client-drop", type=int, default=0, help="the percent chance to drop packets from the client")
    parser.add_argument("--server-drop", type=int, default=0, help="the percent chance to drop packets from the server")
    parser.add_argument("--client-delay", type=int, default=0, help="the percent chance to delay packets from the client")
    parser.add_argument("--server-delay", type=int, default=0, help="the percent chance to delay packets from the server")
    parser.add_argument("--client-delay-time", type=str, default="0", help="the delay time in milliseconds for packets from the client")
    parser.add_argument("--server-delay-time", type=str, default="0", help="the delay time in milliseconds for packets from the server")

    args = parser.parse_args()
    print(args)
    handle_arguments(args)
    return args

def send_packet(fd, address, packet):
    try:
        print(f"Proxy - Sending packet to {(address[0], address[1])}")
        fd.sendto(packet, address)
    except socket.error as e:
        fd.close()
        sys.exit("Proxy - Error sending packet to server: {}".format(e))

def handle_drop(drop_percentage):
    random_num = random.randint(1, 100)
    print(f"Random number for dropping {random_num}")
    if random_num <= drop_percentage or drop_percentage == 0:
        print("Proxy - No dropping, delaying if any...")
        return False
    else:
        print("Proxy - Dropping packet, returning...")
        return True

def handle_delay(delay_percentage, delay_time):
    random_num = random.randint(1, 100)
    # print(f"Random number for delaying {random_num}")
    if random_num >= delay_percentage != 0:
        print(f"Proxy - Delaying packet by {delay_time} milliseconds")
        time.sleep(delay_time / 1000)
    else:
        print(f"Proxy - No delaying")


def handle_value_or_range(delay):
    if delay.isdigit():
        try:
            int_delay = int(delay)
            return int_delay
        except ValueError:
            pass  # If it can't
    else:
        try:
            count_dash = delay.count('-')
            if count_dash != 1:
                print("there should only be 1 dash in your range")
                raise ValueError
            else:
                before, after = delay.split('-')
                try:
                    low = int(before)
                    high = int(after)
                except ValueError:
                    print("Please enter your range as #-#")
                    exit(-1)
                if low > high:
                    print("Start cannot be greater than end of range")
                    raise ValueError
                range_list = [low, high]
                return [low, high]
        except ValueError as e:
            print(e)
            exit(-1)

if __name__ == '__main__':
    args = parse_arguments()
    listen_ip = args.listen_ip
    listen_port = args.listen_port
    target_ip = args.target_ip
    target_port = args.target_port
    # client_drop = args.client_drop
    # client_delay = args.client_delay
    # server_drop = args.server_drop
    # server_delay = args.server_delay
    # client_delay_time = handle_value_or_range(args.client_delay_time)
    # server_delay_time = handle_value_or_range(args.server_delay_time)

    # TODO: Configurable server but it's a one time thing
    client_drop = input(
        "New client drop percentage (0 to 100, or press enter to use pre-defined or default value):\n") or args.client_drop
    client_delay = input(
        "New client delay percentage (0 to 100, or press enter to use pre-defined or default value):\n") or args.client_delay
    server_drop = input(
        "New server drop percentage (0 to 100, or press enter to use pre-defined or default value):\n") or args.server_drop
    server_delay = input(
        "New server delay percentage (0 to 100, or press enter to use pre-defined or default value):\n") or args.server_delay
    client_delay_time = handle_value_or_range(input(
        "New client delay time (in milliseconds, or press enter to use pre-defined or default value):\n") or args.client_delay_time)
    server_delay_time = handle_value_or_range(input(
        "New server delay time (in milliseconds, or press enter to use pre-defined or default value):\n") or args.server_delay_time)

    # print(isinstance(client_delay_time, list))
    client_fd = create_socket()
    server_fd = create_socket()
    routing_table = {}
    bind_socket(client_fd, listen_ip, listen_port)

    try:
        while True:
            ready, _, _ = select.select([client_fd, server_fd], [], [])

            for sock in ready:
                if sock is client_fd:
                    print(f"Client sock ready")
                    client_packet, client_addr = receive_data(client_fd)  # Buffer size of 1024 bytes
                    print(f"Received '{client_packet.decode()} from {client_addr}")

                    # Drop
                    if handle_drop(client_drop):
                        continue

                    # Delay
                    handle_delay(client_delay_time, client_delay_time)
                    # Forward packet from client to server
                    send_packet(server_fd, (target_ip, target_port), client_packet)

                    routing_table[(target_ip, target_port)] = client_addr

                if sock is server_fd:
                    print(f"Server sock ready")
                    server_packet, server_addr = receive_data(server_fd)
                    print(f"Received '{server_packet.decode()} from {server_addr}")

                    client_addr = routing_table.get((target_ip, target_port))

                    if client_addr:
                        # Drop
                        if handle_drop(server_drop):
                            continue
                        # Delay
                        handle_delay(server_delay, server_delay_time)
                        # Forward packet from server to client
                        send_packet(client_fd, client_addr, server_packet)

    except socket.error as e:
        print(f"Proxy - Socket error: {e}. Closing...")
        close_socket(client_fd)
        close_socket(server_fd)
        exit(-1)

    except KeyboardInterrupt:
        print("Proxy - Keyboard interrupt. Closing...")
        close_socket(client_fd)
        close_socket(server_fd)
        exit(-1)
