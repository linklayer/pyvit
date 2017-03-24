import os
import unittest

from pyvit.log import Logger
from pyvit import can
from pyvit.hw.logplayer import LogPlayer


class CanTest(unittest.TestCase):
    def setUp(self):
        self.log_filename = 'tmp.log'
        self.f = can.Frame(0x123)
        self.f.data = [1, 2, 3, 4, 5, 6, 7, 8]

        with Logger(self.log_filename) as log:
            for i in range(0, 10):
                log.log_frame(self.f)

    def test_log_and_readback_one(self):
        with LogPlayer('tmp.log') as lp:
            f2 = lp.recv()

        self.assertEqual(self.f, f2)

    def test_logplayer_iteration(self):
        with LogPlayer('tmp.log') as lp:
            count = 0

            for f in lp.recv_all():
                self.assertEqual(self.f, f)
                count += 1

            self.assertEqual(count, 10)

    def tearDown(self):
        os.remove(self.log_filename)

if __name__ == '__main__':
    unittest.main()
