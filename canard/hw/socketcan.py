import os
import struct
import socket
import time

from .. import can

class SocketCanDev:
    def __init__(self, ndev):
        self.running = False
        self.socket = socket.socket(socket.PF_CAN, socket.SOCK_RAW,
                                    socket.CAN_RAW)
        self.ndev = ndev

    def start(self):
        self.socket.bind((self.ndev,))
        self.start_time = time.time()
        self.running = True

    def recv(self):
        assert self.running, 'device not running'
        frame_format = "=IB3xBBBBBBBB"
        frame_size = struct.calcsize(frame_format)

        frame_raw = self.socket.recv(frame_size)
        id, dlc, d0, d1, d2, d3, d4, d5, d6, d7 = struct.unpack(frame_format,
                                                                frame_raw)

        frame = can.Frame(id)
        frame.dlc = dlc
        frame.data = [d0,d1,d2,d3,d4,d5,d6,d7]
        frame.timestamp = time.time() - self.start_time

        return frame

    def send(self, frame):
        assert self.running, 'device not running'
        frame_format = "=IBBBBBBBBBBBB"

        data = frame.data
        packet = struct.pack(frame_format, frame.id, frame.dlc,
                    0xff, 0xff, 0xff, data[0], data[1], data[2], data[3], 
                    data[4], data[5], data[6], data[7])
        self.socket.send(packet)
