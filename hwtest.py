from canard import can
from canard.hw import peak

d = peak.Pcan()

# set device to 125 kHz
d.set_btr(0x031c)

f = can.Frame(0x100)
f.dlc=4
f.data=[1,2,3,4]

print('reading')
print(d.read())
print('writing')
d.write(f)

