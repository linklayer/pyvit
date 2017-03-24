import unittest
from pyvit.proto import uds


class CanTest(unittest.TestCase):
    def test_nrc(self):
        resp = uds.DiagnosticSessionControl.Response()
        try:
            resp.decode([0x7F, 0x21, 0x33])
        except uds.NegativeResponseException as e:
            print('nrc:', e)

    def test_diagnostic_session_control(self):
        print('\n\nDiagnosticSessionControl')
        req = uds.DiagnosticSessionControl.Request(
            uds.DiagnosticSessionControl.
            DiagnosticSessionType.programmingSession
            )
        print(req)
        valid = [uds.DiagnosticSessionControl.SID, 0x02]
        self.assertEqual(req.encode(), valid)

        resp = uds.DiagnosticSessionControl.Response()
        resp.decode([0x40 + uds.DiagnosticSessionControl.SID, 2])
        print(resp)

    def test_ecu_reset(self):
        print('\n\nECUReset')
        req = uds.ECUReset.Request(
            uds.ECUReset.ResetType.hardReset
            )
        print(req)
        valid = [uds.ECUReset.SID, 0x1]
        self.assertEqual(req.encode(), valid)
        resp = uds.ECUReset.Response()
        resp.decode([0x40 + uds.ECUReset.SID, 2])
        print(resp)
        self.assertEqual(resp['resetType'], 2)

    def test_security_access(self):
        print('\n\nSecurityAccess')
        req = uds.SecurityAccess.Request(1)
        valid = [uds.SecurityAccess.SID, 1]
        print(req)
        self.assertEqual(req.encode(), valid)

        resp = uds.SecurityAccess.Response()
        resp.decode([0x40 + uds.SecurityAccess.SID, 1, 0x12, 0x34])
        print(resp)
        self.assertEqual(resp['securityAccessType'], 1)
        self.assertEqual(resp['securitySeed'], 0x1234)

        req = uds.SecurityAccess.Request(2, 0x1234)
        valid = [uds.SecurityAccess.SID, 2, 0x12, 0x34]
        print(req)
        self.assertEqual(req.encode(), valid)

        resp.decode([0x40 + uds.SecurityAccess.SID, 2])
        self.assertEqual(resp['securityAccessType'], 2)
        print(resp)

    def test_communication_control(self):
        print('\n\nCommunicationControl')
        req = uds.CommunicationControl.Request(
            uds.CommunicationControl.ControlType.disableRxAndTx,
            uds.CommunicationControl.CommunicationType
            .normalCommunicationMessages
        )
        valid = [uds.CommunicationControl.SID,
                 uds.CommunicationControl.ControlType.disableRxAndTx,
                 0x1]
        self.assertEqual(req.encode(), valid)

        resp = uds.CommunicationControl.Response()
        resp.decode([0x40 + uds.CommunicationControl.SID, 1])
        print(resp)
        self.assertEqual(resp['controlType'], 1)

    def test_tester_present(self):
        print('\n\nTesterPresent')
        req = uds.TesterPresent.Request()
        print(req)
        valid = [uds.TesterPresent.SID, 0]
        self.assertEqual(req.encode(), valid)

        resp = uds.TesterPresent.Response()
        print(resp)
        resp.decode([0x40 + uds.TesterPresent.SID, 0])

    def test_access_timing_parameter(self):
        print('\n\nAccessTimingParameter')
        at = (uds.AccessTimingParameter.AccessType
              .setTimingParametersToGivenValues)

        req = uds.AccessTimingParameter.Request(at, [1, 2, 3])
        print(req)
        valid = [uds.AccessTimingParameter.SID, at, 1, 2, 3]
        self.assertEqual(req.encode(), valid)

        at = (uds.AccessTimingParameter.AccessType
              .setTimingParametersToGivenValues)

        resp = uds.AccessTimingParameter.Response()
        resp.decode([0x40 + uds.AccessTimingParameter.SID, at])
        print(resp)
        self.assertEqual(resp['timingParameterAccessType'], at)

        at = (uds.AccessTimingParameter.AccessType
              .readCurrentlyActiveTimingParameters)
        req = uds.AccessTimingParameter.Request(at)
        print(req)
        valid = [uds.AccessTimingParameter.SID, at]
        self.assertEqual(req.encode(), valid)

        at = (uds.AccessTimingParameter.AccessType
              .readCurrentlyActiveTimingParameters)
        resp.decode([0x40 + uds.AccessTimingParameter.SID, at,
                     1, 2, 3])
        print(resp)
        self.assertEqual(resp['TimingParameterResponseRecord'], [1, 2, 3])
        self.assertEqual(resp['timingParameterAccessType'], at)

    def test_security_data_transmission(self):
        print('\n\nsSecuredDataTransmission')
        req = uds.SecuredDataTransmission.Request([1, 2, 3, 4])
        print(req)
        valid = [uds.SecuredDataTransmission.SID, 1, 2, 3, 4]
        self.assertEqual(req.encode(), valid)

        resp = uds.SecuredDataTransmission.Response()
        resp.decode([0x40 + uds.SecuredDataTransmission.SID,
                     1, 2, 3, 4])
        print(resp)
        self.assertEqual(resp['securityDataResponseRecord'], [1, 2, 3, 4])

    def test_control_dtc_setting(self):
        print('\n\nControlDTCSetting')
        req = uds.ControlDTCSetting.Request(uds.
                                            ControlDTCSetting.DTCSettingType.
                                            on)
        print(req)
        valid = [uds.ControlDTCSetting.SID, 1]
        self.assertEqual(req.encode(), valid)

        resp = uds.ControlDTCSetting.Response()
        resp.decode([0x40 + uds.ControlDTCSetting.SID, 2])
        print(resp)
        self.assertEqual(resp['DTCSettingType'], 2)

    def test_response_on_event(self):
        print('\n\nResponseOnEvent')
        req = uds.ResponseOnEvent.Request(uds.ResponseOnEvent.EventType
                                          .stopResponseOnEvent)
        print(req)
        valid = [uds.ResponseOnEvent.SID, 0x0, 0x02]
        self.assertEqual(req.encode(), valid)

        resp = uds.ResponseOnEvent.Response()
        resp.decode([0x40 + uds.ResponseOnEvent.SID, 2])
        print(resp)

        req = uds.ResponseOnEvent.Request(uds.ResponseOnEvent.EventType
                                          .onComparisonOfValues,
                                          event_window_time=0x10,
                                          event_type_record=[5] * 10,
                                          service_to_respond_to_record=[1,
                                                                        2,
                                                                        3])
        print(req)
        valid = [uds.ResponseOnEvent.SID, 0x07, 0x10, 5, 5, 5, 5, 5, 5, 5,
                 5, 5, 5, 1, 2, 3]
        self.assertEqual(req.encode(), valid)

        resp.decode([0x40 + uds.ResponseOnEvent.SID, 2])
        print(resp)

    def test_link_control(self):
        print('\n\nLinkControl')
        req = uds.LinkControl.Request(
            uds.LinkControl.LinkControlType.transitionBaudrate)
        print(req)
        valid = [uds.LinkControl.SID, 3]
        self.assertEqual(req.encode(), valid)

        resp = uds.LinkControl.Response()
        resp.decode([0x40 + uds.LinkControl.SID, 3])
        print(resp)
        self.assertEqual(resp['linkControlType'], 3)

        req = uds.LinkControl.Request(
            uds.LinkControl.LinkControlType.
            verifyBaudrateTransitionWithFixedBaudrate, 0xFF)
        print(req)
        valid = [uds.LinkControl.SID, 1, 0xFF]
        self.assertEqual(req.encode(), valid)

        resp.decode([0x40 + uds.LinkControl.SID, 2])
        print(resp)
        self.assertEqual(resp['linkControlType'], 2)

    def test_rdbi(self):
        print('\n\nRDBI')
        req = uds.ReadDataByIdentifier.Request(0x1234)
        print(req)
        valid = [uds.ReadDataByIdentifier.SID, 0x12, 0x34]
        self.assertEqual(req.encode(), valid)

        resp = uds.ReadDataByIdentifier.Response()
        resp.decode([0x40 + uds.ReadDataByIdentifier.SID, 0x12, 0x34,
                     1, 2, 3])
        print(resp)
        self.assertEqual(resp['dataIdentifier'], 0x1234)
        self.assertEqual(resp['dataRecord'], [1, 2, 3])

    def test_rmba(self):
        print('\n\nRMBA')
        req = uds.ReadMemoryByAddress.Request(0x12345678, 0x10)
        print(req)
        valid = [uds.ReadMemoryByAddress.SID, 0x14, 0x12, 0x34, 0x56, 0x78,
                 0x10]
        self.assertEqual(req.encode(), valid)

        resp = uds.ReadMemoryByAddress.Response()
        resp.decode([0x40 + uds.ReadMemoryByAddress.SID, 0xAA, 0xBB,
                     1, 2, 3])
        print(resp)
        self.assertEqual(resp['dataRecord'], [0xAA, 0xBB, 1, 2, 3])

    def test_read_scaling(self):
        print('\n\nRScalingDBI')
        req = uds.ReadScalingDataByIdentifier.Request(0x1234)
        print(req)
        valid = [uds.ReadScalingDataByIdentifier.SID, 0x12, 0x34]
        self.assertEqual(req.encode(), valid)

        resp = uds.ReadScalingDataByIdentifier.Response()
        resp.decode([0x40 + uds.ReadScalingDataByIdentifier.SID,
                     0xAA, 0xBB, 1, 2, 3])
        print(resp)
        self.assertEqual(resp['dataIdentifier'], 0xAABB)
        self.assertEqual(resp['scalingData'], [1, 2, 3])

    def test_read_periodic(self):
        print('\n\nRDBPeriodicI')
        req = uds.ReadDataByPeriodicIdentifier.Request(
            uds.ReadDataByPeriodicIdentifier.TransmissionMode.sendAtSlowRate,
            0xAA, 0xBB)
        print(req)
        valid = [uds.ReadDataByPeriodicIdentifier.SID, 0x1, 0xAA, 0xBB]
        self.assertEqual(req.encode(), valid)

        resp = uds.ReadDataByPeriodicIdentifier.Response()
        resp.decode([0x40 + uds.ReadDataByPeriodicIdentifier.SID])
        print(resp)

    def test_wdbi(self):
        print('\n\nWDBI')
        req = uds.WriteDataByIdentifier.Request(0xBEEF,
                                                [1, 2, 3, 4, 5, 6, 7])
        print(req)
        valid = [uds.WriteDataByIdentifier.SID, 0xBE, 0xEF,
                 1, 2, 3, 4, 5, 6, 7]
        self.assertEqual(req.encode(), valid)

        resp = uds.WriteDataByIdentifier.Response()
        resp.decode([0x40 + uds.WriteDataByIdentifier.SID,
                     0xBE, 0xEF])
        print(resp)
        self.assertEqual(resp['dataIdentifier'], 0xBEEF)

    def test_wmba(self):
        print('\n\nWMBA')
        req = uds.WriteMemoryByAddress.Request(0xBEEF, [1, 2, 3, 4, 5, 6, 7])
        print(req)
        valid = [uds.WriteMemoryByAddress.SID, 0x12, 0xBE, 0xEF, 7,
                 1, 2, 3, 4, 5, 6, 7]
        self.assertEqual(req.encode(), valid)

        resp = uds.WriteMemoryByAddress.Response()
        resp.decode([0x40 + uds.WriteMemoryByAddress.SID, 0x12,
                     0xBE, 0xEF, 7])
        print(resp)
        self.assertEqual(resp['memoryAddress'], 0xBEEF)
        self.assertEqual(resp['memorySize'], 7)

    def test_clear_dtc(self):
        print('\n\nClearDiagnosticInformation')
        req = uds.ClearDiagnosticInformation.Request(0xAABBCC)
        print(req)
        valid = [uds.ClearDiagnosticInformation.SID, 0xAA, 0xBB, 0xCC]
        self.assertEqual(req.encode(), valid)

        resp = uds.ClearDiagnosticInformation.Response()
        resp.decode([0x40 + uds.ClearDiagnosticInformation.SID])
        print(resp)

    def test_io_ctl(self):
        print('\n\nIO Control')
        req = uds.InputOutputControlByIdentifier.Request(0xABBA,
                                                         [1, 2, 3], [1, 2, 3])
        print(req)
        valid = [uds.InputOutputControlByIdentifier.SID, 0xAB, 0xBA, 1, 2, 3,
                 1, 2, 3]
        self.assertEqual(req.encode(), valid)

        resp = uds.InputOutputControlByIdentifier.Response()
        resp.decode([0x40 + uds.InputOutputControlByIdentifier.SID,
                     0xAB, 0xBA, 1, 2, 3])
        self.assertEqual(resp['dataIdentifier'], 0xABBA)
        self.assertEqual(resp['controlStatusRecord'], [1, 2, 3])
        print(resp)

    def test_routine_ctl(self):
        print('\n\nRoutine Control')
        req = uds.RoutineControl.Request(
            uds.RoutineControl.RoutineControlType.startRoutine,
            0xABBA, [1, 2, 3, 4, 5])
        print(req)
        valid = [uds.RoutineControl.SID, 0x1, 0xAB, 0xBA, 1, 2, 3, 4, 5]
        self.assertEqual(req.encode(), valid)

        resp = uds.RoutineControl.Response()
        resp.decode([0x40 + uds.RoutineControl.SID, 0x3,
                     0xAB, 0xBA, 1, 2, 3])
        self.assertEqual(resp['routineControlType'],
                         uds.RoutineControl.RoutineControlType.
                         requestRoutineResults)
        self.assertEqual(resp['routineIdentifier'], 0xABBA)
        self.assertEqual(resp['routineStatusRecord'], [1, 2, 3])
        print(resp)

    def test_request_dl(self):
        print('\n\nRequestDownload')
        req = uds.RequestDownload.Request(0x1000, 0x100)
        print(req)
        valid = [uds.RequestDownload.SID, 0, 0x22, 0x10, 0x0, 0x1, 0x0]
        self.assertEqual(req.encode(), valid)

        resp = uds.RequestDownload.Response()
        resp.decode([0x40 + uds.RequestDownload.SID, 0x20,
                     0xAB, 0xBA])
        self.assertEqual(resp['maxNumberOfBlockLength'], 0xABBA)
        print(resp)

    def test_request_upl(self):
        print('\n\nRequestUpload')
        req = uds.RequestUpload.Request(0x1000, 0x100)
        valid = [uds.RequestUpload.SID, 0, 0x22, 0x10, 0x0, 0x1, 0x0]
        self.assertEqual(req.encode(), valid)

        resp = uds.RequestUpload.Response()
        resp.decode([0x40 + uds.RequestUpload.SID, 0x20,
                     0xAB, 0xBA])
        self.assertEqual(resp['maxNumberOfBlockLength'], 0xABBA)
        print(resp)

    def test_transfer_data(self):
        print('\n\nTransferData')
        data = ['w', 'o', 'o', 'p']
        req = uds.TransferData.Request(1, data)
        print(req)
        valid = [uds.TransferData.SID, 1] + data
        self.assertEqual(req.encode(), valid)

        resp = uds.TransferData.Response()
        resp.decode([0x40 + uds.TransferData.SID, 2,
                     0xAB, 0xBA])
        self.assertEqual(resp['blockSequenceCounter'], 2)
        self.assertEqual(resp['transferResponseParameterRecord'], [0xAB, 0xBA])
        print(resp)

    def test_transfer_exit(self):
        print('\n\nTransferExit')
        data = [1, 2, 3]
        req = uds.RequestTransferExit.Request(data)
        print(req)
        valid = [uds.RequestTransferExit.SID] + data
        self.assertEqual(req.encode(), valid)

        resp = uds.RequestTransferExit.Response()
        resp.decode([0x40 + uds.RequestTransferExit.SID,
                     0xAB, 0xBA])
        self.assertEqual(resp['transferResponseParameterRecord'], [0xAB, 0xBA])
        print(resp)


if __name__ == '__main__':
    unittest.main()
