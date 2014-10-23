from canard import can
from canard.hw import peak

d = peak.Pcan(32)

d.set_btr(0x031c)

f = can.Frame(0x100)

d.write_frame(f)

f = open(d.device_filename, 'r')
f.readline()
