import unittest

from pyvit.hw.loopback import LoopbackDev
from pyvit import can


class LoopbackTest(unittest.TestCase):
    def setUp(self):
        self.dev = LoopbackDev()
        self.dev.start()

    def tearDown(self):
        self.dev.stop()

    def test_tx_rx_one(self):
        """ Test transmission and reception of one frame """
        f = can.Frame(0x123)
        self.dev.send(f)
        self.assertEqual(f, self.dev.recv())

    def test_tx_rx_multiple(self):
        """ Test transmission and reception of multiple frames """
        f1 = can.Frame(0x1)
        f2 = can.Frame(0x2)
        f3 = can.Frame(0x3)

        self.dev.send(f1)
        self.dev.send(f2)
        self.dev.send(f3)

        self.assertEqual(f1, self.dev.recv())
        self.assertEqual(f2, self.dev.recv())
        self.assertEqual(f3, self.dev.recv())


if __name__ == '__main__':
    unittest.main()
