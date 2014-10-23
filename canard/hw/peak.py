import os
from .. import can

class Pcan:
    def __init__(self, minor_number)
        self.device_filename = "/dev/pcan%d" % minor_number

    def _write_to_device(self, string):
        os.system("echo '%s' > %s" % string, self.device_filename)

