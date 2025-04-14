import serial
import time
from protocol import *

def send_file(ser: serial.Serial, filename: str, use_crc=False):
    with open(filename, 'rb') as f:
        block_num = 1

        # Czekaj na inicjację przez odbiornik
        start_time = time.time()
        while True:
            if ser.in_waiting:
                start_byte = ser.read(1)
                if start_byte in [bytes([NAK]), bytes([C])]:
                    use_crc = (start_byte == bytes([C]))
                    break
            if time.time() - start_time > 60:
                print("Timeout waiting for receiver.")
                return

        while True:
            data = f.read(BLOCK_SIZE)
            if not data:
                break

            block = create_block(block_num, data, use_crc)
            while True:
                ser.write(block)
                response = ser.read(1)
                if response == bytes([ACK]):
                    block_num += 1
                    break
                elif response == bytes([NAK]):
                    continue
                else:
                    print("Transmission canceled or unknown error.")
                    return

        # Wysyłanie EOT
        while True:
            ser.write(bytes([EOT]))
            if ser.read(1) == bytes([ACK]):
                break
