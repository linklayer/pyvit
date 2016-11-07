class LoopbackDev:
    def __init__(self):
        self._buffer = []

    def send(self, msg):
        self._buffer.append(msg)

    def recv(self):
        if len(self._buffer) == 0:
            return None
        return self._buffer.pop()
