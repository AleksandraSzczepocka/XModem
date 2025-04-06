from protocol import *

def send_file(serial_port, file_bytes, mode):
    print("Czekam na odbiornik...")

    while True:
        c = serial_port.read()
        print(f"Received byte: {c}")  # Logowanie odebranego bajtu
        if c == b'':
            continue  # Ignorowanie pustych bajtów
        if (mode == ALGEBRAIC_CHECKSUM and c == bytes([NAK])) or \
           (mode == CRC16 and c == bytes([C])):
            print("Odbiornik gotowy, rozpoczynamy wysyłanie.")
            break
        else:
            print(f"❌ Nieoczekiwany bajt: {c}, oczekiwano NAK lub C")

    no_of_blocks = math.ceil(len(file_bytes) / 128)

    for i in range(no_of_blocks):
        block = file_bytes[i * 128: (i + 1) * 128]
        block += bytes([0] * (128 - len(block)))  # Pad z zerami do pełnych 128 bajtów
        block_number = (i + 1) & 0xFF
        header = bytes([SOH, block_number, 255 - block_number])
        serial_port.write(header + block)

        # Wysyłanie sumy kontrolnej
        if mode == ALGEBRAIC_CHECKSUM:
            checksum = algebraic_checksum(block)
            serial_port.write(bytes([checksum]))
        else:
            crc = crc16_checksum(block)
            serial_port.write(crc)

        # Czekamy na odpowiedź
        response = serial_port.read()
        print(f"Received response: {response}")  # Logowanie odpowiedzi
        if response == bytes([NAK]):
            print(f"❌ NAK odebrany, powtarzam blok {i+1}")
            i -= 1  # Powtarzamy ten sam blok
        elif response == bytes([CAN]):
            raise Exception("Connection canceled!")
        elif response == bytes([ACK]):
            print(f"✅ ACK odebrany, blok {i+1} wysłany poprawnie.")
        else:
            print(f"⚠️ Nieoczekiwana odpowiedź: {response}")
            raise Exception("Protocol error!")

    # Wysyłanie EOT (koniec transmisji)
    serial_port.write(bytes([EOT]))
    print("Plik wysłany.")
