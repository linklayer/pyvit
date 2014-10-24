from canard import can, bus
from canard.file import jsondb
from canard.hw import socketcan

parser = jsondb.JsonDbParser()
b = parser.parse('example_db.json')

dev = socketcan.SocketCanDev('vcan0')
dev.start()

while True:
    frame = dev.recv()
    signals = b.parse_frame(frame)
    for s in signals:
        print(s)

f = can.Frame(0x100)
f.dlc = 8
f.data = [1, 2, 0x81, 4, 5]

for s in b.parse_frame(f):
    print(s)
