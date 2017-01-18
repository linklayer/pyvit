from pyvit.proto.isotp import IsotpInterface


class ObdException(Exception):
    pass

class ObdInterface(IsotpInterface):
    def __init__(self, dispatcher, tx_arb_id=0x7DF, rx_arb_id=0x7E8):
        super().__init__(dispatcher, tx_arb_id, rx_arb_id)

    def request(self, mode, pid=None, timeout=2):
        # pack data according to OBD-II standard
        request = [mode]
        if pid is not None:
            request.append(pid)

        # send the request
        self.send(request)

        return self.recv()
    
    def get_supported_pids(self, mode=1):
        if mode not in (1, 9):
            raise ValueError("Only modes 1 and 9 are supported")

        resp = self.request(mode, 0)

        # first byte is mode + 0x40, second byte is pid (0)
        if resp[0] != mode + 0x40 or len(resp) != 6:
            raise ObdException("invalid response from ECU")

        # remaining bytes are data, convert so we can do bitwise math
        bits = (resp[2] << 24) + (resp[3] << 16) + (resp[4] << 8) + resp[5]

        # PIDs are encoded bitwise, MSB is pid 1
        pids = []
        pid = 0x20
        while pid >= 0: 
            if bits & 1:
                pids.append(pid)
            bits >>= 1
            pid -= 1

        return sorted(pids)
