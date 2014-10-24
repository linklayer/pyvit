from . import can

class Bus:
    # message that belong to this bus
    _messages = []

    def add_message(self, message):
        assert isinstance(message, Message), 'invalid message'
        if message in self._messages:
            raise ValueError('Message %s already in bus' % message)
        else:
            self._messages.append(message)

    def remove_message(self, message):
        assert isinstance(Message, message), 'invalid message'
        try:
            self._messages.remove(message)
        except ValueError:
            raise ValueError('Message %s is not in bus' % message)

    def parse_frame(self, frame):
        assert isinstance(frame, can.Frame), 'invalid frame'
        for message in self._messages:
            if message.id == frame.id:
                return message.parse_frame(frame)

    def __str__(self):
        s = "Bus:\n"
        for message in self._messages:
            s = s + message.__str__()
        return s

class Message(object):
    # signals that belong to this message, indexed by start bit
    _signals = {}

    def __init__(self, name, id):
        self.name = name
        self.id = id

    def add_signal(self, signal, start_bit):
        assert isinstance(signal, Signal), 'invalid signal'
        assert isinstance(start_bit, int) and start_bit < 63, 'invalid start bit'
        self._signals[start_bit] = signal

    def remove_signal(self, signal):
        pass

    def parse_frame(self, frame):
        assert isinstance(frame, can.Frame), 'invalid frame'
        assert frame.id == self.id, 'frame id does not match message id'

        # combine 8 data bytes into single value
        frame_value = 0
        for i in range(0, frame.dlc):
            if frame.data[i] != None:
                frame_value = frame_value + (frame.data[i] << (8 * i))

        result_signals = []

        # iterate over signals
        for start_bit, signal in self._signals.items():

            # find the last bit of the singal
            end_bit = signal.bit_length + start_bit

            # compute the mask
            mask = 0
            for j in range(start_bit, end_bit):
                mask = mask + 2**j

            # apply the mask, then downshift
            value = (frame_value & mask) >> start_bit
            # pass the maksed value to the signal
            signal.parse_value(value)

            result_signals.append(signal)

        return result_signals

    def __str__(self):
        s = "Message: %s, ID: 0x%X\n" % (self.name, self.id)
        for start_bit, signal in self._signals.items():
            s = s + "\t" + signal.__str__() + "\n"
        return s

class Signal:
    def __init__(self, name, bit_length, factor=1, offset=0):
        self.name = name
        self.bit_length = bit_length
        self.factor = factor
        self.offset = offset
        self.value = 0

    def parse_value(self, value):
        self.value = value * self.factor + self.offset
        return self

    def __str__(self):
        s = "Signal: %s\tValue = %d" % (self.name, self.value)
        return s
