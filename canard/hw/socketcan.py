import struct
import socket
import time

from .. import can


class SocketCanDev:
    def __init__(self, ndev):
        self.running = False

        try:
            socket.PF_CAN
            socket.CAN_RAW
        except:
            print("Python 3.3 or later is needed for native SocketCan")
            raise SystemExit(1)

        self.socket = socket.socket(socket.PF_CAN, socket.SOCK_RAW,
                                    socket.CAN_RAW)
        self.ndev = ndev

    def start(self):
        self.socket.bind((self.ndev,))
        self.start_time = time.time()
        self.running = True

    def stop(self):
        pass

    def recv(self):
        assert self.running, 'device not running'
        frame_format = "=IB3xBBBBBBBB"
        frame_size = struct.calcsize(frame_format)

        frame_raw = self.socket.recv(frame_size)
        id_, dlc, d0, d1, d2, d3, d4, d5, d6, d7 = struct.unpack(frame_format,
                                                                 frame_raw)

        # adjust the id and set the extended id flag
        is_extended = False
        if id_ & 0x80000000:
            id_ &= 0x7FFFFFFF
            is_extended = True

        frame = can.Frame(id_, is_extended_id=is_extended)
        # select the data bytes up to the DLC value
        frame.data = [d0, d1, d2, d3, d4, d5, d6, d7][0:dlc]
        frame.timestamp = time.time() - self.start_time

        return frame

    def send(self, frame):
        assert self.running, 'device not running'
        frame_format = "=IBBBBBBBBBBBB"

        # set the extended bit if a extended id is used
        id_ = frame.id
        if frame.is_extended_id:
            id_ |= 0x80000000

        data = frame.data
        packet = struct.pack(frame_format, id_, frame.dlc, 0xff, 0xff, 0xff,
                             data[0], data[1], data[2], data[3],
                             data[4], data[5], data[6], data[7])
        self.socket.send(packet)
