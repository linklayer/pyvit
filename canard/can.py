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
        dlc (int): data length code
        data (list of int): CAN data bytes
        frame_type (int): type of CAN frame
        dlc (int): data length code of frame
        is_extended_id (bool): is this frame an extended identifier frame?
    """

    _id = None
    _data = []
    _frame_type = None
    dlc = 0
    timestamp = None

    def __init__(self, id, dlc = 0, data = [], frame_type = FrameType.DataFrame,
                 is_extended_id = False):
        """ Initializer of Frame
        Args:
            id (int): identifier of CAN frame
            dlc (int, optional): data length code of frame (defaults to 0)
            data (list, optional): data of CAN frame, defaults to empty list
            frame_type (int, optional): type of frame, defaults to 
                                        FrameType.DataFrame
            is_extended_id (bool, optional): is the frame an extended id frame?
                                             defaults to False
        """
        self.id = id
        self.data = data
        self.frame_type = frame_type
        self.is_extended_id = is_extended_id
        self.dlc = dlc

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
        elif value > 0x7FF and value <= 0x1FFFFFFF and self.is_extended_id:
            self._id = value
        # otherwise, id is not valid
        else:
            raise ValueError('CAN ID out of range')

    @property
    def data(self):
        result = []
        # return bytes up to dlc length, pad with zeros
        for i in range(0, min(self.dlc, len(self._data))):
            result.append(self._data[i])
        result = result + [0] * (8 - len(result))
        return result

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
        return self._dlc
    @dlc.setter
    def dlc(self, value):
        assert isinstance(value, int)
        assert value >= 0 and value <= 8, 'dlc must be between 0 and 8'
        self._dlc = value

    def __str__(self):
        ext_str = 'standard'
        if self.is_extended_id:
            ext_str == 'extended'
        if self.frame_type == FrameType.DataFrame:
            type_str = "data"
        elif self.frame_type == FrameType.RemoteFrame:
            type_str = "remote"
        elif self.frame_type == FrameType.ErrorFrame:
            type_str = "error"
        elif self.frame_type == FrameType.OverloadFrame:
            type_str = "overload"

        result = 'Frame:'
        result = result + '\tID=0x%X, DLC=%d, ' % (self.id, self.dlc)
        result = result + '%s, %s' % (ext_str, type_str)
        result = result + '\n\tData=%s' % self.data
        return result

