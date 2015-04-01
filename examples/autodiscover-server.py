import sys

from canard.proto.uds import UdsInterface
from canard.hw.socketcan import SocketCanDev
from canard import can

d = SocketCanDev('vcan0')
d.start()

while True:
    frame = d.recv()
    if frame.id == 0x705:
        resp = can.Frame(0x725)
        resp.dlc = 8
        resp.data = [0x02, 0x41]
        d.send(resp)



