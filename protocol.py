SOH = 0x01
EOT = 0x04
ACK = 0x06
NAK = 0x15
CAN = 0x18
C = 0x43

BLOCK_SIZE = 128

def calc_checksum(data: bytes) -> int:
    return sum(data) % 256

def calc_crc(data: bytes) -> int:
    crc = 0
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
    return crc & 0xFFFF

def create_block(block_num: int, data: bytes, use_crc=False):
    data = data.ljust(BLOCK_SIZE, b'\x1A')
    header = bytes([SOH, block_num % 256, 255 - (block_num % 256)])
    if use_crc:
        crc = calc_crc(data)
        footer = crc.to_bytes(2, 'big')
    else:
        checksum = calc_checksum(data)
        footer = bytes([checksum])
    return header + data + footer
