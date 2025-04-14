import serial
import time
from protocol import *

def read_exact(ser: serial.Serial, n: int) -> bytes:
    buf = b''
    while len(buf) < n:
        chunk = ser.read(n - len(buf))
        if not chunk:
            break
        buf += chunk
    return buf

def receive_file(ser: serial.Serial, filename: str):
    use_crc = True
    with open(filename, 'wb') as f:
        # Start transmission
        print("Wysyłanie C/NAK do rozpoczęcia transmisji...")
        start = time.time()
        while True:
            ser.write(bytes([C if use_crc else NAK]))
            time.sleep(1)
            if ser.in_waiting:
                print("Odpowiedź od nadajnika, rozpoczynam odbiór...")
                break
            if time.time() - start > 60:
                print("Timeout czekania na nadajnik.")
                return

        expected_block = 1
        last_block = b''

        while True:
            start_byte = read_exact(ser, 1)
            if not start_byte:
                continue

            if start_byte == bytes([SOH]):
                print(f"SOH odebrany. Oczekuję blok #{expected_block}")
                block_header = read_exact(ser, 2)
                if len(block_header) < 2:
                    print("Niepełny nagłówek bloku.")
                    continue

                block_num, block_neg = block_header
                print(f"Nagłówek bloku: num={block_num}, neg={block_neg}")

                data = read_exact(ser, BLOCK_SIZE)
                if len(data) < BLOCK_SIZE:
                    print("Niepełny blok danych. Wysyłam NAK.")
                    ser.write(bytes([NAK]))
                    continue

                if use_crc:
                    footer = read_exact(ser, 2)
                    if len(footer) < 2:
                        print("Niepełny CRC.")
                        ser.write(bytes([NAK]))
                        continue
                    recv_crc = int.from_bytes(footer, 'big')
                    calc = calc_crc(data)
                    print(f"CRC: otrzymany={recv_crc}, wyliczony={calc}")
                    if calc != recv_crc:
                        print("CRC niezgodne. Wysyłam NAK.")
                        ser.write(bytes([NAK]))
                        continue
                else:
                    footer = read_exact(ser, 1)
                    if len(footer) < 1:
                        print("Niepełna suma kontrolna.")
                        ser.write(bytes([NAK]))
                        continue
                    recv_sum = footer[0]
                    calc = calc_checksum(data)
                    print(f"Checksum: otrzymany={recv_sum}, wyliczony={calc}")
                    if calc != recv_sum:
                        print("Checksum niezgodna. Wysyłam NAK.")
                        ser.write(bytes([NAK]))
                        continue

                if block_num == expected_block:
                    f.write(data)
                    last_block = data
                    ser.write(bytes([ACK]))
                    print(f"Blok {block_num} OK. Wysłano ACK.")
                    expected_block += 1
                elif block_num == expected_block - 1:
                    if data == last_block:
                        ser.write(bytes([ACK]))
                        print(f"Retransmisja bloku {block_num}. ACK.")
                    else:
                        ser.write(bytes([NAK]))
                        print(f"Retransmisja z błędną zawartością. NAK.")
                else:
                    ser.write(bytes([NAK]))
                    print(f"Nieoczekiwany numer bloku {block_num}. Oczekiwałem {expected_block}. Wysyłam NAK.")

            elif start_byte == bytes([EOT]):
                print("Odebrano EOT. Wysyłam ACK i kończę transmisję.")
                ser.write(bytes([ACK]))
                break

            else:
                print(f"Nieznany bajt startowy: {start_byte}")
