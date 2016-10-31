from canard import can
from canard.hw import peak
from canard.hw import socketcan

dev = socketcan.SocketCanDev("vcan0")

dev.start()

frame = can.Frame(0)
frame.data = [0] * 8

while True:
    dev.send(frame)
