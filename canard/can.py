""" can.py

Defines the low-level implementation of CAN.

"""


class FrameType:
    """ Enumerates the types of CAN frames """
    DataFrame = 1
    RemoteFrame = 2
    ErrorFrame = 3
    OverloadFrame = 4


class Frame(object):
    """ Represents a CAN Frame

    Attributes:
        id (int): CAN identifier of the Frame
        data (list of int): CAN data bytes
        frame_type (int): type of CAN frame
        is_extended_id (bool): is this frame an extended identifier frame?
    """

    def __init__(self, id, data=None, frame_type=FrameType.DataFrame,
                 is_extended_id=False):
        """ Initializer of Frame
        Args:
            id (int): identifier of CAN frame
            data (list, optional): data of CAN frame, defaults to empty list
            frame_type (int, optional): type of frame, defaults to
                                        FrameType.DataFrame
            is_extended_id (bool, optional): is the frame an extended id frame?
                                             defaults to False
        """

        self.is_extended_id = is_extended_id

        self.id = id
        if data:
            self.data = data
        else:
            self.data = []
        self.frame_type = frame_type

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        # ensure value is an integer
        assert isinstance(value, int), 'id must be an integer'
        # ensure standard id is in range
        if value >= 0 and value <= 0x7FF:
            self._id = value
        # otherwise, check if frame is extended
        elif self.is_extended_id and value > 0x7FF and value <= 0x1FFFFFFF:
            self._id = value
        # otherwise, id is not valid
        else:
            raise ValueError('CAN ID out of range')

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        # data should be a list
        assert isinstance(value, list), 'CAN data must be a list'
        # data can only be 8 bytes maximum
        assert not len(value) > 8, 'CAN data cannot contain more than 8 bytes'
        # each byte must be a valid byte, int between 0x0 and 0xFF
        for byte in value:
            assert isinstance(byte, int), 'CAN data must consist of bytes'
            assert byte >= 0 and byte <= 0xFF, 'CAN data must consist of bytes'
        # data is valid
        self._data = value

    @property
    def frame_type(self):
        return self._frame_type

    @frame_type.setter
    def frame_type(self, value):
        assert value == FrameType.DataFrame or value == FrameType.RemoteFrame \
            or value == FrameType.ErrorFrame or \
            value == FrameType.OverloadFrame, 'invalid frame type'
        self._frame_type = value

    @property
    def dlc(self):
        return len(self.data)

    def __str__(self):
        return ('ID=0x%03X, DLC=%d, Data=[%s]' %
                (self.id, self.dlc, ', '.join(hex(b) for b in self.data)))
