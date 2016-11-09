from collections import deque


class LoopbackDev:
    def __init__(self):
        self._buffer = deque()

    def send(self, msg):
        self._buffer.appendleft(msg)

    def recv(self):
        if len(self._buffer) == 0:
            return None
        return self._buffer.pop()
