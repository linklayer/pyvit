import sys
from pyvit.hw.logplayer import LogPlayer
from pyvit.proto.uds import *


def read_file(filename, req_arb_id, resp_arb_id, resp_timeout = 0.5):
    lp = LogPlayer(filename, realtime=False)
    disp = Dispatcher(lp)
    uds_req = UDSInterface(disp, 0, req_arb_id)
    uds_resp = UDSInterface(disp, 0, resp_arb_id)
    disp.start()

    session = []

    while True:
        try:
            req = uds_req.decode_request()
            if req is None:
                break
            session.append(req)

            resp = None
            # wait until we get a response
            # this will return None if there is a response pending
            start = time.time()
            while resp is None:
                try:
                    resp = uds_resp.decode_response()
                except ResponsePendingException as e:
                    # response pending, go for next
                    resp = None
                if time.time() - start > resp_timeout:
                    break
            session.append(resp)

        except NegativeResponseException as e:
            session.append(e)
        except ValueError as e:
            # sometimes other errors could be present in the log
            session.append(e)

    disp.stop()
    return session

if len(sys.argv) == 4:
    filename = sys.argv[1]
    uds_tx_id = int(sys.argv[2], 0)
    uds_rx_id = int(sys.argv[3], 0)
else:
    print('using sample file')
    filename = 'sample_uds_log.txt'
    uds_tx_id = 0x6E0
    uds_rx_id = 0x51C

print(filename)
session = read_file(filename, uds_tx_id, uds_rx_id)

for r in session:
    if isinstance(r, GenericRequest):
        print('\n[->] Request [%s / 0x%X]' % (r.name, r.SID))
        for k in r.keys():
            if isinstance(r[k],list):
                print('\t%s: %s' % (k,[hex(x) for x in r[k]]))
            else:
                print('\t%s: 0x%X' % (k, r[k]))

    elif isinstance(r, GenericResponse):
        print('[<-] Response [%s / 0x%X]' % (r.name, r.SID))
        for k in r.keys():
            if isinstance(r[k],list):
                print('\t%s: %s' % (k,[hex(x) for x in r[k]]))
            else:
                print('\t%s: %s' % (k, r[k]))

    elif isinstance(r, NegativeResponseException):
        print('\n[!!] %s' % r)
    elif r is None:
        print('\n[??] Unknown Service: %s' % r)
    else:
        print('\n[!?] Strange stuff: %s' % r)
