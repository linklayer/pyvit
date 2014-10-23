import os
import struct
import socket
import time

from .. import can
from .socketcan import SocketCanDev

class PcanDev(SocketCanDev):
    def __init__(self, minor_number=32, ndev="can0"):
        SocketCanDev.__init__(self, ndev=ndev)
        self.device_filename = "/dev/pcan%d" % minor_number

    def _write_to_chardev(self, string):
        os.system("echo '%s' > %s" % (string, self.device_filename))

    def set_btr(self, value):
        self._write_to_chardev('i 0x%X e' % value)
