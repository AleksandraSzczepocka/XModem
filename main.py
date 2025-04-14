import serial
import sys
from sender import send_file
from receiver import receive_file

def setup_serial(port: str, baudrate=9600) -> serial.Serial:
    return serial.Serial(port, baudrate=baudrate, timeout=5)

def main():
    if len(sys.argv) < 4:
        print("Usage:")
        print("  python main.py send COMx filename [crc|sum]")
        print("  python main.py receive COMx filename")
        return

    mode = sys.argv[1]
    port = sys.argv[2]
    filename = sys.argv[3]
    ser = setup_serial(port)

    if mode == 'send':
        use_crc = False  # domyślnie suma kontrolna
        if len(sys.argv) >= 5:
            method = sys.argv[4].lower()
            if method == "crc":
                use_crc = True
            elif method == "sum":
                use_crc = False
            else:
                print("Unknown checksum method. Use 'crc' or 'sum'.")
                return
        send_file(ser, filename, use_crc)

    elif mode == 'receive':
        receive_file(ser, filename)

    else:
        print("Unknown mode. Use 'send' or 'receive'.")

if __name__ == "__main__":
    main()
