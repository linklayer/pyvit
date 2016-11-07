from pyvit import can
from pyvit.hw import cantact
from pyvit.utils.queue import CanQueue
import sys

dev = cantact.CantactDev(sys.argv[1])
dev.set_bitrate(125000)
cq = CanQueue(dev)

cq.start()

print cq.recv()

req = can.Frame(0x6A5)
req.data = [0x10, 0xFF, 0xFF]

cq.send(req)

print cq.recv(arb_id=0x625, timeout=10)

cq.stop()
