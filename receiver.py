from protocol import *
import time


def receive_file(serial_port, mode):
    print("Nasłuchiwanie nadawcy...")
    start_time = time.time()
    data = bytearray()

    while time.time() - start_time < 60:
        serial_port.write(bytes([C if mode == CRC16 else NAK]))
        if serial_port.in_waiting:
            if serial_port.read() == bytes([SOH]):
                break
        time.sleep(0.1)
    else:
        raise TimeoutError("Nie znaleziono nadawcy")

    while True:
        block_number = serial_port.read()[0]
        _ = serial_port.read()  # ignored complement
        block = serial_port.read(128)

        if mode == ALGEBRAIC_CHECKSUM:
            received_checksum = serial_port.read()[0]
            if algebraic_checksum(block) == received_checksum:
                serial_port.write(bytes([ACK]))
                data.extend(block)
            else:
                serial_port.write(bytes([NAK]))
                continue
        else:
            received_crc = serial_port.read(2)
            if received_crc == crc16_checksum(block):
                serial_port.write(bytes([ACK]))
                data.extend(block)
            else:
                serial_port.write(bytes([NAK]))
                continue

        next_byte = serial_port.read()
        if next_byte == bytes([EOT]):
            serial_port.write(bytes([ACK]))
            break
        elif next_byte != bytes([SOH]):
            raise Exception("Protocol error!")

    # Usuń końcowe NULL-e (0x00)
    while data and data[-1] == 0x00:
        data.pop()

    print("Odebrano plik".format(len(data)))
    return data
