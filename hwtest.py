from canard import can
from canard import log
from canard.hw import peak

d = peak.Pcan()

# set device to 125 kHz
d.set_btr(0x031c)

f = can.Frame(0x200)
f.dlc=8
f.data=[1,2,3,4,5]

d.start()

d.send(f)

logger = log.Logger()
while True:
    rf = d.recv()
    logger.log(rf)
    logger.write_file('test.log')
