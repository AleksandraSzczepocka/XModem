from protocol import *

def send_file(serial_port, file_bytes, mode):
    print("Czekam na odbiornik...")
    while True:
        c = serial_port.read()
        if (mode == ALGEBRAIC_CHECKSUM and c == bytes([NAK])) or \
           (mode == CRC16 and c == bytes([C])):
            break

    no_of_blocks = math.ceil(len(file_bytes) / 128)

    for i in range(no_of_blocks):
        block = file_bytes[i * 128: (i + 1) * 128]
        block += bytes([0] * (128 - len(block)))  # pad with zeros
        block_number = (i + 1) & 0xFF
        header = bytes([SOH, block_number, 255 - block_number])
        serial_port.write(header + block)

        if mode == ALGEBRAIC_CHECKSUM:
            serial_port.write(bytes([algebraic_checksum(block)]))
        else:
            serial_port.write(crc16_checksum(block))

        response = serial_port.read()
        if response == bytes([NAK]):
            i -= 1
        elif response == bytes([CAN]):
            raise Exception("Connection canceled!")
        elif response == bytes([C]):
            continue
        elif response != bytes([ACK]):
            raise Exception("Protocol error!")

    serial_port.write(bytes([EOT]))
    print("Plik wysłany.")
