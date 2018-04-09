import serial

from .. import can


class CantactDev:
    debug = False

    def __init__(self, port):
        # opening the serial connection with the device in attribute ser
        self.ser = serial.Serial(port)

    def _dev_write(self, string):
        self.ser.write(string.encode())

    def start(self):
        # activate CANtact standard operations
        self._dev_write('O\r')
        if self.debug:
            print("CantactDev started")

    def stop(self):
        # terminates CANtact standard operations
        self._dev_write('C\r')
        if self.debug:
            print("CantactDev stopped")

    def set_bitrate(self, bitrate):
        # set the CAN bus bitrate
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
        elif bitrate == 83000:
            self._dev_write('S9\r')
        elif bitrate == 800000:
            self._dev_write('Sa\r')
        elif bitrate == 0:
            self._dev_write('Su\r')
        else:
            raise ValueError("Bitrate not supported")

    def recv(self):
        # receive characters until a newline (\r) is hit
        rx_str = ""
        if self.debug:
            print("CantactDev recv called")
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
        else:
            # If I read somthing meaningless read next packet
            return self.recv()

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
        frame = can.Frame(arb_id, extended=ext_id)
        if remote:
            frame.frame_type = can.FrameType.RemoteFrame

        # parse the data bytes
        data = []
        for i in range(0, dlc):
            data.append(int(rx_str[data_offset+i*2:(data_offset+2)+i*2], 16))
            frame.data = data

        if self.debug:
            print("RECV: %s" % frame)
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
        if self.debug:
            print("SENT: %s" % frame)

    def set_filter_id(self, filter_id):
        # set CAN filter identifier
        self._dev_write('F%X\r' % filter_id)

    def set_filter_mask(self, filter_mask):
        # set CAN filter mask
        self._dev_write('K%X\r' % filter_mask)
