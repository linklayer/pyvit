from pyvit.hw.socketcan import SocketCanDev
from pyvit import can

d = SocketCanDev('vcan0')
d.start()

while True:
    frame = d.recv()
    if frame.arb_id == 0x705:
        resp = can.Frame(0x725)
        resp.data = [0x02, 0x41]
        d.send(resp)
