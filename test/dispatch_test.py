import unittest
from multiprocessing import Queue

from pyvit.dispatch import Dispatcher
from pyvit.hw.loopback import LoopbackDev
from pyvit import can


class DispatchTest(unittest.TestCase):
    def setUp(self):
        dev = LoopbackDev()
        self.disp = Dispatcher(dev)

    def test_dispatcher_single(self):
        rx = Queue()
        self.disp.add_receiver(rx)

        self.disp.start()
        f = can.Frame(0x123)
        self.disp.send(f)
        f2 = rx.get()
        self.disp.stop()

        self.assertEqual(f, f2)

    def test_dispatcher_multiple(self):
        rx = Queue()
        self.disp.add_receiver(rx)

        tx1 = can.Frame(1, data=[1, 2, 3, 4, 5])
        tx2 = can.Frame(2, data=[0xFF, 0xFF, 0xFF])
        tx3 = can.Frame(3, data=[0xDE, 0xAD, 0xBE, 0xEF])

        self.disp.start()
        self.disp.send(tx1)
        self.disp.send(tx2)
        self.disp.send(tx3)
        rx1 = rx.get()
        rx2 = rx.get()
        rx3 = rx.get()
        self.disp.stop()

        self.assertEqual(rx1, tx1)
        self.assertEqual(rx2, tx2)
        self.assertEqual(rx3, tx3)

if __name__ == '__main__':
    unittest.main()
