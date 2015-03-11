from canard import can 
from canard.proto.isotp import IsoTpProtocol, IsoTpMessage
import time

class UdsInterface(IsoTpProtocol):
    def __init__(self, can_dev):
        self.can_dev = can_dev

    def uds_request(self, ecu_id, service, payload, timeout=2):
        msg = IsoTpMessage(ecu_id)
        
        # first byte is service ID, rest of message is payload
        msg.data = [service] + payload
        
        # length is payload length plus 1 for service ID byte
        msg.length = len(payload) + 1

        # generate a request
        request = self.generate_frames(msg)

        # send the request
        for f in request:
            self.can_dev.send(f)
        
        # get a response message with the same ID
        start_ts = time.time()
        result = None

        while result == None:
            if time.time() - start_ts > timeout:
                return None
 
            response = self.can_dev.recv()
            
            if response.id == ecu_id + 0x20:
                result = self.parse_frame(response)

        return result
