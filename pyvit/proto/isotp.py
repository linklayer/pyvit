import time
from multiprocessing import Queue
from queue import Empty

from .. import can


class IsotpInterface:
    debug = False

    def __init__(self, dispatcher, tx_arb_id, rx_arb_id, padding=0):
        self._dispatcher = dispatcher
        self.tx_arb_id = tx_arb_id
        self.rx_arb_id = rx_arb_id
        self.padding_value = padding
        self._recv_queue = Queue()

        self._dispatcher.add_receiver(self._recv_queue)

    def _pad_data(self, data):
        # pad data to 8 bytes
        return data + ([self.padding_value] * (8 - len(data)))

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

    def _set_filter(self):
        if (hasattr(self._dispatcher._device, "set_filter_id") and
                hasattr(self._dispatcher._device, "set_filter_mask")):
            self._dispatcher._device.set_filter_id(self.rx_arb_id)
            self._dispatcher._device.set_filter_mask(0x7FF)

    def _unset_filter(self):
        if (hasattr(self._dispatcher._device, "set_filter_id") and
                hasattr(self._dispatcher._device, "set_filter_mask")):
            self._dispatcher._device.set_filter_mask(0)

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
                raise ValueError('invalid SF_DL parameter for single frame')

            self.data_len = sf_dl

            # get data bytes from this frame
            self.data = frame.data[1:sf_dl+1]

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

            # send a flow control frame
            fc = can.Frame(self.tx_arb_id, data=[0x30,
                                                 self.block_size,
                                                 self.st_min])
            self._dispatcher.send(fc)
            self.block_size_counter = self.block_size

        elif pci_type == 2:
            # consecutive frame

            # check that a FF has been sent
            if self.data_len == 0:
                raise ValueError('consecutive frame before first frame')

            # frame's sequence number is lower nybble of byte 0
            frame_sequence_number = frame.data[0] & 0xF

            # check the sequence number
            if frame_sequence_number != self.sequence_number:
                raise ValueError('invalid sequence number!')

            bytes_remaining = self.data_len - self.data_byte_count

            # grab data bytes from this message
            for i in range(1, min(bytes_remaining, 7) + 1):
                self.data.append(frame.data[i])
                self.data_byte_count = self.data_byte_count + 1

            if self.data_byte_count == self.data_len:
                return self._end_msg()
            elif self.data_byte_count > self.data_len:
                raise ValueError('data length mismatch')

            # wrap around when sequence number reaches 0xF
            self.sequence_number = self.sequence_number + 1
            if self.sequence_number > 0xF:
                self.sequence_number = 0

            if self.block_size_counter > 0:
                self.block_size_counter -= 1
                if self.block_size_counter == 0:
                    # need to send flow control
                    fc = can.Frame(self.tx_arb_id, data=[0x30,
                                                         self.block_size,
                                                         self.st_min])
                    self._dispatcher.send(fc)

                    # reset block size counter
                    self.block_size_counter = self.block_size

        else:
            raise ValueError('invalid PCItype parameter')

    def recv(self, timeout=1, bs=0, st_min=0):
        data = None
        start = time.time()

        self._set_filter()

        self.block_size = bs

        if not st_min <= 0x7F and not (st_min >= 0xF1 and st_min <= 0xF9):
            raise ValueError(
                "st_min must be beween 0x00 and 0x7F or 0xF1 and 0xF9")
        self.st_min = st_min

        while data is None:
            # attempt to get data, returning None if we timeout
            try:
                rx_frame = self._recv_queue.get(timeout=timeout)
            except Empty:
                return None

            if rx_frame.arb_id == self.rx_arb_id:
                if self.debug:
                    print(rx_frame)
                data = self.parse_frame(rx_frame)

            # check timeout, since we may be receiving messages that do not
            # have the required arb_id
            if time.time() - start > timeout:
                return None

        self._unset_filter()
        return data

    def send(self, data):
        if len(data) > 4095:
            raise ValueError('ISOTP data must be <= 4095 bytes long')

        self._set_filter()

        if len(data) < 8:
            # message is less than 8 bytes, use single frame

            sf = can.Frame(self.tx_arb_id)

            # first byte is data length, remainder is data
            sf.data = self._pad_data([len(data)] + data)

            if self.debug:
                print(sf)
            self._dispatcher.send(sf)

        else:
            # message must be composed of FF and CF

            # first frame
            ff = can.Frame(self.tx_arb_id)

            frame_data = []
            # FF pci type and msb of length
            frame_data.append(0x10 + (len(data) >> 8))
            # lower byte of data
            frame_data.append(len(data) & 0xFF)
            # first 6 bytes of data
            frame_data = frame_data + data[0:6]

            ff.data = self._pad_data(frame_data)
            if self.debug:
                print(ff)
            self._dispatcher.send(ff)

            bytes_sent = 6
            sequence_number = 1

            # force to wait for a flow control frame
            fc_bs = 1

            while bytes_sent < len(data):
                if fc_bs > 0:
                    fc_bs -= 1
                    if fc_bs == 0:
                        # must wait for a flow control frame
                        while True:
                            rx_frame = self._recv_queue.get()
                            if (rx_frame.arb_id == self.rx_arb_id and
                                    rx_frame.data[0] == 0x30):
                                if self.debug:
                                    print(rx_frame)
                                # flow control frame received, get parameters
                                fc_bs = rx_frame.data[1]
                                fc_stmin = rx_frame.data[2]
                                break

                # wait for fc_stmin ms/us
                if fc_stmin < 0x80:
                    # fc_stmin equal to ms to wait
                    time_to_wait = fc_stmin/1000.0
                    time.sleep(time_to_wait)
                elif fc_stmin >= 0xF1 and fc_stmin <= 0xF9:
                    # fc_stmin equal to 100 - 900 us to wait
                    time_to_wait = (fc_stmin-0xF0)/1000000.0
                    time.sleep(time_to_wait)

                cf = can.Frame(self.tx_arb_id)
                data_bytes_in_msg = min(len(data) - bytes_sent, 7)

                frame_data = []
                frame_data.append(0x20 + sequence_number)
                frame_data = (frame_data +
                              data[bytes_sent:bytes_sent+data_bytes_in_msg])
                cf.data = self._pad_data(frame_data)

                if self.debug:
                    print(cf)
                self._dispatcher.send(cf)

                sequence_number = sequence_number + 1
                # wrap around when sequence number reaches 0xF
                if sequence_number > 0xF:
                    sequence_number = 0

                bytes_sent = bytes_sent + data_bytes_in_msg

        self._unset_filter()
