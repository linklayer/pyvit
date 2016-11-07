from pyvit import can, bus
from pyvit.file import jsondb
from pyvit.hw import socketcan

parser = jsondb.JsonDbParser()
b = parser.parse('examples/example_db.json')

dev = socketcan.SocketCanDev('vcan0')
dev.start()

while True:
    frame = dev.recv()
    signals = b.parse_frame(frame)
    if signals:
        for s in signals:
            print(s)
