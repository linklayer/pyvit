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
req.dlc = 8
req.data = [0x10,0xFF, 0xFF]

cq.send(req)

print cq.recv(filter=0x625, timeout=10)

cq.stop()

#dev.stop()
#dev.ser.write('S0\r')
#dev.start()

#while True:
#    frame = can.Frame(0x10)
#    frame.dlc=3
#    frame.data = [1,2,3]
#    dev.send(frame)
#    time.sleep(0.5)
