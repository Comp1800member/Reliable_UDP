import random
from tkinter.ttk import Label


def generate_sequence_number():
    # Return 4-byte random number
    return random.getrandbits(32)

def calculate_acknowledgement_number(sequence_num, payload_size):
    return (sequence_num + payload_size) % (2**32)

def calculate_packet_size(payload_size):
    return payload_size + (3 * 4) + 3 * len(";".encode("utf-8"))

def get_payload_size(payload):
    return len(payload.encode("utf-8"))

# TODO - Billy: Fix sequence vs acknowledgement number logic
# def compile_packet(payload):
#     payload_size = get_payload_size(payload)
#     print(f"Payload size: {payload_size}")
#     sequence_num = generate_sequence_number()
#     ack_num = calculate_acknowledgement_number(sequence_num, payload_size)
#     packet_size = calculate_packet_size(payload_size)
#     return f"{packet_size};{sequence_num};{ack_num};{payload}"

def get_fields(packet):
    fields = packet.split(";")
    packet_size = fields[0]
    sequence_num = fields[1]
    ack_num = fields[2]
    payload = fields[3]
    return packet_size, sequence_num, ack_num, payload