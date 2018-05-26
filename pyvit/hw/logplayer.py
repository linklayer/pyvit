import time
from .. import can


class LogPlayer:
    running = False
    debug = False

    def __init__(self, log_filename, realtime=True):
        self.log_filename = log_filename
        self.realtime = realtime

    def start(self):
        assert not self.running, 'cannot start, already running'

        self.logfile = open(self.log_filename, 'r')
        self.start_timestamp = None
        self.running = True
        self.linenumber = 0

    def __enter__(self):
        self.start()
        return self

    def stop(self):
        self.running = False
        self.logfile.close()

    def __exit__(self, exception_type, exception_value, traceback):
        self.stop()

    def send(self, data):
        if self.debug:
            print("DEV SEND: %s " % data)

    def recv(self):
        assert self.running, 'not running'

        line = self.logfile.readline()
        self.linenumber = self.linenumber + 1
        if line == '':
            # out of frames
            return None
        if line in ['\n','\n\r']:
            # seams to be an empty line, just go for next one
            return self.recv()

        # convert line to frame
        frame = self._log_to_frame(line)

        # make the first frame's timestamp now
        if self.start_timestamp is None:
            self.start_timestamp = time.time() - frame.timestamp
        # sleep until message occurs
        if self.realtime:
            time.sleep(max((self.start_timestamp - time.time() +
                            frame.timestamp), 0))
        if self.debug:
            print("DEV RECV: %s " % frame)
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

        arb_id_str = fields[2].split('#')[0]
        arb_id = int(arb_id_str, 16)

        extended_id = len(arb_id_str)>3
        frame = can.Frame(arb_id,extended=extended_id)

        frame.timestamp = float(fields[0][1:-1])

        datastr = fields[2].split('#')[1]
        dlc = int(len(datastr) / 2)

        frame.data = []
        for i in range(0, dlc):
            frame.data.append(int(datastr[i*2:i*2+2], 16))

        return frame

    def set_bitrate(self,value):
        pass