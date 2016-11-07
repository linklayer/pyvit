import sys

from pyvit.proto.uds import UdsInterface
from pyvit.hw.cantact import CantactDev

d = CantactDev(sys.argv[1])
d.set_bitrate(500000)
d.start()

p = UdsInterface(d)

# DiagnosticSessionControl Discovery
for i in range(0x700, 0x800):
    # attempt to enter diagnostic session
    resp = p.uds_request(i, 0x10, [0x1], timeout=0.2)
    if resp is not None:
        print("ECU response for ID 0x%X!" % i)
