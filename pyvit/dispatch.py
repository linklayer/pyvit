import multiprocessing
from multiprocessing import Queue, Process

class Dispatcher:
    def __init__(self, device):
        # ensure the device has the required method functions
        if not (hasattr(device, 'start') and hasattr(device, 'stop') and
                hasattr(device, 'send') and hasattr(device, 'recv')):
            raise ValueError('invalid device')

        self._device = device
        self._rx_queues = []
        self._tx_queue = Queue()

    def add_receiver(self, rx_queue):
        # ensure the receive queue is a queue
        if not type(rx_queue) is multiprocessing.queues.Queue:
            raise ValueError('invalid receive queue, %s' % type(rx_queue))
        # ensure this queue is not already in the dispacher
        elif rx_queue in self._rx_queues:
            raise ValueError('queue already in dispatcher')

        self._rx_queues.append(rx_queue)

    def remove_receiver(self, rx_queue):
        # check the receive queue is in the dispatcher
        if not rx_queue in self._rx_queues:
            raise ValueError('rx_queue not in dispatcher')
        else:
            self._rx_queue.remove(rx_queue)

    def start(self):
        self._device.start()
        
        self.send_process = Process(target=self._send_loop)
        self.recv_process = Process(target=self._recv_loop)
        self.recv_process.start()
        self.send_process.start()


    def stop(self):
        self.recv_process.terminate()
        self.send_process.terminate()
        self._device.stop()

    def send(self, data):
        self._tx_queue.put(data)

    def _send_loop(self):
        while True:
            data = self._tx_queue.get()
            self._device.send(data)

    def _recv_loop(self):
        while True:
            data = self._device.recv()
            for rx_queue in self._rx_queues:
                rx_queue.put_nowait(data)
