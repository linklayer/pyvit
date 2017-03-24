import time
from .. import can


class LogPlayer:
    running = False

    def __init__(self, log_filename, realtime=True):
        self.log_filename = log_filename
        self.realtime = realtime

    def start(self):
        assert not self.running, 'cannot start, already running'

        self.logfile = open(self.log_filename, 'r')
        self.start_timestamp = None
        self.running = True

    def __enter__(self):
        self.start()
        return self

    def stop(self):
        self.running = False
        self.logfile.close()

    def __exit__(self, exception_type, exception_value, traceback):
        self.stop()

    def send(self, data):
        pass

    def recv(self):
        assert self.running, 'not running'

        line = self.logfile.readline()
        if line == '':
            # out of frames, cause a timeout
            while True:
                pass

        # convert line to frame
        frame = self._log_to_frame(line)

        # make the first frame's timestamp now
        if self.start_timestamp is None:
            self.start_timestamp = time.time() - frame.timestamp
        # sleep until message occurs
        if self.realtime:
            time.sleep(max((self.start_timestamp - time.time() +
                            frame.timestamp), 0))

        return frame

    def recv_all(self):
        frames = []

        line = self.logfile.readline()
        while line != '':
            frame = self._log_to_frame(line)
            frames.append(frame)
            line = self.logfile.readline()

        return frames

    def _log_to_frame(self, line):
        fields = line.split(' ')

        arb_id = int(fields[2].split('#')[0], 16)
        frame = can.Frame(arb_id)

        frame.timestamp = float(fields[0][1:-1])

        datastr = fields[2].split('#')[1]
        dlc = int(len(datastr) / 2)

        frame.data = []
        for i in range(0, dlc):
            frame.data.append(int(datastr[i*2:i*2+2], 16))

        return frame
