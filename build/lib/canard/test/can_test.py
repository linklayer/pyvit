import canard.can as can
import unittest

class CanTest(unittest.TestCase):
    def setUp(self):
        self.frame = can.Frame(0)

    def test_id(self):
        # test non-integer fails
        with self.assertRaises(AssertionError):
            self.frame.id = 'boo!'

        # test negative id fails
        with self.assertRaises(ValueError):
            self.frame.id = -1

        # test standard id out of range
        self.frame.is_extended_id = False
        with self.assertRaises(ValueError):
            self.frame.id = 0x800
        # test standard id in range
        self.frame.id = 0x7FF
        self.frame.id = 0x0

        # test extended id out of range
        self.frame.is_extended_id = True
        with self.assertRaises(ValueError):
            self.frame.id = 0x2FFFFFFF
        # test extended id in range
        self.frame.id = 0x1FFFFFFF
        self.frame.id = 0x0

    def test_data(self):
        # test too many bytes causes error
        with self.assertRaises(AssertionError):
            self.frame.data = [1,2,3,4,5,6,7,8,9]
        # test wrong datatype causes error
        with self.assertRaises(AssertionError):
            self.frame.data = 4
        # test out of range byte causes error
        with self.assertRaises(AssertionError):
            self.frame.data = [1,2,3,4,5,6,7,0xFFFF]
        # check padding
        self.frame.data = [1,2,3,4,5,6,7,8]
        self.frame.dlc = 8
        self.assertEqual(self.frame.data,
                         [1, 2, 3, 4, 5, 6, 7, 8])

        self.frame.dlc = 3
        self.assertEqual(self.frame.data,
                         [1, 2, 3, None, None, None, None, None])
        self.frame.dlc = 0
        self.assertEqual(self.frame.data,
                         [None, None, None, None, None, None, None, None])

    def test_frame_type(self):
        # test invalid frame type causes error
        with self.assertRaises(AssertionError):
            self.frame.frame_type = 5
        # test valid frame types
        self.frame.frame_type = can.FrameType.DataFrame
        self.frame.frame_type = can.FrameType.RemoteFrame
        self.frame.frame_type = can.FrameType.ErrorFrame
        self.frame.frame_type = can.FrameType.OverloadFrame

    def test_dlc(self):
        with self.assertRaises(AssertionError):
            self.frame.dlc = 'test'
        with self.assertRaises(AssertionError):
            self.frame.dlc = 9
        with self.assertRaises(AssertionError):
            self.frame.dlc = -1

    def test_init(self):
        frame = can.Frame(0x55, 6, [1,2,3,4,5,6], can.FrameType.ErrorFrame, True)
        self.assertEqual(frame.id, 0x55)
        self.assertEqual(frame.data, [1,2,3,4,5,6,None,None])
        self.assertEqual(frame.frame_type, can.FrameType.ErrorFrame)
        self.assertEqual(frame.is_extended_id, True)

if __name__ == '__main__':
    unittest.main()
