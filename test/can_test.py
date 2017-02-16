import pyvit.can as can
import unittest


class CanTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_arb_id(self):
        """ Test CAN frame arbitration ID validation """

        std_frame = can.Frame(0)
        ext_frame = can.Frame(0, extended=True)

        # test non-integer fails
        with self.assertRaises(AssertionError):
            std_frame.arb_id = 'boo!'

        # test negative id fails
        with self.assertRaises(ValueError):
            std_frame.arb_id = -1

        # test non extended throws error when ID is too large
        with self.assertRaises(ValueError):
            std_frame.arb_id = 0x1234

        # test id out of range
        ext_frame = can.Frame(0, extended=True)
        with self.assertRaises(ValueError):
            ext_frame.arb_id = 0x2FFFFFFF

        # test id in range
        ext_frame.arb_id = 0x1FFFFFFF
        ext_frame.arb_id = 0x0
        std_frame.arb_id = 0x7FF
        std_frame.arb_id = 0x0

    def test_data(self):
        """ Test CAN frame data validation """

        frame = can.Frame(0)

        # test too many bytes causes error
        with self.assertRaises(AssertionError):
            frame.data = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        # test wrong datatype causes error
        with self.assertRaises(AssertionError):
            frame.data = 4
        # test out of range byte causes error
        with self.assertRaises(AssertionError):
            frame.data = [1, 2, 3, 4, 5, 6, 7, 0xFFFF]

    def test_frame_type(self):
        """ Test CAN frame type validation """

        frame = can.Frame(0)

        # test invalid frame type causes error
        with self.assertRaises(AssertionError):
            frame.frame_type = 5
        # test valid frame types
        frame.frame_type = can.FrameType.DataFrame
        frame.frame_type = can.FrameType.RemoteFrame
        frame.frame_type = can.FrameType.ErrorFrame
        frame.frame_type = can.FrameType.OverloadFrame

    def test_init(self):
        """ Test CAN frame initialization """
        frame = can.Frame(0x55, [1, 2, 3, 4, 5, 6], can.FrameType.ErrorFrame)
        self.assertEqual(frame.arb_id, 0x55)
        self.assertEqual(frame.data, [1, 2, 3, 4, 5, 6])
        self.assertEqual(frame.frame_type, can.FrameType.ErrorFrame)

    def test_extended(self):
        """ Test extended arbitration IDs """
        frame = can.Frame(0x1234, extended=True)
        self.assertEqual(frame.arb_id, 0x1234)
        self.assertTrue(frame.is_extended_id)

if __name__ == '__main__':
    unittest.main()
