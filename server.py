import socket, select, argparse, ipaddress, sys
from rich import print as rprint

from utils import graphing, compile_packet, get_fields, INIT_PACKET

server_graphing = graphing()

def handle_arguments(args):
    ip = args.listen_ip
    if args.listen_port < 1 or args.listen_port > 65535:
        rprint('[red]Error: Port must be between 1 and 65535[red]')
        exit(-1)
    try:
        ipaddress.ip_address(ip)
    except ValueError:
        rprint("[red]Error: Invalid IP address[red]")
        exit(-1)


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--listen-ip", type=str, help="IP address of the server")
    parser.add_argument("--listen-port", type=int, help="The port number")
    args = parser.parse_args()
    handle_arguments(args)
    return args


def create_socket():
    # note to self, changed to DGRAM for UDP
    try:
        fd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except socket.error as e:
        rprint(f"[red]Failed to create socket: {e}[red]")
        exit(-1)
    return fd


def bind_socket(server_socket, ip_addr, port):
    try:
        server_socket.bind((ip_addr, port))
    except OSError as e:
        rprint(f"[red]Binding failed: {e}[red]")
        exit(-1)


def close_socket(sock_to_close):
    try:
        sock_to_close.close()
    except OSError as e:
        rprint(f"[red]Error: {e}[red]")
        exit(-1)


def receive_data(server_socket):
    try:
        data, client_address = server_socket.recvfrom(1024)
    except Exception as e:
        rprint(f"[red]Error: {e}[red]")
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
    print("[SERVER CONFIGURATIONS]")
    print(f"IP Address: {ip_addr}")
    print(f"Port: {port}")
    print("=============================================")
    server_socket = create_socket()

    bind_socket(server_socket, ip_addr, port)

    try:
        while True:
            ready, _, _ = select.select([server_socket], [], [])
            for sock in ready:
                data, client_addr = receive_data(sock)  # Buffer size of 1024 bytes
                rprint(f"Received packet: {data}")
                server_graphing.log_packet_received("server")

                received_packet_size, received_seq_number, received_ack_num, payload = get_fields(data)
                rprint("[green bold]Client packet found:[green bold]")
                print(f"\tPacket size: {received_packet_size}")
                print(f"\tSequence number: {received_seq_number}")
                print(f"\tAcknowledgement number: {received_ack_num}")
                print(f"\tPayload: {payload if not payload == "" else "N/A"}")
                print("=============================================")
                print("[DISPLAY CLIENT PAYLOAD]")
                rprint(f"[green]{payload}[green]")
                packet_to_send = compile_packet(received_ack_num, received_seq_number, len(payload), "")
                server_socket.sendto(packet_to_send, client_addr)
                server_graphing.log_packet_sent("server")
                rprint(f"\nSending packet {packet_to_send}")
                print("=============================================")

    except KeyboardInterrupt:
        rprint("[red]Keyboard Interrupt: Server shutting down.[red]")
        close_socket(server_socket)
        # server_graphing.plot_server_metrics()
        exit(0)
