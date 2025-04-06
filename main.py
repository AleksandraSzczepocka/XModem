from transmitter import send_file
from receiver import receive_file
from protocol import *
import serial

def main():
    port_name = input("Podaj nazwę portu COM (np. COM3): ")
    working_mode = int(input("Wybierz tryb pracy:\n0) wysyłanie\n1) odbieranie\n"))
    checksum_mode = int(input("Wybierz tryb sumy kontrolnej:\n0) algebraiczna\n1) CRC16\n"))

    with serial.Serial(port=port_name, baudrate=9600, timeout=1) as ser:
        if working_mode == 0:
            path = input("Podaj ścieżkę do pliku: ")
            with open(path, "rb") as f:
                file_data = f.read()
            send_file(ser, file_data, checksum_mode)

        else:
            out_path = input("Podaj nazwę pliku do zapisania: ")
            file_data = receive_file(ser, checksum_mode)
            with open(out_path, "wb") as f:
                f.write(file_data)

if __name__ == "__main__":
    main()
