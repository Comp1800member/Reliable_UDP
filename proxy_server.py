import socket, select, argparse, ipaddress
import sys
import random
import threading
import time
from rich import print as rprint
from server import bind_socket, create_socket, close_socket, receive_data

class proxy_server:
    def __init__(self, arguments):
        self.client_drop = arguments.client_drop
        self.server_drop = arguments.server_drop
        self.client_delay = arguments.client_delay
        self.server_delay = arguments.server_delay
        self.client_delay_time = arguments.client_delay_time
        self.server_delay_time = arguments.server_delay_time

    def update_drop_delay(self):
        while True:
            try:
                self.client_drop = int(input("Please enter a new client drop value "))
                if self.client_drop > 100:
                    print("Please enter a client drop value between 0 and 100")
                    break
                self.server_drop = int(input("Please enter a new server drop value "))
                if self.server_drop > 100:
                    print("Please enter a client drop value between 0 and 100")
                    break
                self.client_delay = int(input("Please enter a new client delay value "))
                if self.client_delay > 100:
                    print("Please enter a client drop value between 0 and 100")
                    break
                self.server_delay = int(input("Please enter a new server delay value "))
                if self.server_delay > 100:
                    print("Please enter a client drop value between 0 and 100")
                    break
                self.client_delay_time = int(input("Please enter a new client delay timevalue "))
                self.server_delay_time = int(input("Please enter a new server delay time value "))
                loop = int(input("Would you like to continue entering values? 1 for yes 0 for no"))
                if loop != 1:
                    break
            except SystemExit:
                print("Invalid input format")
            except ValueError:
                print("Please enter an integer between 0 and 100")
                exit(-1)

def handle_port(port):
    if port < 1 or port > 65535:
        rprint('[red]Error: Port must be between 1 and 65535[red]')
        exit(-1)

def handle_ip(ip):
    try:
        ipaddress.ip_address(ip)
    except ValueError:
        rprint("[red]Error: Invalid IP address[red]")
        exit(-1)

def handle_drop_value(value):
    if value > 100 or value < 0:
        rprint('[red]Error: Drop percentage must be between 0 and 100[red]')
        exit(-1)

def handle_delay_value(value):
    if value > 100 or value < 0:
        rprint('[red]Error: Delay percentage must be between 0 and 100[red]')
        exit(-1)

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
    handle_port(listen_port)
    handle_ip(listen_ip)

    #target port and ip
    handle_port(target_port)
    handle_ip(target_ip)

    #drops
    handle_drop_value(client_drop)
    handle_drop_value(server_drop)


    #delays
    handle_delay_value(client_delay)
    handle_delay_value(server_delay)

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
        print(f"Sending packet to {(address[0], address[1])}")
        fd.sendto(packet, address)
    except socket.error as e:
        fd.close()
        rprint(f"[red]Error sending packet to server: {e}[red]")
        exit(-1)

def handle_drop(drop_percentage):
    random_num = random.random()
    if random_num > (drop_percentage / 100) or drop_percentage == 0:
        rprint("[green]\t>> No dropping, delaying if any...[green]")
        return False
    else:
        rprint("[yellow]\t>> Dropping packet, returning...[yellow]")
        return True

def handle_delay(delay_percentage, delay_time):
    random_num = random.random()
    # print(f"Random number for delaying {random_num}")
    if random_num < (delay_percentage / 100) != 0:
        rprint(f"[yellow]\t>> Delaying packet by {delay_time} milliseconds[yellow]")
        time.sleep(delay_time / 1000)
    else:
        rprint(f"[green]\t>> No delaying[green]")


def handle_value_or_range(delay):
    if delay.isdigit():
        try:
            int_delay = int(delay)
            return int_delay
        except ValueError:
            rprint("[red]Error: Invalid value or range[red]")
            pass  # If it can't
    else:
        try:
            count_dash = delay.count('-')
            if count_dash != 1:
                rprint("[red]Error: There should only be 1 dash in your range[red]")
                raise ValueError
            else:
                before, after = delay.split('-')
                try:
                    low = int(before)
                    high = int(after)
                except ValueError:
                    rprint("[red]Error: Please enter your range as #-#[red]")
                    exit(-1)
                if low > high:
                    rprint("[red]Error: Start cannot be greater than end of range[red]")
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

    proxy = proxy_server(args)

    print("[PROXY SERVER CONFIGURATIONS]")
    print(f"Listen IP Address: {listen_ip}")
    print(f"Listen Port: {listen_port}")
    print(f"Target IP Address: {target_ip}")
    print(f"Target Port: {target_port}")
    print(f"Client Drop Percentage: {proxy.client_drop}")
    print(f"Client Delay Percentage: {proxy.client_delay}")
    print(f"Client Delay Time (milliseconds): {proxy.client_delay_time}")
    print(f"Server Drop Percentage: {proxy.server_drop}")
    print(f"Server Delay Percentage: {proxy.server_delay}")
    print(f"Server Delay Time (milliseconds): {proxy.server_delay_time}")
    print("=============================================")

    client_fd = create_socket()
    server_fd = create_socket()
    routing_table = {}
    bind_socket(client_fd, listen_ip, listen_port)

    try:
        threading.Thread(target=proxy.update_drop_delay, daemon=True).start()
        while True:
            ready, _, _ = select.select([client_fd, server_fd], [], [])

            for sock in ready:
                if sock is client_fd:
                    client_packet, client_addr = receive_data(client_fd)  # Buffer size of 1024 bytes
                    print(f"Client socket ready at {client_addr}")
                    print(f"\tReceived '{client_packet.decode()}")

                    # Drop
                    if handle_drop(proxy.client_drop):
                        continue

                    # Delay
                    handle_delay(proxy.client_delay, proxy.client_delay_time)

                    # Forward packet from client to server
                    send_packet(server_fd, (target_ip, target_port), client_packet)

                    routing_table[(target_ip, target_port)] = client_addr
                    print("=============================================")

                if sock is server_fd:
                    server_packet, server_addr = receive_data(server_fd)
                    print(f"Server sock ready at {server_addr}")
                    print(f"\tReceived '{server_packet.decode()}")

                    client_addr = routing_table.get((target_ip, target_port))

                    if client_addr:
                        # Drop
                        if handle_drop(proxy.server_drop):
                            continue

                        # Delay
                        handle_delay(proxy.server_delay, proxy.server_delay_time)

                        # Forward packet from server to client
                        send_packet(client_fd, client_addr, server_packet)
                        print("=============================================")

    except socket.error as e:
        rprint(f"[red]Socket error: {e}. Closing...[red]")
        close_socket(client_fd)
        close_socket(server_fd)
        exit(-1)

    except ValueError as e:
        rprint(f"[red]Value error: {e}. Please enter a # between 0 and 100 Closing...[red]")
        exit(-1)

    except KeyboardInterrupt:
        rprint("[red]Keyboard interrupt. Closing]")
        close_socket(client_fd)
        close_socket(server_fd)
        exit(-1)
