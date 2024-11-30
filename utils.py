import sys

INIT_PACKET = 1
PACKET_SIZE = 1024

# def generate_sequence_number(received_ack = INIT_PACKET):
#     # Return 4-byte random number
#     # return random.getrandbits(32)
#     return received_ack

def calculate_acknowledgement_number(received_seq, received_payload_size):
    return received_seq + received_payload_size

def calculate_packet_size(seq_num, ack_num, payload_size):
    header_payload_size = payload_size + 3 + seq_num + ack_num
    total_length = len(str(header_payload_size)) + header_payload_size

    # if total_length > PACKET_SIZE:
    #     print(f"Error: Packet size must be smaller than 1024. Try again.")
    #     sys.exit()

    return total_length

def get_payload_size(payload):
    return len(payload)

# TODO - Billy: Fix sequence vs acknowledgement number logic
def compile_packet(seq_num = INIT_PACKET, received_payload_size = 0, payload = ""):
    payload_size = get_payload_size(payload)
    print(f"To send payload size: {payload_size}")
    # seq_num = generate_sequence_number(received_ack)
    ack_num = calculate_acknowledgement_number(seq_num, received_payload_size)
    packet_size = calculate_packet_size(seq_num, ack_num, payload_size)

    # Send packet in bytes
    return f"{packet_size};{seq_num};{ack_num};{payload}".encode('utf-8')

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
