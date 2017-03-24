from . import can
import time


class Logger:
    def __init__(self, filename, if_name='can0'):
        self.if_name = if_name
        self.filename = filename
        self.started = False

    def start(self):
        self.start_timestamp = time.time()
        self.started = True
        self._file = open(self.filename, 'w')

    def __enter__(self):
        self.start()
        return self

    def stop(self):
        self.started = False
        self._file.close()

    def __exit__(self, exception_type, exception_value, traceback):
        self.stop()

    def log_frame(self, frame):
        assert isinstance(frame, can.Frame), 'invalid frame'

        if not self.started:
            raise Exception('logger not started')

        ts = time.time() - self.start_timestamp

        line = ("(%f) %s %03X#%02X%02X%02X%02X%02X%02X%02X%02X\n" %
                (ts,
                 self.if_name,
                 frame.arb_id,
                 frame.data[0],
                 frame.data[1],
                 frame.data[2],
                 frame.data[3],
                 frame.data[4],
                 frame.data[5],
                 frame.data[6],
                 frame.data[7]))
        self._file.write(line)

    def clear(self):
        self._buffer = []
