import unittest
from pyvit.proto import uds


class CanTest(unittest.TestCase):
    def test_nrc(self):
        service = uds.DiagnosticSessionControl(0)
        try:
            service.decode([0x7F, 0x33])
        except uds.NegativeResponseException as e:
            print('nrc:', e)

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

        service = uds.AccessTimingParameter(at, [1, 2, 3])
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
                               1, 2, 3])
        print(resp)
        self.assertEqual(resp['TimingParameterResponseRecord'], [1, 2, 3])
        self.assertEqual(resp['timingParameterAccessType'], at)

    def test_security_data_transmission(self):
        print('\n\nsSecuredDataTransmission')
        service = uds.SecuredDataTransmission([1, 2, 3, 4])
        req = service.encode()
        print(req)
        valid = [uds.SecuredDataTransmission.SID, 1, 2, 3, 4]
        self.assertEqual(req, valid)

        resp = service.decode([0x40 + uds.SecuredDataTransmission.SID,
                               1, 2, 3, 4])
        print(resp)
        self.assertEqual(resp['securityDataResponseRecord'], [1, 2, 3, 4])

    def test_control_dtc_setting(self):
        print('\n\nControlDTCSetting')
        service = uds.ControlDTCSetting(uds.
                                        ControlDTCSetting.DTCSettingType.on)
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

    def test_link_control(self):
        print('\n\nLinkControl')
        service = uds.LinkControl(
            uds.LinkControl.LinkControlType.transitionBaudrate)
        req = service.encode()
        print(req)
        valid = [uds.LinkControl.SID, 3]
        self.assertEqual(req, valid)

        resp = service.decode([0x40 + uds.LinkControl.SID, 3])
        print(resp)
        self.assertEqual(resp['linkControlType'], 3)

        service = uds.LinkControl(
            uds.LinkControl.LinkControlType.
            verifyBaudrateTransitionWithFixedBaudrate, 0xFF)
        req = service.encode()
        print(req)
        valid = [uds.LinkControl.SID, 1, 0xFF]
        self.assertEqual(req, valid)

        resp = service.decode([0x40 + uds.LinkControl.SID, 2])
        print(resp)
        self.assertEqual(resp['linkControlType'], 2)

    def test_rdbi(self):
        print('\n\nRDBI')
        service = uds.ReadDataByIdentifier(0x1234)
        req = service.encode()
        print(req)
        valid = [uds.ReadDataByIdentifier.SID, 0x12, 0x34]
        self.assertEqual(req, valid)

        resp = service.decode([0x40 + uds.ReadDataByIdentifier.SID, 0x12, 0x34,
                               1, 2, 3])
        print(resp)
        self.assertEqual(resp['dataIdentifier'], 0x1234)
        self.assertEqual(resp['dataRecord'], [1, 2, 3])

    def test_rmba(self):
        print('\n\nRMBA')
        service = uds.ReadMemoryByAddress(0x12345678, 0x10)
        req = service.encode()
        print(req)
        valid = [uds.ReadMemoryByAddress.SID, 0x14, 0x12, 0x34, 0x56, 0x78,
                 0x10]
        self.assertEqual(req, valid)

        resp = service.decode([0x40 + uds.ReadMemoryByAddress.SID, 0xAA, 0xBB,
                               1, 2, 3])
        print(resp)
        self.assertEqual(resp['dataRecord'], [0xAA, 0xBB, 1, 2, 3])

    def test_read_scaling(self):
        print('\n\nRScalingDBI')
        service = uds.ReadScalingDataByIdentifier(0x1234)
        req = service.encode()
        print(req)
        valid = [uds.ReadScalingDataByIdentifier.SID, 0x12, 0x34]
        self.assertEqual(req, valid)

        resp = service.decode([0x40 + uds.ReadScalingDataByIdentifier.SID,
                               0xAA, 0xBB, 1, 2, 3])
        print(resp)
        self.assertEqual(resp['dataIdentifier'], 0xAABB)
        self.assertEqual(resp['scalingData'], [1, 2, 3])

    def test_read_periodic(self):
        print('\n\nRDBPeriodicI')
        service = uds.ReadDataByPeriodicIdentifier(
            uds.ReadDataByPeriodicIdentifier.TransmissionMode.sendAtSlowRate,
            0xAA, 0xBB)
        req = service.encode()
        print(req)
        valid = [uds.ReadDataByPeriodicIdentifier.SID, 0x1, 0xAA, 0xBB]
        self.assertEqual(req, valid)

        resp = service.decode([0x40 + uds.ReadDataByPeriodicIdentifier.SID])
        print(resp)

    def test_wdbi(self):
        print('\n\nWDBI')
        service = uds.WriteDataByIdentifier(0xBEEF, [1, 2, 3, 4, 5, 6, 7])
        req = service.encode()
        print(req)
        valid = [uds.WriteDataByIdentifier.SID, 0xBE, 0xEF,
                 1, 2, 3, 4, 5, 6, 7]
        self.assertEqual(req, valid)

        resp = service.decode([0x40 + uds.WriteDataByIdentifier.SID,
                               0xBE, 0xEF])
        print(resp)
        self.assertEqual(resp['dataIdentifier'], 0xBEEF)

    def test_wmba(self):
        print('\n\nWMBA')
        service = uds.WriteMemoryByAddress(0xBEEF, [1, 2, 3, 4, 5, 6, 7])
        req = service.encode()
        print(req)
        valid = [uds.WriteMemoryByAddress.SID, 0x12, 0xBE, 0xEF, 7,
                 1, 2, 3, 4, 5, 6, 7]
        self.assertEqual(req, valid)

        resp = service.decode([0x40 + uds.WriteMemoryByAddress.SID, 0x12,
                               0xBE, 0xEF, 7])
        print(resp)
        self.assertEqual(resp['memoryAddress'], 0xBEEF)
        self.assertEqual(resp['memorySize'], 7)

    def test_clear_dtc(self):
        print('\n\nClearDiagnosticInformation')
        service = uds.ClearDiagnosticInformation(0xAABBCC)
        req = service.encode()
        print(req)
        valid = [uds.ClearDiagnosticInformation.SID, 0xAA, 0xBB, 0xCC]
        self.assertEqual(req, valid)

        resp = service.decode([0x40 + uds.ClearDiagnosticInformation.SID])
        print(resp)

    def test_io_ctl(self):
        print('\n\nIO Control')
        service = uds.InputOutputControlByIdentifier(0xABBA,
                                                     [1, 2, 3], [1, 2, 3])
        req = service.encode()
        print(req)
        valid = [uds.InputOutputControlByIdentifier.SID, 0xAB, 0xBA, 1, 2, 3,
                 1, 2, 3]
        self.assertEqual(req, valid)

        resp = service.decode([0x40 + uds.InputOutputControlByIdentifier.SID,
                               0xAB, 0xBA, 1, 2, 3])
        self.assertEqual(resp['dataIdentifier'], 0xABBA)
        self.assertEqual(resp['controlStatusRecord'], [1, 2, 3])
        print(resp)

    def test_routine_ctl(self):
        print('\n\nRoutine Control')
        service = uds.RoutineControl(
            uds.RoutineControl.RoutineControlType.startRoutine,
            0xABBA, [1, 2, 3, 4, 5])
        req = service.encode()
        print(req)
        valid = [uds.RoutineControl.SID, 0x1, 0xAB, 0xBA, 1, 2, 3, 4, 5]
        self.assertEqual(req, valid)

        resp = service.decode([0x40 + uds.RoutineControl.SID, 0x3,
                               0xAB, 0xBA, 1, 2, 3])
        self.assertEqual(resp['routineControlType'],
                         uds.RoutineControl.RoutineControlType.
                         requestRoutineResults)
        self.assertEqual(resp['routineIdentifier'], 0xABBA)
        self.assertEqual(resp['routineStatusRecord'], [1, 2, 3])
        print(resp)

    def test_request_dl(self):
        print('\n\nRequestDownload')
        service = uds.RequestDownload(0x1000, 0x100)
        req = service.encode()
        print(req)
        valid = [uds.RequestDownload.SID, 0, 0x22, 0x10, 0x0, 0x1, 0x0]
        self.assertEqual(req, valid)

        resp = service.decode([0x40 + uds.RequestDownload.SID, 0x20,
                               0xAB, 0xBA])
        self.assertEqual(resp['maxNumberOfBlockLength'], 0xABBA)
        print(resp)

    def test_request_upl(self):
        print('\n\nRequestUpload')
        service = uds.RequestUpload(0x1000, 0x100)
        req = service.encode()
        print(req)
        valid = [uds.RequestUpload.SID, 0, 0x22, 0x10, 0x0, 0x1, 0x0]
        self.assertEqual(req, valid)

        resp = service.decode([0x40 + uds.RequestUpload.SID, 0x20,
                               0xAB, 0xBA])
        self.assertEqual(resp['maxNumberOfBlockLength'], 0xABBA)
        print(resp)

    def test_transfer_data(self):
        print('\n\nTransferData')
        data = ['w', 'o', 'o', 'p']
        service = uds.TransferData(1, data)
        req = service.encode()
        print(req)
        valid = [uds.TransferData.SID, 1] + data
        self.assertEqual(req, valid)

        resp = service.decode([0x40 + uds.TransferData.SID, 2,
                               0xAB, 0xBA])
        self.assertEqual(resp['blockSequenceCounter'], 2)
        self.assertEqual(resp['transferResponseParameterRecord'], [0xAB, 0xBA])
        print(resp)

    def test_transfer_exit(self):
        print('\n\nTransferExit')
        data = [1, 2, 3]
        service = uds.RequestTransferExit(data)
        req = service.encode()
        print(req)
        valid = [uds.RequestTransferExit.SID] + data
        self.assertEqual(req, valid)

        resp = service.decode([0x40 + uds.RequestTransferExit.SID,
                               0xAB, 0xBA])
        self.assertEqual(resp['transferResponseParameterRecord'], [0xAB, 0xBA])
        print(resp)


if __name__ == '__main__':
    unittest.main()
