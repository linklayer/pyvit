from multiprocessing import Queue


class LoopbackDev:
    def __init__(self):
        self._queue = Queue()
        self.running = False

    def start(self):
        if self.running:
            raise Exception('device already started')

        self.running = True

    def stop(self):
        if not self.running:
            raise Exception('device not started')

        self.running = False

    def send(self, data):
        if not self.running:
            raise Exception('device not started')

        self._queue.put(data)

    def recv(self):
        if not self.running:
            raise Exception('device not started')

        return self._queue.get()
