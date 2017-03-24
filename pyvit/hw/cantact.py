import serial

from .. import can


class CantactDev:
    def __init__(self, port):
        self.ser = serial.Serial(port)

    def _dev_write(self, string):
        self.ser.write(string.encode())

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

        # check frame type
        if rx_str[0] == 'T':
            ext_id = True
            remote = False
        elif rx_str[0] == 't':
            ext_id = False
            remote = False
        elif rx_str[0] == 'R':
            ext_id = True
            remote = True
        elif rx_str[0] == 'r':
            ext_id = False
            remote = True

        # parse the id and DLC
        if ext_id:
            arb_id = int(rx_str[1:9], 16)
            dlc = int(rx_str[9])
            data_offset = 10
        else:
            arb_id = int(rx_str[1:4], 16)
            dlc = int(rx_str[4])
            data_offset = 5

        # create the frame
        frame = can.Frame(arb_id)
        if remote:
            frame.frame_type = can.FrameType.RemoteFrame

        # parse the data bytes
        data = []
        for i in range(0, dlc):
            data.append(int(rx_str[data_offset+i*2:7+i*2], 16))
            frame.data = data

        return frame

    def send(self, frame):
        # add type, id, and dlc to string
        if frame.is_extended_id:
            tx_str = "T%08X%d" % (frame.arb_id, frame.dlc)
        else:
            tx_str = "t%03X%d" % (frame.arb_id, frame.dlc)

        # add data bytes to string
        for i in range(0, frame.dlc):
            tx_str = tx_str + ("%02X" % frame.data[i])

        # add newline (\r) to string
        tx_str = tx_str + '\r'

        # send it
        self._dev_write(tx_str)

    def set_filter_id(self, filter_id):
        # set CAN filter identifier
        self._dev_write('F%X\r' % filter_id)

    def set_filter_mask(self, filter_mask):
        # set CAN filter mask
        self._dev_write('K%X\r' % filter_mask)
