import os
from .. import can

class Pcan:
    def __init__(self, minor_number):
        self.device_filename = "/dev/pcan%d" % minor_number

    def _write_to_device(self, string):
        os.system("echo '%s' > %s" % (string, self.device_filename))

    def set_btr(self, value):
        self._write_to_device('i 0x%X e' % value)

    def write_frame(self, frame):
        # message string
        s = "m "

        # standard or extended frame
        if frame.is_extended_id:
            s = s + "e "
        else:
            s = s + "s "

        # frame identifier
        s = s + "0x%X " % frame.id

        # length of frame (dlc)
        s = s + "%d " % frame.dlc

        # data
        for i in range(0, frame.dlc):
            s = s + "0x%X " % frame.data[i]

        self._write_to_device(s)
