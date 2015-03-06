from .. import can

class IsoTpProtocol:
    def __init__(self):
        pass

    def _start_msg(self, id=0):
        # initialize reading of a message
        self.msg = IsoTpMessage(id)
        self.data_byte_count = 0
        self.sequence_number = 0

    def _end_msg(self):
        # finish reading a message
        tmp = self.msg
        self.msg = None
        return tmp
        
    def reset(self):
        # abort reading a message
        self.msg = None

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
            
            self.msg.length = sf_dl

            # get data bytes from this frame
            self.msg.data = frame.data[1:sf_dl+1]

            # single frame, we're done!
            return self._end_msg()
            
        elif pci_type == 1:
            # first frame
            
            self._start_msg()

            # data length is lower nybble of byte 0 and byte 1
            ff_dl = ((frame.data[0] & 0xF) << 8) + frame.data[1]

            self.msg.length = ff_dl
            
            # retrieve data bytes from first frame
            for i in range(2, min(ff_dl+2, 8)):
                self.msg.data.append(frame.data[i])
                self.data_byte_count = self.data_byte_count + 1
                
            self.sequence_number = self.sequence_number + 1
            
        elif pci_type == 2:
            # consecutive frame
            
            # check that a FF has been sent
            if self.msg == None:
                raise ValueError("consecutive frame before first frame")
            
            # frame's sequence number is lower nybble of byte 0
            frame_sequence_number = frame.data[0] & 0xF
            
            # check the sequence number
            if frame_sequence_number != self.sequence_number:
                raise ValueError("invalid sequence number!")
            
            bytes_remaining = self.msg.length - self.data_byte_count

            # grab data bytes from this message
            for i in range(1, min(bytes_remaining, 7) + 1):
                self.msg.data.append(frame.data[i])
                self.data_byte_count = self.data_byte_count + 1
                
            if self.data_byte_count == self.msg.length:
                return self._end_msg()
            elif self.data_byte_count > self.msg.length:
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
            
            
    def generate_frames(self, msg):
        res = []
        if msg.length < 8:
            # message is less than 8 bytes, use single frame

            sf = can.Frame(msg.id)
            sf.dlc = msg.length + 1

            # first byte is data length
            sf.data = [msg.length] + msg.data
            
            res.append(sf)
            
        
        else:
            # message must be composed of FF and CF
            
            # first frame
            ff = can.Frame(msg.id)
            ff.dlc = min(msg.length+2, 8)

            data = []
            # FF pci type and msb of length
            data.append(0x10 + (msg.length >> 8))
            # lower byte of data
            data.append(msg.length & 0xFF)
            # first 6 bytes of data
            data = data + msg.data[0:6]

            ff.data = data
            res.append(ff)
            
            bytes_sent = 6
            sequence_number = 1
             
            while bytes_sent < msg.length:
                cf = can.Frame(msg.id)
                data_bytes_in_msg = min(msg.length - bytes_sent, 7)
                cf.dlc = data_bytes_in_msg + 1
                
                data = []
                data.append(0x20 + sequence_number)
                data = data + msg.data[bytes_sent:bytes_sent+data_bytes_in_msg]
                cf.data = data
                res.append(cf)
                
                sequence_number = sequence_number + 1
                # wrap around when sequence number reaches 0xF
                if sequence_number > 0xF:
                    sequence_number = 0

                bytes_sent = bytes_sent + data_bytes_in_msg

        return res
        
class IsoTpMessage:
    def __init__(self, id):
        self.length = 0 
        self.data = []
        self.id = id

    def __str__(self):
        return "%s" % self.data
