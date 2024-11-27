import random

INIT_PACKET = 1
PACKET_SIZE = 1024

def generate_sequence_number(received_ack = INIT_PACKET):
    # Return 4-byte random number
    # return random.getrandbits(32)
    return received_ack

def calculate_acknowledgement_number(received_seq, received_payload_size):
    return received_seq + received_payload_size

def calculate_packet_size(seq_num, ack_num, payload_size):
    header_payload_size = payload_size + 3 + seq_num + ack_num
    total_length = len(str(header_payload_size))

    return total_length

def get_payload_size(payload):
    return len(payload)

# TODO - Billy: Fix sequence vs acknowledgement number logic
def compile_packet(received_seq, received_ack, received_payload_size, payload):
    payload_size = get_payload_size(payload)
    print(f"To send payload size: {payload_size}")
    seq_num = generate_sequence_number(received_ack)
    ack_num = calculate_acknowledgement_number(received_seq, received_payload_size)
    packet_size = calculate_packet_size(payload_size, seq_num, ack_num)

    return f"{packet_size};{seq_num};{ack_num};{payload}"

def get_fields(packet):
    try:
        fields = packet.split(";")
        packet_size = fields[0]
        sequence_num = fields[1]
        ack_num = fields[2]
        payload = fields[3]
        return int(packet_size), int(sequence_num), int(ack_num), payload
    except Exception as e:
        print(f"Error: {e}")
