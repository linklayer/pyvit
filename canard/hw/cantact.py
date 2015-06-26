import serial
import io

from .. import can

class CantactDev:
    def __init__(self, port):
        self.ser = serial.Serial(port)

    def start(self):
        self.ser.write('O\r')

    def stop(self):
        self.ser.write('C\r')

    def set_bitrate(self, bitrate):
        if bitrate == 10000:
            self.ser.write('S0\r')
        elif bitrate == 20000:
            self.ser.write('S1\r')
        elif bitrate == 50000:
            self.ser.write('S2\r')
        elif bitrate == 100000:
            self.ser.write('S3\r')
        elif bitrate == 125000:
            self.ser.write('S4\r')
        elif bitrate == 250000:
            self.ser.write('S5\r')
        elif bitrate == 500000:
            self.ser.write('S6\r')
        elif bitrate == 750000:
            self.ser.write('S7\r')
        elif bitrate == 1000000:
            self.ser.write('S8\r')
        else:
            raise ValueError("Bitrate not supported")

    def recv(self):
        # receive characters until a newline (\r) is hit
        rx_str = ""
        while rx_str == "" or rx_str[-1] != '\r':
            rx_str = rx_str + self.ser.read()

        # parse the id, create a frame
        frame_id = int(rx_str[1:4], 16)
        frame = can.Frame(frame_id)

        # parse the DLC
        frame.dlc = int(rx_str[4])

        # parse the data bytes
        data = []
        for i in range(0, frame.dlc):
            data.append(int(rx_str[5+i*2:7+i*2], 16))
            frame.data = data

        return frame

    def send(self, frame):
        # add type, id, and dlc to string
        tx_str = "%s%03X%d" % ('t', frame.id, frame.dlc)

        # add data bytes to string
        for i in range(0, frame.dlc):
            tx_str = tx_str + ("%02X" % frame.data[i])

        # add newline (\r) to string
        tx_str = tx_str + '\r'

        # send it
        self.ser.write(tx_str)
