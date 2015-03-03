from canard import can

class LoopbackDev:
    def __init__(self):
        self.buffer = []
    
    def send(self, msg):
        self.buffer.append(msg)

    def recv(self):
        if len(self.buffer) == 0:
            return None
        return self.buffer.pop()
