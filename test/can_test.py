import pyvit.can as can
import unittest


class CanTest(unittest.TestCase):
    def setUp(self):
        self.frame = can.Frame(0)

    def test_arb_id(self):
        """ Test CAN frame arbitration ID validation """

        # test non-integer fails
        with self.assertRaises(AssertionError):
            self.frame.arb_id = 'boo!'

        # test negative id fails
        with self.assertRaises(ValueError):
            self.frame.arb_id = -1

        # test id out of range
        with self.assertRaises(ValueError):
            self.frame.arb_id = 0x2FFFFFFF

        # test id in range
        self.frame.arb_id = 0x1FFFFFFF
        self.frame.arb_id = 0x0

    def test_data(self):
        """ Test CAN frame data validation """

        # test too many bytes causes error
        with self.assertRaises(AssertionError):
            self.frame.data = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        # test wrong datatype causes error
        with self.assertRaises(AssertionError):
            self.frame.data = 4
        # test out of range byte causes error
        with self.assertRaises(AssertionError):
            self.frame.data = [1, 2, 3, 4, 5, 6, 7, 0xFFFF]

    def test_frame_type(self):
        """ Test CAN frame type validation """

        # test invalid frame type causes error
        with self.assertRaises(AssertionError):
            self.frame.frame_type = 5
        # test valid frame types
        self.frame.frame_type = can.FrameType.DataFrame
        self.frame.frame_type = can.FrameType.RemoteFrame
        self.frame.frame_type = can.FrameType.ErrorFrame
        self.frame.frame_type = can.FrameType.OverloadFrame

    def test_init(self):
        """ Test CAN frame initialization """
        frame = can.Frame(0x55, [1, 2, 3, 4, 5, 6], can.FrameType.ErrorFrame)
        self.assertEqual(frame.arb_id, 0x55)
        self.assertEqual(frame.data, [1, 2, 3, 4, 5, 6])
        self.assertEqual(frame.frame_type, can.FrameType.ErrorFrame)

    def test_extended(self):
        """ Test extended arbitration IDs """
        frame = can.Frame(0x1234)
        self.assertEqual(frame.arb_id, 0x1234)
        self.assertTrue(frame.is_extended_id)

if __name__ == '__main__':
    unittest.main()
