import unittest

from pyvit.proto.isotp import IsotpProtocol
from pyvit.hw.loopback import LoopbackDev


class IsotpTest(unittest.TestCase):
    def setUp(self):
        self.dev = LoopbackDev()
        self.proto = IsotpProtocol()

    def test_isotp_tx_single(self):
        """ Test transmission and of a single frame isotp message """
        for f in self.proto.generate_frames(0x123, [1, 2, 3, 4, 5, 6, 7]):
            self.dev.send(f)

        f = self.dev.recv()
        # valid response: byte 0 = 0x07 (type 0 for SF, length 7) then data
        self.assertEqual(f.data, [0x7, 1, 2, 3, 4, 5, 6, 7])

    def test_isotp_tx_multiple(self):
        """ Test transmission and of a single frame isotp message """
        for f in self.proto.generate_frames(0x123, [1, 2, 3, 4, 5, 6, 7, 8]):
            self.dev.send(f)

        frames = []
        while True:
            f = self.dev.recv()
            frames.append(f)
            if f is None:
                break

        self.assertEqual(frames[0].data, [0x10, 8, 1, 2, 3, 4, 5, 6])
        self.assertEqual(frames[1].data, [0x21, 7, 8])

    def test_isotp_roundtrip_single(self):
        """ Test roundtrip of a single frame isotp message """
        tx_data = [1, 2, 3, 4, 5]
        for f in self.proto.generate_frames(0x123, tx_data):
            self.dev.send(f)

        while True:
            f = self.dev.recv()
            rx_data = self.proto.parse_frame(f)
            if rx_data is not None:
                break

        self.assertEqual(tx_data, rx_data)

    def test_isotp_roundtrip_multiple(self):
        """ Test roundtrip of a multiple frame isotp message """
        tx_data = range(0, 100)
        for f in self.proto.generate_frames(0x123, tx_data):
            self.dev.send(f)

        while True:
            f = self.dev.recv()
            rx_data = self.proto.parse_frame(f)
            if rx_data is not None:
                break

        self.assertEqual(tx_data, rx_data)

if __name__ == '__main__':
    unittest.main()
