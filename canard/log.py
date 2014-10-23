from . import can

class Logger:
    def __init__(self):
        self._buffer = []

    def log(self, frame):
        assert isinstance(frame, can.Frame), 'invalid frame'

        if frame.frame_type == can.FrameType.DataFrame:
            type_char = "D"
        elif frame.frame_type == can.FrameType.RemoteFrame:
            type_char = "R"
        elif frame.frame_type == can.FrameType.ErrorFrame:
            type_char = "E"
        elif frame.frame_type == can.FrameType.OverloadFrame:
            type_char = "O"

        line = ("%f 0x%X %s %d 0x%X 0x%X 0x%X 0x%X 0x%X 0x%X 0x%X 0x%X\n" %
               (frame.timestamp, frame.id, type_char, frame.dlc, frame.data[0],
                frame.data[1], frame.data[2], frame.data[3], frame.data[4],
                frame.data[5], frame.data[6], frame.data[7]))
        self._buffer.append(line)

    def __str__(self):
        s = ""
        for line in self._buffer:
            s = s + line
        return s

    def write_file(self, filename):
        with open(filename, 'w') as logfile:
            logfile.writelines(self._buffer)

    def clear(self):
        self._buffer = []
