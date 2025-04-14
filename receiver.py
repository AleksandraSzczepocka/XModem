import serial
import time
from protocol import *

def receive_file(ser: serial.Serial, filename: str):
    use_crc = True
    with open(filename, 'wb') as f:
        # Zainicjuj transmisję
        start = time.time()
        while True:
            ser.write(bytes([C if use_crc else NAK]))
            time.sleep(1)
            if ser.in_waiting:
                break
            if time.time() - start > 60:
                print("Timeout waiting for sender.")
                return

        expected_block = 1
        while True:
            start_byte = ser.read(1)
            if start_byte == bytes([SOH]):
                block_header = ser.read(2)
                block_num, block_neg = block_header[0], block_header[1]

                if block_num != expected_block:
                    ser.write(bytes([NAK]))
                    continue

                data = ser.read(BLOCK_SIZE)
                if use_crc:
                    recv_crc = int.from_bytes(ser.read(2), 'big')
                    calc = calc_crc(data)
                    if calc != recv_crc:
                        ser.write(bytes([NAK]))
                        continue
                else:
                    recv_sum = ord(ser.read(1))
                    calc = calc_checksum(data)
                    if calc != recv_sum:
                        ser.write(bytes([NAK]))
                        continue

                f.write(data)
                ser.write(bytes([ACK]))
                expected_block += 1

            elif start_byte == bytes([EOT]):
                ser.write(bytes([ACK]))
                break
