import multiprocessing

try:
    import queue
except ImportError:
    import Queue as queue

import time


class CanQueue:
    def __init__(self, can_dev):
        self.can_dev = can_dev
        self.recv_process = multiprocessing.Process(target=self.recv_task)
        self.send_process = multiprocessing.Process(target=self.send_task)
        self.recv_queue = multiprocessing.Queue()
        self.send_queue = multiprocessing.Queue()

    def start(self):
        self.can_dev.start()
        self.recv_process.start()
        self.send_process.start()

    def stop(self):
        self.recv_process.terminate()
        self.send_process.terminate()
        self.can_dev.stop()

    def send(self, msg):
        self.send_queue.put(msg)

    def recv(self, timeout=1, arb_id=None):
        try:
            start_time = time.time()
            while True:
                msg = self.recv_queue.get(timeout=timeout)
                if not arb_id:
                    return msg
                elif arb_id == msg.id:
                    return msg
                # ensure we haven't gone over the timeout
                if time.time() - start_time > timeout:
                    return None

        except queue.Empty:
            return None

    def recv_task(self):
        while True:
            msg = self.can_dev.recv()
            self.recv_queue.put(msg)

    def send_task(self):
        while True:
            msg = self.send_queue.get()
            self.can_dev.send(msg)
