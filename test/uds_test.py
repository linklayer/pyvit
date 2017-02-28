import unittest
from pyvit.proto import uds


class CanTest(unittest.TestCase):
    def test_nrc(self):
        service = uds.DiagnosticSessionControl(0)
        try:
            service.decode([0x7F, 0x33])
        except uds.NegativeResponseException as e:
            print(e)

    def test_diagnostic_session_control(self):
        service = uds.DiagnosticSessionControl(
            uds.DiagnosticSessionControl.
            DiagnosticSessionType.programmingSession
            )
        req = service.encode()
        print(req)
        resp = service.decode([0x40 + uds.DiagnosticSessionControl.SID, 2])
        print(resp)

if __name__ == '__main__':
    unittest.main()
