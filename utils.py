import sys

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
    print(f"To send payload size: {payload_size}")
    ack_num = calculate_acknowledgement_number(received_seq_num, received_payload_size)
    packet_size = calculate_packet_size(payload_size)

    # Send packet in bytes
    return f"{packet_size:04};{seq_num:04};{ack_num:04};{payload}".encode('utf-8')

def get_fields(packet):
    print(f"Getting fields of packet: {packet}")
    try:
        fields = packet.decode().split(";")
        packet_size = fields[0]
        sequence_num = fields[1]
        ack_num = fields[2]
        payload = fields[3]
        return int(packet_size), int(sequence_num), int(ack_num), str(payload)
    except Exception as e:
        print(f"Error: {e}")
