from canard import can 
from canard.proto.isotp import IsoTpProtocol, IsoTpMessage
import time

class UdsInterface(IsoTpProtocol):
    def __init__(self, can_dev):
        self.can_dev = can_dev

    def uds_request(self, ecu_id, service, payload, timeout=2):
        msg = IsoTpMessage(ecu_id)
        
        # pack data according to OBD-II standard
        msg.data = [service] + payload
        
        # standard OBD-II request messages have length of 2
        msg.length = len(payload) + 1

        # generate a request
        request = self.generate_frames(msg)
        
        # send the request
        for f in request:
            self.can_dev.send(f)
        
        # get a response message with the same ID
        start_ts = time.time()
        result = None

        while result == None
            if time.time() - start_ts > timeout:
                return None
 
            response = self.can_dev.recv()

            if response.id == ecu_id:
                result = self.parse_frame(response)
            
       
