import sys

from canard.proto.uds import UdsInterface
from canard.hw.socketcan import SocketCanDev

d = SocketCanDev('vcan0')
d.start()

p = UdsInterface(d)

# DiagnosticSessionControl Discovery
for i in range(0x700, 0x800):
    # attempt to enter diagnostic session
    resp = p.uds_request(i, 0x10, [0x1], timeout=0.2)
    if resp != None:
        print("ECU response for ID 0x%X!" % i)
