import os
import pyvit.can as can
from pyvit.file.db.jsondb import JsonDbParser

import unittest


class FileDbJsonDbTest(unittest.TestCase):
    def test_defaults(self):
        """ Test parsing a json database """
        uut = JsonDbParser()

        # Should not throw any exceptions or errors
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 'vector_jsondb.json')
        bus_db = uut.parse(file_path)

        # [600 RPM, 4th gear, 2 units of voltage, unit to be divided by 10,
        # unit with offset]
        frame_1 = can.Frame(0x123, [88, 2, 0b00010100, 50, 10])

        signals = bus_db.parse_frame(frame_1)
        # TODO: check signal values

if __name__ == '__main__':
    unittest.main()
