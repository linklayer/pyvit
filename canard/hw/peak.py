import os
import struct
import socket
from .. import can

class Pcan:
    def __init__(self, minor_number=32, ndev="can0"):
        self.device_filename = "/dev/pcan%d" % minor_number
        self.socket = socket.socket(socket.PF_CAN, socket.SOCK_RAW,
                                    socket.CAN_RAW)
        self.ndev = ndev

    def start(self):
        self.socket.bind((self.ndev,))

    def _write_to_chardev(self, string):
        os.system("echo '%s' > %s" % (string, self.device_filename))

    def set_btr(self, value):
        self._write_to_chardev('i 0x%X e' % value)

    def read(self):
        frame_format = "=IB3xBBBBBBBB"
        frame_size = struct.calcsize(frame_format)

        frame_raw, addr = self.socket.recvfrom(frame_size)
        id, dlc, d0, d1, d2, d3, d4, d5, d6, d7 = struct.unpack(frame_format,
                                                                frame_raw)

        frame = can.Frame(id)
        frame.dlc = dlc
        frame.data = [d0,d1,d2,d3,d4,d5,d6,d7]
        return frame

    def write(self, frame):
        frame_format = "=IB3xBBBBBBBB"

        # convert None values into zeros
        data = []
        for b in frame.data:
            if b == None:
                data.append(0)
            else:
                data.append(b)

        packet = struct.pack(frame_format, frame.id, frame.dlc, data[0],
                    data[1], data[2], data[3], data[4], data[5], data[6], 
                    data[7])
        self.socket.sendto(packet, self.ndev)

