from pyvit import can
from pyvit.hw import peak
from pyvit.hw import socketcan

dev = socketcan.SocketCanDev("vcan0")

dev.start()

frame = can.Frame(0)
frame.data = [0] * 8

while True:
    dev.send(frame)
