from canard import can 
from canard.proto.isotp import IsoTpProtocol, IsoTpMessage
import time

class ObdInterface(IsoTpProtocol):
    def __init__(self, can_dev):
        self.can_dev = can_dev

    def obd_request(self, ecu_id, mode, pid_code, timeout=2):
        msg = IsoTpMessage(ecu_id)
        
        # pack data according to OBD-II standard
        msg.data = [mode, pid_code]
        
        # standard OBD-II request messages have length of 2
        msg.length = 2

        # this will always generate a single frame
        request = self.generate_frames(msg)[0]
        
        # send the request
        self.can_dev.send(request)
        
        # get a response message with the same ID
        response = self.can_dev.recv()
        start_ts = time.time()
        while response.id != ecu_id + 0x20:
            response = self.can_dev.recv()
            if time.time() - start_ts > timeout:
                return None
                
        return self.parse_frame(response)
