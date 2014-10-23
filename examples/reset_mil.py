from canard import can
from canard.hw import peak
from canard.hw import socketcan

#dev = peak.PcanDev()
dev = socketcan.SocketCanDev("vcan0")

dev.start()

frame = can.Frame(0x7DF)
frame.dlc = 8

# frame data
# byte 0: number of additional bytes (1)
# byte 1: mode. mode 04 clears MIL
# other bytes not used, set to 0x55
frame.data = [1, 4, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55]

dev.send(frame)
