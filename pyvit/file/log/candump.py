import re

from pyvit import can


class CandumpFile:
    def __init__(self, filename):
        self.filename = filename

    def _str_to_frame(self, string):
        # split by whitespace
        fields = re.split('\s+', string)
        # arb_id is the part before '#' in the 3rd field, represented as hex
        arb_id = int(fields[2].split('#')[0], 16)
        # the data strig follows the '#'
        datastr = fields[2].split('#')[1]

        # iterate over the data string and collect the bytes
        data = []
        for i in range(0, len(datastr)):
            if i % 2 == 0:
                data.append(int(datastr[i:i+2], 16))

        # assemble the frame
        return can.Frame(arb_id, data=data)

    def _frame_to_str(self, frame):
        string = ''

        # insert timestamp if set
        if frame.timestamp:
            string += '(%f) ' % frame.timestamp
        else:
            string += '(0.0) '

        # insert interface if set
        if frame.interface:
            string += '%s ' % frame.interface
        else:
            string += 'can0 '

        # add ID and '#' character
        string += ('%03X' % frame.arb_id) + '#'

        # add data
        for b in frame.data:
            string += '%02X' % b

        string += '\n'
        return string

    def import_frames(self):
        frames = []
        with open(self.filename, 'r') as f:
            for line in f.readlines():
                frames.append(self._str_to_frame(line))
        return frames

    def export_frames(self, frames):
        with open(self.filename, 'w') as f:
            for frame in frames:
                f.write(self._frame_to_str(frame))
