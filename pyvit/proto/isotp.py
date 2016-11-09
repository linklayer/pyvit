from .. import can


class IsotpProtocol:
    def __init__(self):
        pass

    def _start_msg(self, arb_id=0):
        # initialize reading of a message
        self.data = []
        self.data_len = 0
        self.data_byte_count = 0
        self.sequence_number = 0

    def _end_msg(self):
        # finish reading a message
        tmp = self.data
        self.data = []
        self.data_len = 0
        return tmp

    def reset(self):
        # abort reading a message
        self.data = []
        self.data_len = 0

    def parse_frame(self, frame):
        # pci type is upper nybble of first byte
        pci_type = (frame.data[0] & 0xF0) >> 4

        if pci_type == 0:
            # single frame

            self._start_msg()

            # data length is lower nybble for first byte
            sf_dl = frame.data[0] & 0xF

            # check that the data length is valid for a SF
            if not (sf_dl > 0 and sf_dl < 8):
                raise ValueError("invalid SF_DL parameter for single frame")

            self.data.length = sf_dl

            # get data bytes from this frame
            self.data_len = frame.data[1:sf_dl+1]

            # single frame, we're done!
            return self._end_msg()

        elif pci_type == 1:
            # first frame

            self._start_msg()

            # data length is lower nybble of byte 0 and byte 1
            ff_dl = ((frame.data[0] & 0xF) << 8) + frame.data[1]

            self.data_len = ff_dl

            # retrieve data bytes from first frame
            for i in range(2, min(ff_dl+2, 8)):
                self.data.append(frame.data[i])
                self.data_byte_count = self.data_byte_count + 1

            self.sequence_number = self.sequence_number + 1

        elif pci_type == 2:
            # consecutive frame

            # check that a FF has been sent
            if self.data_len == 0:
                raise ValueError("consecutive frame before first frame")

            # frame's sequence number is lower nybble of byte 0
            frame_sequence_number = frame.data[0] & 0xF

            # check the sequence number
            if frame_sequence_number != self.sequence_number:
                raise ValueError("invalid sequence number!")

            bytes_remaining = self.data_len - self.data_byte_count

            # grab data bytes from this message
            for i in range(1, min(bytes_remaining, 7) + 1):
                self.data.append(frame.data[i])
                self.data_byte_count = self.data_byte_count + 1

            if self.data_byte_count == self.data_len:
                return self._end_msg()
            elif self.data_byte_count > self.data_len:
                raise ValueError("invalid data length mismatch")

            # wrap around when sequence number reaches 0xF
            self.sequence_number = self.sequence_number + 1
            if self.sequence_number > 0xF:
                self.sequence_number = 0

        elif pci_type == 3:
            # flow control
            pass

        else:
            raise ValueError("invalid PCItype parameter")

    def generate_frames(self, arb_id, data):
        res = []
        if len(data) < 8:
            # message is less than 8 bytes, use single frame

            sf = can.Frame(arb_id)

            # first byte is data length
            sf.data = [len(data)] + data

            res.append(sf)

        else:
            # message must be composed of FF and CF

            # first frame
            ff = can.Frame(arb_id)

            frame_data = []
            # FF pci type and msb of length
            frame_data.append(0x10 + (len(data) >> 8))
            # lower byte of data
            frame_data.append(len(data) & 0xFF)
            # first 6 bytes of data
            frame_data = frame_data + data[0:6]

            ff.data = frame_data
            res.append(ff)

            bytes_sent = 6
            sequence_number = 1

            while bytes_sent < len(data):
                cf = can.Frame(arb_id)
                data_bytes_in_msg = min(len(data) - bytes_sent, 7)

                frame_data = []
                frame_data.append(0x20 + sequence_number)
                frame_data = (frame_data +
                              data[bytes_sent:bytes_sent+data_bytes_in_msg])
                cf.data = frame_data
                res.append(cf)

                sequence_number = sequence_number + 1
                # wrap around when sequence number reaches 0xF
                if sequence_number > 0xF:
                    sequence_number = 0

                bytes_sent = bytes_sent + data_bytes_in_msg

        return res
