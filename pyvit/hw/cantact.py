import serial

from .. import can


class CantactDev:
    def __init__(self, port):
        self.ser = serial.Serial(port)

    def _dev_write(self, string):
        self.ser.write(bytes(string, encoding='ascii'))

    def start(self):
        self._dev_write('O\r')

    def stop(self):
        self._dev_write('C\r')

    def set_bitrate(self, bitrate):
        if bitrate == 10000:
            self._dev_write('S0\r')
        elif bitrate == 20000:
            self._dev_write('S1\r')
        elif bitrate == 50000:
            self._dev_write('S2\r')
        elif bitrate == 100000:
            self._dev_write('S3\r')
        elif bitrate == 125000:
            self._dev_write('S4\r')
        elif bitrate == 250000:
            self._dev_write('S5\r')
        elif bitrate == 500000:
            self._dev_write('S6\r')
        elif bitrate == 750000:
            self._dev_write('S7\r')
        elif bitrate == 1000000:
            self._dev_write('S8\r')
        else:
            raise ValueError("Bitrate not supported")

    def recv(self):
        # receive characters until a newline (\r) is hit
        rx_str = ""
        while rx_str == "" or rx_str[-1] != '\r':
            rx_str = rx_str + self.ser.read().decode('ascii')

        # parse the id, create a frame
        arb_id = int(rx_str[1:4], 16)
        frame = can.Frame(arb_id)

        # parse the DLC
        dlc = int(rx_str[4])

        # parse the data bytes
        data = []
        for i in range(0, dlc):
            data.append(int(rx_str[5+i*2:7+i*2], 16))
            frame.data = data

        return frame

    def send(self, frame):
        # add type, id, and dlc to string
        tx_str = "%s%03X%d" % ('t', frame.arb_id, frame.dlc)

        # add data bytes to string
        for i in range(0, frame.dlc):
            tx_str = tx_str + ("%02X" % frame.data[i])

        # add newline (\r) to string
        tx_str = tx_str + '\r'

        # send it
        self._dev_write(tx_str)
