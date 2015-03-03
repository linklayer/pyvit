from canard import can
from canard.hw import cantact
import time
import sys
dev = cantact.CantactDev(sys.argv[1])

dev.stop()
dev.ser.write('S0\r')
dev.start()

while True:
    frame = can.Frame(0x10)
    frame.dlc=3
    frame.data = [1,2,3]
    dev.send(frame)
    time.sleep(0.5)
