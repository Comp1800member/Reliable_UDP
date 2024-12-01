import socket, select, os, argparse, threading, ipaddress
import sys
import random
import time

from server import bind_socket, create_socket, close_socket, receive_data

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
    parser.add_argument("--client-delay-time", type=str, help="the delay time in milliseconds for packets from the client")
    parser.add_argument("--server-delay-time", type=str, help="the delay time in milliseconds for packets from the server")

    args = parser.parse_args()
    print(args)
    handle_arguments(args)
    return args

def send_packet(fd, ip, port, packet):
    try:
        fd.sendto(packet, (ip, port))
    except socket.error as e:
        fd.close()
        sys.exit("Proxy - Error sending packet to server: {}".format(e))

#
def handle_packet(fd, drop_percentage, delay_percentage, delay_time, ip, port, packet):
    random_num = random.randint(1, 100)
    if random_num <= drop_percentage != 0:
        print("Proxy - No dropping, delaying if anys...")
        # TODO - delay here if no drop
        # if delay then timeout
        handle_delay(delay_percentage, delay_time)
        # After delay, send packet
        send_packet(fd, ip, port, packet)
        return False
    else:
        print("Proxy - Dropping packet, returning...")
        return True

def handle_delay(delay_percentage, delay_time):
    random_num = random.randint(1, 100)
    if random_num >= delay_percentage != 0:
        print(f"Proxy - Delaying packet by {delay_time} milliseconds")
        time.sleep(delay_time / 1000)

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
    client_drop = args.client_drop
    client_delay = args.client_delay
    server_drop = args.server_drop
    server_delay = args.server_delay
    client_delay_time = handle_value_or_range(args.client_delay_time)
    server_delay_time = handle_value_or_range(args.server_delay_time)

    print(isinstance(client_delay_time, list))

    client_fd = create_socket()
    bind_socket(client_fd, listen_ip, listen_port)

    server_fd = create_socket()

    try:
        while True:
            ready, _, _ = select.select([client_fd], [], [])
            for sock in ready:
                data, client_addr = receive_data(sock)  # Buffer size of 1024 bytes
                print(f"Received '{data.decode()} from {client_addr}")

                # TODO: Handle drop and/or delay here
                # Drop and/or delay from client to server
                if handle_packet(server_fd, client_drop, client_delay, client_delay_time, target_ip, target_port, data):
                    continue

                # Drop or delay from server to client
                if handle_packet(client_fd, server_drop, server_delay, server_delay_time, listen_ip, listen_port, data):
                    continue

    except KeyboardInterrupt:
        print("\nKeyboard Interrupt: Proxy Server shutting down.")
        exit(-1)
    finally:
        close_socket(client_fd)
        close_socket(server_fd)
