import unittest
import threading

from pyvit.hw.loopback import LoopbackDev
from pyvit.dispatch import Dispatcher
from pyvit.proto.isotp import IsotpInterface


class IsotpTest(unittest.TestCase):
    def setUp(self):
        self.dev = LoopbackDev()
        self.disp = Dispatcher(self.dev)
        # set up an isotp interface that sends and receives the same arb id
        self.sender = IsotpInterface(self.disp, 0, 1)
        self.receiver = IsotpInterface(self.disp, 1, 0)
        self.disp.start()

    def tearDown(self):
        self.disp.stop()

    def test_single_frame_loopback(self):
        """ Test ISOTP transmission and reception of a single frame message """
        payload = [0xDE, 0xAD, 0xBE, 0xEF]
        self.sender.send(payload)
        resp = self.receiver.recv()
        self.assertEqual(payload, resp)

    def test_multi_frame_loopback(self):
        """ Test ISOTP transmission and reception of a multi-frame message """
        payload = [0xDE, 0xAD, 0xBE, 0xEF, 0xDE, 0xAD, 0xBE, 0xEF]*50

        # we need to run this in a thread so that the flow control frame is
        # sent and received, as IsotpInterfaces block
        tx_thread = threading.Thread(target=self.sender.send, args=(payload, ))
        tx_thread.start()

        # we'll receive data in this thread
        resp = self.receiver.recv()

        # wait for the transmitting thread to finish, then verify the result
        tx_thread.join()
        self.assertEqual(payload, resp)

    def test_tx_too_long(self):
        """ Ensure transmission of data that is too long raises exception """
        with self.assertRaises(ValueError):
            self.sender.send([0xFF]*4096)

    def test_padding(self):
        """ Test padding of frames sent using ISOTP """
        payload = [0xDE, 0xAD, 0xBE, 0xEF]
        self.sender.padding_value = 0x55
        self.sender.send(payload)
        resp = self.dev.recv()
        self.assertEqual(resp.data,
                         [0x04, 0xDE, 0xAD, 0xBE, 0xEF, 0x55, 0x55, 0x55])

if __name__ == '__main__':
    unittest.main()
