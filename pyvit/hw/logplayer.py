import time
from .. import can


class LogPlayer:
    running = False

    def __init__(self, log_filename):
        self.logfile = open(log_filename, 'r')

    def start(self):
        assert not self.running, 'cannot start, already running'
        self.start_timestamp = time.time()
        self.running = True

    def recv(self):
        assert self.running, 'not running'
        line = self.logfile.readline()
        if line == '':
            return None

        # convert line to frame
        frame = self._log_to_frame(line)

        # sleep until message occurs
        time.sleep(max((self.start_timestamp - time.time() + frame.timestamp),
                   0))

        return frame

    def _log_to_frame(self, line):
        fields = line.split(' ')

        arb_id = int(fields[1], 0)
        frame = can.Frame(arb_id)

        frame.timestamp = float(fields[0])

        if fields[2].upper() == 'D':
            frame.frame_type = can.FrameType.DataFrame
        elif fields[2].upper() == 'R':
            frame.frame_type = can.FrameType.RemoteFrame
        elif fields[2].upper() == 'E':
            frame.frame_type = can.FrameType.ErrorFrame
        elif fields[2].upper() == 'O':
            frame.frame_type = can.FrameType.OverloadFrame
        else:
            raise ValueError('invalid frame type')

        dlc = int(fields[3])
        frame.data = []
        for i in range(0, dlc):
            frame.data.append(int(fields[i+4], 0))

        return frame
