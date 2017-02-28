import operator

from pyvit.proto.isotp import IsotpInterface


class UDSParameter:
    def __init__(self, name, data):
        self.name = name
        self.data = data

        for (k, v) in data.items():
            setattr(self, k, v)

    def __dir__(self):
        # hack to make ipython completion nice
        return list(self.data.keys()) + ['to_str']

    def to_str(self, value):
        for (k, v) in self.data.items():
            if value == v:
                return k

        raise ValueError("No parameter value defined for 0x%X" % value)

    def __repr__(self):
        result = self.name + ':\n'
        for (k, v) in sorted(self.data.items(), key=operator.itemgetter(1)):
            result += '\t%s:\t0x%X\n' % (k, v)
        return result


NegativeResponse = UDSParameter('NegativeResponse', {
    'positiveResponse': 0x00,
    # 0x01 - 0x0F ISOSAEReserved
    'generalReject': 0x10,
    'serviceNotSupported': 0x11,
    'subFunctionNotSupported': 0x12,
    'incorrectMessageLengthOrInvalidFormat': 0x13,
    'responseTooLong': 0x14,
    # 0x15 - 0x20: ISOSAEReserved
    'busyRepeatRequest': 0x21,
    'conditionsNotCorrect': 0x22,
    # 0x23: ISOSAEReserved
    'requestSequenceError': 0x24,
    'noResponseFromSubnetComponent': 0x25,
    'failurePreventsExecutionOfRequestedAction': 0x26,
    # 0x27 - 0x30 ISOSAEReserved
    'requestOutOfRange': 0x31,
    # 0x32: ISOSAEReserved
    'securityAccessDenied': 0x33,
    # 0x34: ISOSAEReserved
    'invalidKey': 0x35,
    'exceedNumebrOfAttempts': 0x36,
    'requiredTimeDelayNotExpired': 0x37,
    # 0x38 – 0x4F: reservedByExtendedDataLinkSecurityDocument
    # 0x50 - 0x6F: ISOSAEReserved
    'uploadDownloadNotAccepted': 0x70,
    'transferDataSuspended': 0x71,
    'generalProgrammingFailure': 0x72,
    'wrongBlockSequenceCounter': 0x73,
    # 0x74 - 0x77: ISOSAEReserved
    'requestCorrectlyReceived-ResponsePending': 0x78,
    # 0x79 - 0x7D: ISOSAEReserved
    'subFunctionNotSupportedInActiveSession': 0x7E,
    'serviceNotSupportedInActiveSession': 0x7F,
    # 0x80: ISOSAEReserved
    'rpmTooHigh': 0x81,
    'rpmTooLow': 0x82,
    'engineIsRunning': 0x83,
    'engineIsNotRunning': 0x84,
    'engineRunTimeTooLow': 0x85,
    'temperatureTooHigh': 0x86,
    'temperatureTooLow': 0x87,
    'vehicleSpeedTooHigh': 0x88,
    'vehicleSpeedTooLow': 0x89,
    'throttle/PedalTooHigh': 0x8A,
    'throttle/PedalTooLow': 0x8B,
    'transmissionRangeNotInNeutral': 0x8C,
    'transmissionRangeNotInGear': 0x8D,
    # 0x8E: ISOSAEReserved
    'brakeSwitch(es)NotClosed': 0x8F,
    'shifterLeverNotInPark': 0x90,
    'torqueConverterClutchLocked': 0x91,
    'voltageTooHigh': 0x92,
    'voltageTooLow': 0x93,
    # 0x94 - 0xFE: reservedForSpecificConditionsNotCorrect
    # 0xFF: ISOSAEReserved
})


class NegativeResponseException(Exception):
    nrc_code = None

    def __init__(self, nrc_data):
        self.nrc_code = nrc_data[1]

    def __str__(self):
        return NegativeResponse.to_str(self.nrc_code)


class TimeoutException(Exception):
    pass


class GenericResponse(dict):
    SID = None

    def __init__(self, sid, data):
        """ Generic function for checking received data is valid. If data
        is not received, a timeout is raised. If an negative response was
        received an approproate exception is raised """

        self.SID = sid

        if data is None:
            raise TimeoutException("No data received")

        if data[0] != self.SID + 0x40:
            raise NegativeResponseException(data)


class DiagnosticSessionControl:
    """ DiagnsoticSessionControl service """
    SID = 0x10

    DiagnosticSessionType = UDSParameter('DiagnosticSessionType', {
        # 0x00: ISOASAEReserved
        'defaultSession': 0x01,
        'programmingSession': 0x02,
        'extendedDiagnosticSession': 0x03,
        'safetySystemDiagnosticSession': 0x04,
        # 0x05 - 0x3F: ISOSAEReserved
        # 0x40 - 0x5F: vehicleManufacturerSpecific
        # 0x60 - 0x7E: vehicleManufacturerSpecific
        # 0x7F: ISOASAEReserved
    })

    class Response(GenericResponse):
        def __init__(self, data):
            super().__init__(DiagnosticSessionControl.SID, data)
            self['diagnosticSessionType'] = data[1]
            self['sessionParameterRecord'] = data[2:]

    def __init__(self, diagnostic_session_type):
        self.diagnostic_session_type = diagnostic_session_type

    def encode(self):
        return [self.SID, self.diagnostic_session_type]

    def decode(self, data):
        return self.Response(data)


class ECUReset:
    """ ECUReset service """
    SID = 0x11

    ResetType = UDSParameter('ResetType', {
        # 0x00: ISOASAEReserved
        'hardReset': 0x01,
        'keyOffOnReset': 0x02,
        'softReset': 0x03,
        'enableRapidPowerShutDown': 0x04,
        'disableRapidPowerShutDown': 0x05
        # 0x06 - 0x3F: ISOSAEReserved
        # 0x40 - 0x5F: vehicleManufacturerSpecific
        # 0x60 - 0x7E: vehicleManufacturerSpecific
        # 0x7F: ISOASAEReserved
        })

    def __init__(self, reset_type):
        self.reset_type = reset_type

    def encode(self):
        return [self.SID, self.reset_type]

    def decode(self, data):
        # TODO
        return None


class SecurityAccess:
    """ SecurityAccess service """
    SID = 0x27

    def __init__(self):
        raise NotImplementedError("Service not implemented.")


class CommunicationControl:
    """ CommunicationControl service """
    SID = 0x28

    def __init__(self):
        raise NotImplementedError("Service not implemented.")


class TesterPresent:
    """ TesterPresent service """
    SID = 0x3E

    def __init__(self):
        raise NotImplementedError("Service not implemented.")


class AccessTimingParameter:
    """ AccessTimingParameter service """
    SID = 0x83

    def __init__(self):
        raise NotImplementedError("Service not implemented.")


class SecuredDataTransmission:
    """ SecuredDataTransmission service """
    SID = 0x84

    def __init__(self):
        raise NotImplementedError("Service not implemented.")


class ControlDTCSetting:
    """ ControlDTCSetting service """
    SID = 0x85

    def __init__(self):
        raise NotImplementedError("Service not implemented.")


class ResponseOnEvent:
    """ ResponseOnEvent service """
    SID = 0x86

    def __init__(self):
        raise NotImplementedError("Service not implemented.")


class LinkControl:
    """ ResponseOnEvent service """
    SID = 0x87

    def __init__(self):
        raise NotImplementedError("Service not implemented.")


class ReadDataByIdentifier:
    """ ReadDataByIdentifier service """
    SID = 0x22

    def __init__(self):
        raise NotImplementedError("Service not implemented.")


class ReadMemoryByAddress:
    """ ReadMemoryByAddress service """
    SID = 0x23

    def __init__(self):
        raise NotImplementedError("Service not implemented.")


class ReadScalingDataByIdentifier:
    """ ReadScalingDataByIdentifier service """
    SID = 0x24

    def __init__(self):
        raise NotImplementedError("Service not implemented.")


class ReadDataByPeriodicIdentifier:
    """ ReadDataByPeriodicIdentifier service """
    SID = 0x2A

    def __init__(self):
        raise NotImplementedError("Service not implemented.")


class DynamicallyDefineDataIdentifier:
    """ DynamicallyDefineDataIdentifier service """
    SID = 0x2C

    def __init__(self):
        raise NotImplementedError("Service not implemented.")


class WriteDataByIdentifier:
    """ WriteDataByIdentifier service """
    SID = 0x2E

    def __init__(self):
        raise NotImplementedError("Service not implemented.")


class WriteMemoryByAddress:
    """ WriteMemoryByAddress service """
    SID = 0x3D

    def __init__(self):
        raise NotImplementedError("Service not implemented.")


class ClearDiagnosticInformation:
    """ ClearDiagnosticInformation service """
    SID = 0x14

    def __init__(self):
        raise NotImplementedError("Service not implemented.")


class ReadDTCInformation:
    """ WriteMemoryByAddress service """
    SID = 0x19

    def __init__(self):
        raise NotImplementedError("Service not implemented.")


class InputOutputControlByIdentifier:
    """ InputOutputControlByIdentifier service """
    SID = 0x2F

    def __init__(self):
        raise NotImplementedError("Service not implemented.")


class RoutineControl:
    """ RoutineControl service """
    SID = 0x31

    def __init__(self):
        raise NotImplementedError("Service not implemented.")


class RequestDownload:
    """ RequestDownload service """
    SID = 0x34

    def __init__(self):
        raise NotImplementedError("Service not implemented.")


class RequestUpload:
    """ RequestUpload service """
    SID = 0x35

    def __init__(self):
        raise NotImplementedError("Service not implemented.")


class TransferData:
    """ TransferData service """
    SID = 0x36

    def __init__(self):
        raise NotImplementedError("Service not implemented.")


class RequestTransferExit:
    """ RequestTransferExit service """
    SID = 0x37

    def __init__(self):
        raise NotImplementedError("Service not implemented.")


class UDSInterface(IsotpInterface):
    def __init__(self, dispatcher, tx_arb_id=0x7E0, rx_arb_id=0x7E8):
        super().__init__(dispatcher, tx_arb_id, rx_arb_id)

    def request(self, service, timeout=0.5):
        self.send(service.encode())
        data = self.recv(timeout=timeout)
        return service.decode(data)
