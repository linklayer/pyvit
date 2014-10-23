import Queue, threading, time
from .. import can

class LogPlayer:
    running = False
    def __init__(self, log_filename):
        self.logfile = open(log_filename, 'r')
        self.recv_queue = Queue.Queue()
        self.send_queue = Queue.Queue()

    def start(self):
        assert not self.running, 'cannot start, already running'
        self.thread = threading.Thread(target=self.task)
        self.thread.daemon = True
        self.thread.start()

    def task(self):
        last_timestamp = 0
        for line in self.logfile:
            # convert line to frame
            frame = self._log_to_frame(line)

            # sleep until message occurs
            time.sleep(frame.timestamp - last_timestamp)
            last_timestamp = frame.timestamp

            # place message into queue
            self.recv_queue.put(frame)
        self.recv_queue.task_done()

    def _log_to_frame(self, line):
        fields = line.split(' ')

        id = int(fields[1], 0)
        frame = can.Frame(id)

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

        frame.dlc = int(fields[3])
        data = [int(fields[4], 0), int(fields[5], 0), int(fields[6], 0),
                int(fields[7], 0), int(fields[8], 0), int(fields[9], 0),
                int(fields[10], 0), int(fields[11], 0)]
        frame.data = data

        return frame
