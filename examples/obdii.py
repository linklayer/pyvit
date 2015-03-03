from canard.proto.obdii import ObdInterface

from canard.hw.cantact import CantactDev
from canard.hw.loopback import LoopbackDev
import sys

#d = LoopbackDev()
d = CantactDev(sys.argv[1])
p = ObdInterface(d)

# read engine RPM
# mode 1, PID 0x0C
print(p.send_request(0x7E8, 1, 0x0C))

