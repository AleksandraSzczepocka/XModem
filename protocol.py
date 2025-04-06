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
    crc = 0xFFFF  # Inicjalizacja wartości CRC
    for byte in data:
        crc ^= byte  # XOR z bajtem danych
        for _ in range(8):  # Proces przetwarzania każdego bitu
            if crc & 0x0001:  # Sprawdzamy najmłodszy bit
                crc = (crc >> 1) ^ 0xA001  # Polinom CRC-16-IBM (0x8005, odwrócony)
            else:
                crc >>= 1
    return crc.to_bytes(2, 'little')
