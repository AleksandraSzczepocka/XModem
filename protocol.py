import serial
import time
import math

SOH = 0x01
EOT = 0x04
ACK = 0x06
NAK = 0x15
CAN = 0x18
C   = 0x43

ALGEBRAIC_CHECKSUM = 0
CRC16 = 1

def algebraic_checksum(data):
    return sum(data) % 256

def crc16_checksum(data):
    # Append two zero bytes
    poly = 0x11021
    a = list(data) + [0, 0]
    for bit_index in range(len(data) * 8):
        byte_index = bit_index // 8
        bit_pos = 7 - (bit_index % 8)
        if a[byte_index] & (1 << bit_pos):
            to_xor = poly << (7 - bit_pos)
            a[byte_index] ^= (to_xor >> 16) & 0xFF
            a[byte_index+1] ^= (to_xor >> 8) & 0xFF
            a[byte_index+2] ^= to_xor & 0xFF
    return bytes(a[-2:])
