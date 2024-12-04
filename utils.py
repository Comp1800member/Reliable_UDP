from rich import print as rprint
import matplotlib.pyplot as plt

INIT_PACKET = 1
PACKET_SIZE = 1024
PAYLOAD_SIZE = PACKET_SIZE - 4 * 3 - 3

def calculate_acknowledgement_number(received_seq, received_payload_size):
    return received_seq + received_payload_size

def calculate_packet_size(payload_size):
    header_size = 3 + 4 * 3 # 3 * ";" + 3 * 4-byte-header-field
    total_length = header_size + payload_size

    return total_length

def get_payload_size(payload):
    return len(payload)

def compile_packet(seq_num, received_seq_num, received_payload_size, payload):
    payload_size = get_payload_size(payload)
    ack_num = calculate_acknowledgement_number(received_seq_num, received_payload_size)
    packet_size = calculate_packet_size(payload_size)

    # Send packet in bytes
    return f"{packet_size:04};{seq_num:04};{ack_num:04};{payload}".encode('utf-8')

def get_fields(packet):
    try:
        fields = packet.decode().split(";")
        packet_size = fields[0]
        sequence_num = fields[1]
        ack_num = fields[2]
        payload = fields[3]
        return int(packet_size), int(sequence_num), int(ack_num), str(payload)
    except Exception as e:
        print(f"[red]Error: {e}[red]")

# Graphing utilities
class graphing:
    def __init__(self):
        self.client_packets_received = 0
        self.server_packets_received = 0
        self.client_packets_sent = 0
        self.server_packets_sent = 0
        self.packets_retransmitted = 0
        self.packets_lost = 0
        self.latency = []

    def log_packet_received(self, source):
        if source == "client":
            self.client_packets_received += 1
            self.plot_client_metrics()
        elif source == "server":
            self.server_packets_received += 1
            self.plot_server_metrics()

    def log_packet_sent(self, destination):
        if destination == "client":
            self.client_packets_sent += 1
            self.plot_client_metrics()
        elif destination == "server":
            self.server_packets_sent += 1
            self.plot_server_metrics()

    def log_packet_retransmitted(self):
        self.packets_retransmitted += 1
        self.plot_client_metrics()

    def log_packet_lost(self):
        self.packets_lost += 1
        self.plot_client_metrics()

    def log_latency(self, latency_ms):
        self.latency.append(latency_ms)
        self.plot_latency()

    def average_latency(self):
        return sum(self.latency) / len(self.latency) if self.latency else 0

    def plot_client_metrics(self):
        self.packets_lost = self.client_packets_sent - self.client_packets_received
        plt.figure(figsize=(10, 6))
        plt.bar(["Packets Sent", "Packets Received", "Packets Retransmitted", "Packets Lost"],
                [self.client_packets_sent, self.client_packets_received, self.packets_retransmitted, self.packets_lost],
                color=['blue', 'green', 'red', 'black'])
        plt.title("Client Packets Analysis")
        plt.ylabel("Count")
        plt.savefig("client_packets.png")
        plt.close()

    def plot_server_metrics(self):
        # Plot packets received
        plt.figure(figsize=(10, 6))
        plt.bar(["Packets Received", "Packets Sent"],
                [self.server_packets_received, self.server_packets_sent],
                color=['cyan', 'pink'])
        plt.title("Server Packets Analysis")
        plt.ylabel("Count")
        plt.savefig("server_packets.png")
        plt.close()

    def plot_latency(self):
        # Plot latency
        if self.latency:
            plt.figure(figsize=(10, 6))
            plt.plot(self.latency, label="Latency (ms)", marker='o')
            plt.title(f"Latency over Time")
            plt.xlabel("Packet Index")
            plt.ylabel("Latency (ms)")
            plt.legend()
            plt.grid()
            plt.savefig("latency_over_time.png")
            plt.close()
        else:
            rprint("[red]Error: No latency data available to plot.[red]")