# from pyvit import can
# from pyvit.hw.cantact import CantactDev

from pyvit.hw import cantact

dev = cantact.CantactDev("/dev/tty.usbmodemFA131")
dev.set_bitrate(500000)

dev.start()
while True:
      print(dev.recv())
