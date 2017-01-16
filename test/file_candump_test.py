import tempfile

import pyvit.can as can
from pyvit.file import log

import unittest


class FileCanDumpTest(unittest.TestCase):
    def test_defaults(self):
        """ Test write & readback of candump file with default timestamp and
        interface """
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        file_name = temp_file.name

        cdf = log.CandumpFile(file_name)

        frames = [can.Frame(0x123, [1, 2, 3, 4, 5, 6, 7, 8]),
                  can.Frame(0x0),
                  can.Frame(0x1, [0xFF] * 8)]

        cdf.export_frames(frames)
        frames2 = cdf.import_frames()

        temp_file.close()

        for i in range(0, len(frames)):
            self.assertEqual(frames[i], frames2[i])

    def test_full(self):
        """ Test write & readback of candump file with defined timestamp and
        interface """
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        file_name = temp_file.name

        cdf = log.CandumpFile(file_name)

        frames = [can.Frame(0x1,
                            [1, 2, 3, 4, 5, 6, 7, 8],
                            interface='can0',
                            timestamp=1.0),
                  can.Frame(0x2,
                            interface='can1',
                            timestamp=2.0),
                  can.Frame(0x3,
                            [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF],
                            interface='can2',
                            timestamp=3.0)]

        cdf.export_frames(frames)
        frames2 = cdf.import_frames()

        temp_file.close()

        for i in range(0, len(frames)):
            self.assertEqual(frames[i], frames2[i])

if __name__ == '__main__':
    unittest.main()
