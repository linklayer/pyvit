import sys

from pyvit.proto.obdii import ObdInterface
from pyvit.hw.cantact import CantactDev
from pyvit.dispatch import Dispatcher

if len(sys.argv) != 3:
    print("usage: %s [CANtact device] [PID]" % sys.argv[0])
    sys.exit(1)

# set up a CANtact device
dev = CantactDev(sys.argv[1])
dev.set_bitrate(500000)

# create our dispatcher and OBD interface
disp = Dispatcher(dev)
obd = ObdInterface(disp)

# setting debug to true will print all frames sent and received
obd.debug = True
disp.start()

# read the PID given using OBD mode 1
pid = int(sys.argv[2], 0)
print("OBD response:", obd.obd_request(1, pid))

disp.stop()
