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
        print('\n\nDiagnosticSessionControl')
        service = uds.DiagnosticSessionControl(
            uds.DiagnosticSessionControl.
            DiagnosticSessionType.programmingSession
            )
        req = service.encode()
        print(req)
        resp = service.decode([0x40 + uds.DiagnosticSessionControl.SID, 2])
        print(resp)

    def test_ecu_reset(self):
        print('\n\nECUReset')
        service = uds.ECUReset(
            uds.ECUReset.ResetType.hardReset
            )
        req = service.encode()
        print(req)
        resp = service.decode([0x40 + uds.ECUReset.SID, 2])
        print(resp)

    def test_security_access(self):
        print('\n\nSecurityAccess')
        service = uds.SecurityAccess(1) 
        req = service.encode()
        print(req)
        resp = service.decode([0x40 + uds.SecurityAccess.SID, 1, 12, 34])
        print(resp)
        service = uds.SecurityAccess(2, [0x12, 0x34]) 
        req = service.encode()
        print(req)
        resp = service.decode([0x40 + uds.SecurityAccess.SID, 2])
        print(resp)

    def test_communication_control(self):
        print('\n\nCommunicationControl')
        service = uds.CommunicationControl(
            uds.CommunicationControl.ControlType.disableRxAndTx,
            uds.CommunicationControl.CommunicationType
            .normalCommunicationMessages
        ) 
        req = service.encode()
        print(req)
        valid = [uds.CommunicationControl.SID,
                 uds.CommunicationControl.ControlType.disableRxAndTx,
                 0x1]
        self.assertEqual(req, valid)

        ct = 1
        resp = service.decode([0x40 + uds.CommunicationControl.SID, ct])
        print(resp)
        self.assertEqual(resp['controlType'], ct)

    def test_tester_present(self):
        print('\n\nTesterPresent')
        service = uds.TesterPresent()
        req = service.encode()
        print(req)
        valid = [uds.TesterPresent.SID, 0]
        self.assertEqual(req, valid)

        resp = service.decode([0x40 + uds.TesterPresent.SID, 0])
        print(resp)
        
    def test_access_timing_parameter(self):
        print('\n\nAccessTimingParameter')
        at = (uds.AccessTimingParameter.AccessType
              .setTimingParametersToGivenValues)

        service = uds.AccessTimingParameter(at, [1,2,3])
        req = service.encode()
        print(req)
        valid = [uds.AccessTimingParameter.SID, at, 1, 2, 3]
        self.assertEqual(req, valid)

        at = (uds.AccessTimingParameter.AccessType
              .setTimingParametersToGivenValues)
        resp = service.decode([0x40 + uds.AccessTimingParameter.SID, at])
        print(resp)
        self.assertEqual(resp['timingParameterAccessType'], at)
     
        at = (uds.AccessTimingParameter.AccessType
              .readCurrentlyActiveTimingParameters)
        service = uds.AccessTimingParameter(at)
        req = service.encode()
        print(req)
        valid = [uds.AccessTimingParameter.SID, at]
        self.assertEqual(req, valid)

        at = (uds.AccessTimingParameter.AccessType
              .readCurrentlyActiveTimingParameters)
        resp = service.decode([0x40 + uds.AccessTimingParameter.SID, at,
                               1,2,3])
        print(resp)
        self.assertEqual(resp['TimingParameterResponseRecord'], [1,2,3])
        self.assertEqual(resp['timingParameterAccessType'], at)
     
    def test_security_data_transmission(self):
        print('\n\nsSecuredDataTransmission')
        service = uds.SecuredDataTransmission([1,2,3,4])
        req = service.encode()
        print(req)
        valid = [uds.SecuredDataTransmission.SID, 1, 2, 3, 4]
        self.assertEqual(req, valid)

        resp = service.decode([0x40 + uds.SecuredDataTransmission.SID,
                               1, 2, 3, 4])
        print(resp)
        self.assertEqual(resp['securityDataResponseRecord'], [1,2,3,4])
 
    def test_control_dtc_setting(self):
        print('\n\nControlDTCSetting')
        service = uds.ControlDTCSetting(uds.ControlDTCSetting.DTCSettingType.on)
        req = service.encode()
        print(req)
        valid = [uds.ControlDTCSetting.SID, 1]
        self.assertEqual(req, valid)

        resp = service.decode([0x40 + uds.ControlDTCSetting.SID, 2])
        print(resp)
        self.assertEqual(resp['DTCSettingType'], 2)
 
    def test_response_on_event(self):
        print('\n\nResponseOnEvent')
        service = uds.ResponseOnEvent(uds.ResponseOnEvent.EventType
                                      .stopResponseOnEvent, False)
        req = service.encode()
        print(req)
        valid = [uds.ResponseOnEvent.SID, 0x0, 0x02]
        self.assertEqual(req, valid)

        resp = service.decode([0x40 + uds.ResponseOnEvent.SID, 2])
        print(resp)

        service = uds.ResponseOnEvent(uds.ResponseOnEvent.EventType
                                      .onComparisonOfValues, True,
                                      event_window_time=0x10,
                                      event_type_record=[5] * 10,
                                      service_to_respond_to_record=[1, 2, 3])
        req = service.encode()
        print(req)
        valid = [uds.ResponseOnEvent.SID, 0x40+0x07, 0x10, 5, 5, 5, 5, 5, 5, 5,
                 5, 5, 5, 1, 2, 3]
        self.assertEqual(req, valid)

        resp = service.decode([0x40 + uds.ResponseOnEvent.SID, 2])
        print(resp)



if __name__ == '__main__':
    unittest.main()
