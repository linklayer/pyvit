from pyvit.proto.isotp import IsotpInterface


class ObdInterface(IsotpInterface):
    def __init__(self, dispatcher, tx_arb_id=0x7DF, rx_arb_id=0x7E8):
        super().__init__(dispatcher, tx_arb_id, rx_arb_id)

    def obd_request(self, mode, pid=None, timeout=2):
        # pack data according to OBD-II standard
        request = [mode]
        if pid is not None:
            request.append(pid)

        # send the request
        self.send(request)

        return self.recv()
