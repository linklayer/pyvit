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
        self._running = False

    def add_receiver(self, rx_queue):
        if self.is_running:
            raise Exception('dispatcher must be stopped to add receiver')

        # ensure the receive queue is a queue
        if not isinstance(rx_queue, multiprocessing.queues.Queue):
            raise ValueError('invalid receive queue, %s' % type(rx_queue))
        # ensure this queue is not already in the dispacher
        elif rx_queue in self._rx_queues:
            raise ValueError('queue already in dispatcher')

        self._rx_queues.append(rx_queue)

    def remove_receiver(self, rx_queue):
        if self.is_runnning():
            raise Exception('dispatcher must be stopped to remove receiver')

        # check the receive queue is in the dispatcher
        if rx_queue not in self._rx_queues:
            raise ValueError('rx_queue not in dispatcher')
        else:
            self._rx_queue.remove(rx_queue)

    def start(self):
        if self.is_running:
            raise Exception('dispatcher already running')

        self._device.start()

        self._send_process = Process(target=self._send_loop)
        self._recv_process = Process(target=self._recv_loop)
        self._recv_process.start()
        self._send_process.start()
        self._running = True

    def stop(self):
        if not self.is_running:
            raise Exception('dispatcher not running')

        self._recv_process.terminate()
        self._send_process.terminate()
        self._device.stop()
        self._running = False

    @property
    def is_running(self):
        return self._running

    def send(self, data):
        if not self.is_running:
            raise Exception('dispatcher not running')

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
