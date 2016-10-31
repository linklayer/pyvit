from canard import can
from canard.hw import cantact
from canard.utils.queue import CanQueue
import time
import sys

dev = cantact.CantactDev(sys.argv[1])
dev.set_bitrate(125000)
cq = CanQueue(dev)

cq.start()

print cq.recv()

req = can.Frame(0x6A5)
req.data = [0x10, 0xFF, 0xFF]

cq.send(req)

print cq.recv(filter=0x625, timeout=10)

cq.stop()
