import operator
import time
import sys

from math import log

from pyvit.proto.isotpAddressing import N_TAtype, IsotpNormalAddressing, IsotpNormalFixedAddressing
from pyvit.dispatch import Dispatcher


def _byte_size(value):
    # return the number of bytes needed to represent a value
    if value == 0:
        return 1
    else:
        return int(log(value, 256)) + 1


def _to_bytes(value, padding=0):
    # convert value to byte array, MSB first
    res = []

    # return an empty list for NoneType
    if value is None:
        return []

    while value > 0:
        res = [value & 0xFF] + res
        value = value >> 8

    # add '0' padding to the front of the list if specified
    while padding > 0:
        res = [0x00] + res
        padding -= 1

    return res


def _from_bytes(bs):
    # convert byte array to value, MSB first
    res = 0
    for b in bs:
        res = res << 8
        res += b

    return res


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
    # 0x38 - 0x4F: reservedByExtendedDataLinkSecurityDocument
    # 0x50 - 0x6F: ISOSAEReserved
    'uploadDownloadNotAccepted': 0x70,
    'transferDataSuspended': 0x71,
    'generalProgrammingFailure': 0x72,
    'wrongBlockSequenceCounter': 0x73,
    # 0x74 - 0x77: ISOSAEReserved
    'responsePending': 0x78,
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

    @staticmethod
    def factory(nrc_data):
        """
        For certain nrc_codes we have specific exception defined, this is a factory pattern which
        instantiate the right exception class depending of the nrc_code of the negative response
        :param nrc_data:
        :return:
        """
        try:
            nrc_class_name = NegativeResponseException.negativeExceptionClassName(nrc_data[2])
            thismodule = sys.modules[__name__]
            specific_except_class = getattr(thismodule,nrc_class_name)
            return specific_except_class(nrc_data)
        except (NameError,AttributeError):
            # Class does not exists for the exception, use general one
            return NegativeResponseException(nrc_data)

    def __init__(self, nrc_data):
        self.sid = nrc_data[1]
        self.nrc_code = nrc_data[2]

    def __str__(self):
        return 'NRC: SID = 0x%X: %s' % (self.sid,
                                        NegativeResponse.to_str(self.nrc_code))

    @classmethod
    def negativeExceptionClassName(self, nrc_code):
        try:
            nrc_name = NegativeResponse.to_str(nrc_code)
        except ValueError:
            # Not able to identify a specific class for the negative response, use general one
            return 'NegativeResponseException'
        return nrc_name[:1].upper() + nrc_name[1:] + 'Exception'

class ResponsePendingException(NegativeResponseException):
    """
    This negative response type says to the client that the server is still computing the response, just wait more
    """
    timeout = 0

    def __init__(self, nrc_data):
        super().__init__(nrc_data)
        # with these kind of negative response the server request the P2extende timeout to wait for the pendind response, see ISO 14229-1:2013
        # the maximum value for this parameter is 5000ms (5s), usually the exact one is comunicated in the response of the diagnosticSessionControl request
        self.timeout = 5

class SecurityAccessDeniedException(NegativeResponseException):
    pass

class ServiceNotSupportedException(NegativeResponseException):
    pass

class SubFunctionNotSupportedInActiveSessionException(NegativeResponseException):
    pass

class ServiceNotSupportedInActiveSessionException(NegativeResponseException):
    pass

class SubFunctionNotSupportedException(NegativeResponseException):
    pass

class TimeoutException(Exception):
    pass


class GenericRequest(dict):
    SID = None
    service_name = None

    def __init__(self, name, sid):
        self.SID = sid
        self.name = name

    def _check_sid(self, data):
        if data[0] != self.SID:
            raise ValueError('Invalid SID for service'
                             '(got 0x%X, expected 0x%X)' %
                             (data[0], self.SID))

    def __str__(self):
        return '%s Request: %s' % (self.name, super(GenericRequest,
                                                    self).__str__())


class GenericResponse(dict):
    SID = None
    service_name = None

    def __init__(self, name, sid):
        self.SID = sid
        self.name = name

    def _check_nrc(self, data):
        """ Generic function for checking received data is valid. If data
        is not received, a timeout is raised. If an negative response was
        received an appropriate exception is raised """

        if data is None:
            raise TimeoutException("No data received")

        if data[0] == 0x7F:
            raise NegativeResponseException.factory(data)
        elif data[0] != self.SID + 0x40:
            raise ValueError('Invalid SID for service'
                             '(got 0x%X, expected 0x%X)' %
                             (data[0] + 0x40, self.SID + 0x40))

    def __str__(self):
        return '%s Response: %s' % (self.name, super(GenericResponse,
                                                     self).__str__())


class DiagnosticSessionControl:
    """ DiagnosticSessionControl service """
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
        def __init__(self):
            super(DiagnosticSessionControl.Response, self).__init__(
                'DiagnosticSessionControl',
                DiagnosticSessionControl.SID)

        def decode(self, data):
            self._check_nrc(data)
            try:
                self['diagnosticSessionType'] = data[1]
                self['sessionParameterRecord'] = data[2:]
            except IndexError:
                # I found on an Opel Corsa a positive response which does not include those info
                # clearly wrong according to the standard but it happens
                self['diagnosticSessionType'] = ""
                self['sessionParameterRecord'] = ""

    class Request(GenericRequest):
        def __init__(self, diagnostic_session_type=None):
            super(DiagnosticSessionControl.Request, self).__init__(
                'DiagnosticSessionControl',
                DiagnosticSessionControl.SID)
            self['diagnosticSessionType'] = diagnostic_session_type

        def encode(self):
            return [self.SID, self['diagnosticSessionType']]

        def decode(self, data):
            self._check_sid(data)
            self['diagnosticSessionType'] = data[1]


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

    class Response(GenericResponse):
        def __init__(self):
            super(ECUReset.Response, self).__init__('ECUReset', ECUReset.SID)

        def decode(self, data):
            self._check_nrc(data)
            self['resetType'] = data[1]

            # powerDownTime only present for enableRapidPowerShutDown
            if (self['resetType'] ==
                    ECUReset.ResetType.enableRapidPowerShutDown):
                self['powerDownTime'] = data[2]

    class Request(GenericRequest):
        def __init__(self, reset_type=0):
            super(ECUReset.Request, self).__init__('ECUReset', ECUReset.SID)
            self['resetType'] = reset_type

        def encode(self):
            return [self.SID, self['resetType']]

        def decode(self, data):
            self._check_sid(data)
            self['resetType'] = data[1]


class SecurityAccess:
    """ SecurityAccess service """
    SID = 0x27

    class Response(GenericResponse):
        def __init__(self):
            super(SecurityAccess.Response, self).__init__('SecurityAccess',
                                                          SecurityAccess.SID)

        def decode(self, data):
            self._check_nrc(data)
            self['securityAccessType'] = data[1]

            # securitySeed is only present for seed requests, which are odd
            # values of securityAccessType
            if self['securityAccessType'] % 2 == 1:
                self['securitySeed'] = _from_bytes(data[2:])

    class Request(GenericRequest):
        def __init__(self, security_access_type=0, security_key=None):
            super(SecurityAccess.Request, self).__init__('SecurityAccess',
                                                         SecurityAccess.SID)
            self['securityAccessType'] = security_access_type
            self['securityKey'] = security_key

        def encode(self):
            return ([self.SID, self['securityAccessType']] +
                    _to_bytes(self['securityKey']))

        def decode(self, data):
            self._check_sid(data)
            self['securityAccessType'] = data[1]
            self['securityKey'] = _from_bytes(data[2:])


class CommunicationControl:
    """ CommunicationControl service """
    SID = 0x28

    ControlType = UDSParameter('ControlType', {
        'enableRxAndTx': 0x00,
        'enableRxAndDisableTx': 0x01,
        'disableRxandEnableTx': 0x02,
        'disableRxAndTx': 0x03,
        'enableRxAndDisableTxWithEnhancedAddressInformation': 0x4,
        'enableRxAndTxWithEnhancedAddressInformation': 0x5,
        # 0x06 - 0x3F: ISOSAEReserved
        # 0x40 - 0x5F: vehicleManufacturerSpecific
        # 0x60 - 0x7E: vehicleManufacturerSpecific
        # 0x7F: ISOASAEReserved
        })

    CommunicationType = UDSParameter('CommunicationType', {
        # Bit encoded parameter, B.1 of ISO14229
        # bits 0-1:
        # 0b00: ISOSAEReserved
        # 0b01: normalCommunicationMessages
        # 0b10: networkManagementCommunicationMessages
        # 0b11: networkManagementCommunicationMessages and
        #       normalCommunicationMessages
        # bits 2-3: ISOSAEReserved
        'normalCommunicationMessages': 0b01,
        'networkManagementCommunicationMessages': 0b10,
        'networkManagementCommunicationMessagesANDnormalCommunicationMessages': 0b11,
        })

    class Response(GenericResponse):
        def __init__(self):
            super(CommunicationControl.Response, self).__init__(
                'CommunicationControl',
                CommunicationControl.SID)

        def decode(self, data):
            self._check_nrc(data)
            self['controlType'] = data[1]

    class Request(GenericRequest):
        def  __init__(self, control_type=0, communication_type=0,
                     network_number=0):
            super(CommunicationControl.Request, self).__init__(
                'CommunicationControl',
                CommunicationControl.SID)
            self['controlType'] = control_type
            self['communicationType'] = communication_type
            self['networkNumber'] = network_number

        def encode(self):
            # communicationType lower nybble is the type of communication.
            # upper nybble is which network to disable/enable, where 0x0
            # specifies all networks, 0xF specifies network the message was
            # received on, and 0x01-0x0E specify a network by network number
            return [self.SID, self['controlType'],
                    self['communicationType'] + (self['networkNumber'] << 4)]

        def decode(self, data):
            self._check_sid(data)
            self['controlType'] = data[1]
            self['communicationType'] = data[2] & 0xF
            self['networkNumber'] = data[2] >> 4


class TesterPresent:
    """ TesterPresent service """
    SID = 0x3E

    ZeroSubFunction = UDSParameter('ZeroSubFunction', {
        'requestPosRspMsg': 0x00,
        'suppressPosRspMsg': 0x80,
        })

    class Response(GenericResponse):
        def __init__(self):
            super(TesterPresent.Response, self).__init__('TesterPresent',
                                                         TesterPresent.SID)

        def decode(self, data):
            self._check_nrc(data)

    class Request(GenericRequest):
        def __init__(self, suppress_response=False):
            super(TesterPresent.Request, self).__init__('TesterPresent',
                                                        TesterPresent.SID)
            if suppress_response:
                self['subFunction'] = TesterPresent.ZeroSubFunction.suppressPosRspMsg
            else:
                self['subFunction'] = TesterPresent.ZeroSubFunction.requestPosRspMsg

        def encode(self):
            return [self.SID, self['subFunction']]

        def decode(self, data):
            self._check_sid(data)


class AccessTimingParameter:
    """ AccessTimingParameter service """
    SID = 0x83

    AccessType = UDSParameter('AccessType', {
       # 0x00: ISOASAEReserved
       'readExtendedTimingParameterSet': 0x01,
       'setTimingParametersToDefaultValues': 0x02,
       'readCurrentlyActiveTimingParameters': 0x03,
       'setTimingParametersToGivenValues': 0x04,
       # 0x05 - 0xFF: ISOSAEReserved
    })

    class Response(GenericResponse):
        def __init__(self):
            super(AccessTimingParameter.Response, self).__init__(
                'AccessTimingParameter',
                AccessTimingParameter.SID)

        def decode(self, data):
            self._check_nrc(data)
            self['timingParameterAccessType'] = data[1]
            if (self['timingParameterAccessType'] ==
                AccessTimingParameter.AccessType
                    .readExtendedTimingParameterSet or
                self['timingParameterAccessType'] ==
                AccessTimingParameter.AccessType
                    .readCurrentlyActiveTimingParameters):
                self['TimingParameterResponseRecord'] = data[2:]

    class Request(GenericRequest):
        def __init__(self, access_type=0, request_record=None):
            super(AccessTimingParameter.Request, self).__init__(
                'AccessTimingParameter',
                AccessTimingParameter.SID)
            self['accessType'] = access_type
            self['requestRecord'] = request_record

        def encode(self):
            result = [self.SID, self['accessType']]

            # TimingParameterRequestRecord is present only when
            # timingParameterAccessType = setTimingParametersToGivenValues
            if (self['accessType'] ==
                AccessTimingParameter.AccessType.
                    setTimingParametersToGivenValues):
                result += self['requestRecord']

            return result

        def decode(self, data):
            self._check_sid(data)
            self['accessType'] = data[1]
            self['requestRecord'] = data[2:]


class SecuredDataTransmission:
    """ SecuredDataTransmission service """
    SID = 0x84

    class Response(GenericResponse):
        def __init__(self):
            super(SecuredDataTransmission.Response, self).__init__(
                'SecuredDataTransmission',
                SecuredDataTransmission.SID)

        def decode(self, data):
            self._check_nrc(data)
            self['securityDataResponseRecord'] = data[1:]

    class Request(GenericRequest):
        def __init__(self, data_record=None):
            super(SecuredDataTransmission.Request, self).__init__(
                'SecuredDataTransmission',
                SecuredDataTransmission.SID)
            self['dataRecord'] = data_record

        def encode(self):
            return [self.SID] + self['dataRecord']

        def decode(self, data):
            self._check_sid(data)
            self['dataRecord'] = data[1:]


class ControlDTCSetting:
    """ ControlDTCSetting service """
    SID = 0x85

    DTCSettingType = UDSParameter('DTCSettingType', {
        # 0x00: ISOASAEReserved
        'on': 0x01,
        'off': 0x02,
        # 0x03 - 0x3F: ISOSAEReserved
        # 0x40 - 0x5F: vehicleManufacturerSpecific
        # 0x60 - 0x7E: vehicleManufacturerSpecific
        # 0x05 - 0xFF: ISOSAEReserved
    })

    class Response(GenericResponse):
        def __init__(self):
            super(ControlDTCSetting.Response, self).__init__(
                'ControlDTCSetting',
                ControlDTCSetting.SID)

        def decode(self, data):
            self._check_nrc(data)
            self['DTCSettingType'] = data[1]

    class Request(GenericRequest):
        def __init__(self, dtc_setting_type=0,
                     dtc_setting_control_option_record=None):
            super(ControlDTCSetting.Request, self).__init__(
                'ControlDTCSetting',
                ControlDTCSetting.SID)
            if dtc_setting_control_option_record is None:
                dtc_setting_control_option_record = []
            self['DTCSettingType'] = dtc_setting_type
            self['DTCSettingControlOptionRecord'] = (
                dtc_setting_control_option_record)

        def encode(self):
            return ([self.SID, self['DTCSettingType']] +
                    self['DTCSettingControlOptionRecord'])

        def decode(self, data):
            self._check_sid(data)
            self['DTCSettingType'] = data[1]
            self['DTCSettingControlOptionRecord'] = data[2:]


class ResponseOnEvent:
    """ ResponseOnEvent service """
    SID = 0x86

    EventType = UDSParameter('EventType', {
        'stopResponseOnEvent': 0x00,
        'onDTCStatusChange': 0x01,
        'onTimerInterrupt': 0x02,
        'onChangeOfDataIdentifier': 0x03,
        'reportActivatedEvents': 0x04,
        'startResponseOnEvent': 0x05,
        'clearResponseOnEvent': 0x06,
        'onComparisonOfValues': 0x07,
        # 0x08 - 0x1F: ISOSAEReserved
        # 0x20 - 0x2F: vehicleManufacturerSpecific
        # 0x30 - 0x3E: vehicleManufacturerSpecific
        # 0x3F: ISOSAEReserved
        # bit 6 is store/doNotStore flag
    })

    class Response(GenericResponse):
        def __init__(self):
            super(ResponseOnEvent.Response, self).__init__('ResponseOnEvent',
                                                           ResponseOnEvent.SID)

        def decode(self, data):
            self._check_nrc(data)
            # TODO
            self['data'] = data

    class Request(GenericRequest):
        def __init__(self, event_type=0, event_window_time=0x02,
                     event_type_record=None, service_to_respond_to_record=None):
            super(ResponseOnEvent.Request, self).__init__(
                'ResponseOnEvent',
                ResponseOnEvent.SID)
            if event_type_record is None:
                event_type_record = []
            if service_to_respond_to_record is None:
                service_to_respond_to_record = []
            # validate eventTypeRecord length for each eventType
            if (event_type == ResponseOnEvent.EventType.stopResponseOnEvent and
                    len(event_type_record) != 0):
                raise ValueError('Invalid eventTypeRecord length')
            elif (event_type == ResponseOnEvent.EventType.onDTCStatusChange and
                    len(event_type_record) != 1):
                raise ValueError('Invalid eventTypeRecord length')
            elif (event_type == ResponseOnEvent.EventType.onTimerInterrupt and
                    len(event_type_record) != 1):
                raise ValueError('Invalid eventTypeRecord length')
            elif (event_type == ResponseOnEvent.EventType.
                  onChangeOfDataIdentifier and len(event_type_record) != 2):
                raise ValueError('Invalid eventTypeRecord length')
            elif (event_type == ResponseOnEvent.EventType.
                  reportActivatedEvents and len(event_type_record) != 0):
                raise ValueError('Invalid eventTypeRecord length')
            elif (event_type == ResponseOnEvent.EventType.
                  startResponseOnEvent and len(event_type_record) != 0):
                raise ValueError('Invalid eventTypeRecord length')
            elif (event_type == ResponseOnEvent.EventType.
                  clearResponseOnEvent and len(event_type_record) != 0):
                raise ValueError('Invalid eventTypeRecord length')
            elif (event_type == ResponseOnEvent.EventType.
                  onComparisonOfValues and len(event_type_record) != 10):
                raise ValueError('Invalid eventTypeRecord length')

            self['eventType'] = event_type
            # event_window_type defaults to 0x02, specifying infinite time
            self['eventWindowTime'] = event_window_time
            self['eventTypeRecord'] = event_type_record
            self['serviceToRespondToRecord'] = service_to_respond_to_record

        def encode(self):
            return ([self.SID, self['eventType'], self['eventWindowTime']] +
                    self['eventTypeRecord'] + self['serviceToRespondToRecord'])

        def decode(self, data):
            self._check_sid(data)
            self['eventType'] = data[1]
            self['eventWindowTime'] = data[2]

            if (self['eventType'] ==
                    ResponseOnEvent.EventType.stopResponseOnEvent):
                event_type_record_len = 0
            elif (self['eventType'] ==
                  ResponseOnEvent.EventType.onDTCStatusChange):
                event_type_record_len = 1
            elif (self['eventType'] ==
                  ResponseOnEvent.EventType.onTimerInterrupt):
                event_type_record_len = 1
            elif (self['eventType'] ==
                  ResponseOnEvent.EventType.onChangeOfDataIdentifier):
                event_type_record_len = 2
            elif (self['eventType'] ==
                  ResponseOnEvent.EventType.reportActivatedEvents):
                event_type_record_len = 0
            elif (self['eventType'] ==
                  ResponseOnEvent.EventType.startResponseOnEvent):
                event_type_record_len = 0
            elif (self['eventType'] ==
                  ResponseOnEvent.EventType.clearResponseOnEvent):
                event_type_record_len = 0
            elif (self['eventType'] ==
                  ResponseOnEvent.EventType.onComparisonOfValues):
                event_type_record_len = 10

            self['eventTypeRecord'] = data[3: 3 + event_type_length]
            try:
                self['serviceToRespondToRecord'] = data[3 + event_type_length:
                                                        3 + event_type_length +
                                                        event_type_record_len]
            except IndexError:
                self['serviceToRespondToRecord'] = None


class LinkControl:
    """ LinkControl service """
    SID = 0x87

    LinkControlType = UDSParameter('LinkControlType', {
        # 0x0: ISOSAEReserved
        'verifyBaudrateTransitionWithFixedBaudrate': 0x01,
        'verifyBaudrateTransitionWithSpecificBaudrate': 0x02,
        'transitionBaudrate': 0x03,
        # 0x04 - 0x3F: ISOSAEReserved
        # 0x40 - 0x5F: vehicleManufacturerSpecific
        # 0x60 - 0x7E: vehicleManufacturerSpecific
        # 0x7F: ISOSAEReserved
    })

    BaudrateIdentifier = UDSParameter('BaudrateIdentifier', {
        # B.3 of ISO14229
        # 0x0: ISOSAEReserved
        'PC9600Baud': 0x01,
        'PC19200Baud': 0x02,
        'PC38400Baud': 0x03,
        'PC57600Baud': 0x04,
        'PC115200Baud': 0x05,
        # 0x06 - 0x0F: ISOSAEReserved
        'CAN125000Baud': 0x10,
        'CAN250000Baud': 0x11,
        'CAN500000Baud': 0x12,
        'CAN1000000Baud': 0x13,
        # 0x14 - 0xFF: ISOSAEReserved
    })

    class Response(GenericResponse):
        def __init__(self):
            super(LinkControl.Response, self).__init__('LinkControl',
                                                       LinkControl.SID)

        def decode(self, data):
            self._check_nrc(data)
            self['linkControlType'] = data[1]

    class Request(GenericRequest):
        def __init__(self, link_control_type=0, link_baudrate_record=None):
            super(LinkControl.Request, self).__init__('LinkControl',
                                                      LinkControl.SID)
            self['linkControlType'] = link_control_type

            if link_baudrate_record is None:
                link_baudrate_record = []

            # baudrate can be a bit/s value (FixedBaudrate)
            # or a baudrateIdentifier (SpecificBaudrate)
            # validate and convert to an array of bytes
            if (link_control_type ==
                LinkControl.LinkControlType.
                    verifyBaudrateTransitionWithFixedBaudrate):
                if link_baudrate_record > 0xFF:
                    raise ValueError('Invalid fixed baudrate')
                else:
                    self['linkBaudrateRecord'] = [link_baudrate_record]
            elif (link_control_type ==
                  LinkControl.LinkControlType.
                    verifyBaudrateTransitionWithSpecificBaudrate):
                if link_baudrate_record > 0xFFFFFF:
                    raise ValueError('Invalid specific baudrate')
                else:
                    self['linkBaudrateRecord'] = [baudrate >> 16,
                                                  (baudrate >> 8) & 0xFF,
                                                  baudrate & 0xFF]
            else:
                self['linkBaudrateRecord'] = link_baudrate_record

        def encode(self):
            return ([self.SID, self['linkControlType']] +
                    self['linkBaudrateRecord'])

        def decode(self, data):
            self._check_sid(data)
            self['linkControlType'] = data[1]
            self['linkBaudrateRecord'] = data[2:]


class ReadDataByIdentifier:
    """ ReadDataByIdentifier service """
    # NB: this currently only supports reading one DID at a time
    SID = 0x22

    class Response(GenericResponse):
        def __init__(self):
            super(ReadDataByIdentifier.Response, self).__init__(
                'ReadDataByIdentifier',
                ReadDataByIdentifier.SID)

        def decode(self, data):
            self._check_nrc(data)
            self['dataIdentifier'] = (data[1] << 8) + data[2]
            self['dataRecord'] = data[3:]
            self['dataRecordASCII'] = ''.join(chr(i) for i in self['dataRecord'])

    class Request(GenericRequest):
        def __init__(self, data_identifier=0):
            super(ReadDataByIdentifier.Request, self).__init__(
                'ReadDataByIdentifier',
                ReadDataByIdentifier.SID)
            if data_identifier < 0 or data_identifier > 0xFFFF:
                raise ValueError('Invalid dataIdentifier, '
                                 'must be > 0 and < 0xFFFF')
            self['dataIdentifier'] = data_identifier

        def encode(self):
            return [self.SID,
                    self['dataIdentifier'] >> 8,
                    self['dataIdentifier'] & 0xFF]

        def decode(self, data):
            self._check_sid(data)
            self['dataIdentifier'] = _from_bytes(data[1:3])


class ReadMemoryByAddress:
    """ ReadMemoryByAddress service """
    SID = 0x23

    class Response(GenericResponse):
        def __init__(self):
            super(ReadMemoryByAddress.Response, self).__init__(
                'ReadMemoryByAddress',
                ReadMemoryByAddress.SID)

        def decode(self, data):
            self._check_nrc(data)
            self['dataRecord'] = data[1:]

    class Request(GenericRequest):
        def __init__(self, memory_address=0, memory_size=0):
            super(ReadMemoryByAddress.Request, self).__init__(
                'ReadMemoryByAddress',
                ReadMemoryByAddress.SID)
            self['memoryAddress'] = memory_address
            self['memorySize'] = memory_size

        def encode(self):
            # addressAndLengthFormatIdentifier specifies length of
            # address and size
            # uppper nybble is byte length of size
            # lower nybble is byte length of address
            format_identifier = ((_byte_size(self['memorySize']) << 4) +
                                 _byte_size(self['memoryAddress']))

            return ([self.SID, format_identifier] +
                    _to_bytes(self['memoryAddress']) +
                    _to_bytes(self['memorySize']))

        def decode(self, data):
            self._check_sid(data)
            memory_size_size = data[1] >> 4
            memory_address_size = data[1] & 0x0F
            self['memoryAddress'] = _from_bytes(data[2:
                                                     2 + memory_address_size])
            self['memorySize'] = _from_bytes(data[2 + memory_address_size:
                                                  2 + memory_address_size +
                                                  memory_size_size])


class ReadScalingDataByIdentifier:
    """ ReadScalingDataByIdentifier service """
    SID = 0x24

    class Response(GenericResponse):
        def __init__(self):
            super(ReadScalingDataByIdentifier.Response, self).__init__(
                'ReadScalingDataByIdentifier',
                ReadScalingDataByIdentifier.SID)

        def decode(self, data):
            self._check_nrc(data)
            self['dataIdentifier'] = (data[1] << 8) + data[2]
            # TODO, decode more specifically
            self['scalingData'] = data[3:]

    class Request(GenericRequest):
        def __init__(self, data_identifier):
            super(ReadScalingDataByIdentifier.Request, self).__init__(
                'ReadScalingDataByIdentifier',
                ReadScalingDataByIdentifier.SID)
            if data_identifier < 0 or data_identifier > 0xFFFF:
                raise ValueError('Invalid dataIdentifier, '
                                 'must be > 0 and < 0xFFFF')
            self['dataIdentifier'] = data_identifier

        def encode(self):
            return [self.SID,
                    (self['dataIdentifier'] >> 8),
                    self['dataIdentifier'] & 0xFF]

        def decode(self, data):
            self.check_sid(data)
            self['dataIdentifier'] = _from_bytes(data[1:3])


class ReadDataByPeriodicIdentifier:
    """ ReadDataByPeriodicIdentifier service """
    SID = 0x2A

    TransmissionMode = UDSParameter('TransmissionMode', {
        # 0x00: ISOASAEReserved
        'sendAtSlowRate': 0x01,
        'sendAtMediumRate': 0x02,
        'sendAtFastRate': 0x03,
        'stopSending': 0x04,
        # 0x05 - 0xFF: ISOSAEReserved
        })

    class Response(GenericResponse):
        def __init__(self):
            super(ReadDataByPeriodicIdentifier.Response, self).__init__(
                'ReadDataByPeriodicIdentifier',
                ReadDataByPeriodicIdentifier.SID)

        def decode(self, data):
            self._check_nrc(data)
            # this response has a periodic response, in one of two formats
            # we can't know what format the server uses, so return data
            # unformatted
            self['periodicReponse'] = data[1:]

    class Request(GenericRequest):
        def __init__(self, transmission_mode=1, *data_identifiers):
            super(ReadDataByPeriodicIdentifier.Request, self).__init__(
                'ReadDataByPeriodicIdentifier',
                ReadDataByPeriodicIdentifier.SID)
            if transmission_mode < 1 or transmission_mode > 4:
                raise ValueError('Invalid transmission mode')

            if (transmission_mode != ReadDataByPeriodicIdentifier.
                TransmissionMode.stopSending and len(data_identifiers) ==
                    0):
                raise ValueError('At least one dataIdentifier must be '
                                 'provided for this transmission mode')
            self['transmissionMode'] = transmission_mode
            self['dataIdentifiers'] = list(data_identifiers)

        def encode(self):
            return ([self.SID, self['transmissionMode']] +
                    self['dataIdentifiers'])

        def decode(self, data):
            self._check_sid(data)
            self['transmissionMode'] = data[1]
            self['dataIdentifiers'] = data[2:]


class DynamicallyDefineDataIdentifier:
    """ DynamicallyDefineDataIdentifier service """
    SID = 0x2C

    class Response(GenericResponse):
        def __init__(self):
            raise NotImplementedError("Service not implemented.")

    class Request(GenericRequest):
        def __init__(self):
            raise NotImplementedError("Service not implemented.")


class WriteDataByIdentifier:
    """ WriteDataByIdentifier service """
    SID = 0x2E

    class Response(GenericResponse):
        def __init__(self):
            super(WriteDataByIdentifier.Response, self).__init__(
                'WriteDataByIdentifier',
                WriteDataByIdentifier.SID)

        def decode(self, data):
            self._check_nrc(data)
            self['dataIdentifier'] = _from_bytes(data[1:3])

    class Request(GenericRequest):
        def __init__(self, data_identifier=0, data_record=None):
            super(WriteDataByIdentifier.Request, self).__init__(
                'WriteDataByIdentifier',
                WriteDataByIdentifier.SID)

            if data_identifier < 0 or data_identifier > 0xFFFF:
                raise ValueError('Invalid dataIdentifier, '
                                 'must be > 0 and < 0xFFFF')
            self['dataIdentifier'] = data_identifier
            self['dataRecord'] = data_record

        def encode(self):
            return ([self.SID] + _to_bytes(self['dataIdentifier']) +
                    self['dataRecord'])

        def decode(self, data):
            self._check_sid(data)
            self['dataIdentifier'] = _from_bytes(data[1:3])
            self['dataRecord'] = _from_bytes(data[3:])


class WriteMemoryByAddress:
    """ WriteMemoryByAddress service """
    SID = 0x3D

    class Response(GenericResponse):
        def __init__(self):
            super(WriteMemoryByAddress.Response, self).__init__(
                'WriteMemoryByAddress',
                WriteMemoryByAddress.SID)

        def decode(self, data):
            self._check_nrc(data)
            format_identifier = data[1]
            # get parameter lengts from format identifier
            addr_bytes = format_identifier & 0x0F
            size_bytes = format_identifier >> 4

            self['memoryAddress'] = _from_bytes(data[2: 2 + addr_bytes])
            self['memorySize'] = _from_bytes(data[2 + addr_bytes:
                                                  2 + addr_bytes + size_bytes])

    class Request(GenericRequest):
        def __init__(self, memory_address=0, data_record=None,
                     memory_size=None):
            super(WriteMemoryByAddress.Request, self).__init__(
                'WriteMemoryByAddress',
                WriteMemoryByAddress.SID)
            self['memoryAddress'] = memory_address
            self['dataRecord'] = data_record
            if memory_size is None:
                self['memorySize'] = len(data_record)
            else:
                self['memorySize'] = memory_size

        def encode(self):
            # addressAndLengthFormatIdentifier specifies length of address and
            # size
            # uppper nybble is byte length of size
            # lower nybble is byte length of address
            format_identifier = ((_byte_size(self['memorySize']) << 4) +
                                 _byte_size(self['memoryAddress']))

            return ([self.SID, format_identifier] +
                    _to_bytes(self['memoryAddress']) +
                    _to_bytes(self['memorySize']) +
                    self['dataRecord'])

        def decode(self, data):
            addr_bytes = format_identifier & 0x0F
            size_bytes = format_identifier >> 4
            self['memoryAddress'] = _from_bytes(data[2: 2 + addr_bytes])
            self['memorySize'] = _from_bytes(data[2 + addr_bytes:
                                                  2 + addr_bytes + size_bytes])
            self['dataRecord'] = data[2 + addr_bytes + size_bytes:]


class ClearDiagnosticInformation:
    """ ClearDiagnosticInformation service """
    SID = 0x14

    class Response(GenericResponse):
        def __init__(self):
            super(ClearDiagnosticInformation.Response, self).__init__(
                'ClearDiagnosticInformation',
                ClearDiagnosticInformation.SID)

        def decode(self, data):
            self._check_nrc(data)

    class Request(GenericRequest):
        def __init__(self, group_of_dtc=0):
            super(ClearDiagnosticInformation.Request, self).__init__(
                'ClearDiagnosticInformation',
                ClearDiagnosticInformation.SID)
            self['groupOfDTC'] = group_of_dtc

        def encode(self):
            return [self.SID] + _to_bytes(self['groupOfDTC'])

        def decode(self, data):
            self._check_sid(data)
            self['groupOfDTC'] = data[1:]


class ReadDTCInformation:
    """ WriteMemoryByAddress service """
    SID = 0x19

    class Response(GenericResponse):
        def __init__(self):
            super(ReadDTCInformation.Response, self).__init__(
                'ReadDTCInformation',
                ReadDTCInformation.SID)

        def decode(self, data):
            self._check_nrc(data)
            # TODO
            self['data'] = data[1:]

    class Request(GenericRequest):
        def __init__(self):
            super(ReadDTCInformation.Request, self).__init__(
                'ReadDTCInformation',
                ReadDTCInformation.SID)

        def decode(self, data):
            self._check_sid(data)
            # TODO
            self['data'] = data[1:]


class InputOutputControlByIdentifier:
    """ InputOutputControlByIdentifier service """
    SID = 0x2F

    class Response(GenericResponse):
        def __init__(self):
            super(InputOutputControlByIdentifier.Response, self).__init__(
                'InputOutputControlByIdentifier',
                InputOutputControlByIdentifier.SID)

        def decode(self, data):
            self._check_nrc(data)
            self['dataIdentifier'] = _from_bytes(data[1:3])
            self['controlStatusRecord'] = data[3:]

    class Request(GenericRequest):
        def __init__(self, data_identifier=0, control_option_record=0,
                     control_enable_mask_record=None):
            super(InputOutputControlByIdentifier.Request, self).__init__(
                'InputOutputControlByIdentifier',
                InputOutputControlByIdentifier.SID)
            if data_identifier < 0 or data_identifier > 0xFFFF:
                raise ValueError('Invalid dataIdentifier, '
                                 'must be >= 0 and <= 0xFFFF')
            self['dataIdentifier'] = data_identifier
            self['controlOptionRecord'] = control_option_record
            self['controlEnableMaskRecord'] = control_enable_mask_record

        def encode(self):
            return ([self.SID] +
                    _to_bytes(self['dataIdentifier']) +
                    self['controlOptionRecord'] +
                    self['controlEnableMaskRecord'])

        def decode(self, data):
            self._check_sid(data)
            self['dataIdentifier'] = _from_bytes(data[1:3])
            self['controlOptionRecord'] = data[3]
            self['controlEnableMaskRecord'] = data[4:]


class RoutineControl:
    """ RoutineControl service """
    SID = 0x31

    RoutineControlType = UDSParameter('RoutineControlType', {
        # 0x00: ISOASAEReserved
        'startRoutine': 0x01,
        'stopRoutine': 0x02,
        'requestRoutineResults': 0x03,
        # 0x04 - 0x3F: ISOSAEReserved
    })

    class Response(GenericResponse):
        def __init__(self):
            super(RoutineControl.Response, self).__init__(
                'RoutineControl',
                RoutineControl.SID)

        def decode(self, data):
            self._check_nrc(data)
            self['routineControlType'] = data[1]
            self['routineIdentifier'] = _from_bytes(data[2:4])
            self['routineStatusRecord'] = data[4:]

    class Request(GenericRequest):
        def __init__(self, routine_control_type=0,
                     routine_identifier=0,
                     routine_control_option_record=None):
            super(RoutineControl.Request, self).__init__(
                'RoutineControl',
                RoutineControl.SID)
            if routine_identifier < 0 or routine_identifier > 0xFFFF:
                raise ValueError('Invalid routineIdentifier, '
                                 'must be > 0 and < 0xFFFF')
            self['routineControlType'] = routine_control_type
            self['routineIdentifier'] = routine_identifier
            self['routineControlOptionRecord'] = routine_control_option_record

        def encode(self):
            return ([self.SID, self['routineControlType']] +
                    _to_bytes(self['routineIdentifier']) +
                    self['routineControlOptionRecord'])

        def decode(self, data):
            self._check_sid(data)
            self['routineControlType'] = data[1]
            self['routineIdentifier'] = _from_bytes(data[2:4])
            self['routineControlOptionRecord'] = _from_bytes(data[4:])


class RequestTransfer:
    """ Generic service for requesting transfers, used for both
    RequestUpload and RequestDownload """

    class Response(GenericResponse):
        def __init__(self, name, sid):
            super(RequestTransfer.Response, self).__init__(name, sid)

        def decode(self, data):
            self._check_nrc(data)
            # length of maxNumberOfBlockLength is upper nybble of first byte
            length = data[1] >> 4
            self['maxNumberOfBlockLength'] = _from_bytes(data[2: 2 + length])

    class Request(GenericRequest):
        def __init__(self, name, sid, memory_address, memory_size,
                     data_format_identifier, address_format_identifier=None, length_format_identifier=None):
            super(RequestTransfer.Request, self).__init__(name, sid)
            self['memoryAddress'] = memory_address
            self['memorySize'] = memory_size
            self['dataFormatIdentifier'] = data_format_identifier
            self['addressFormatIdentifier'] = address_format_identifier
            self['lengthFormatIdentifier'] = length_format_identifier

        def encode(self):
            # addressAndLengthFormatIdentifier specifies length of address and
            # size
            # uppper nybble is byte length of size
            # lower nybble is byte length of address
            if self['addressFormatIdentifier'] is None:
                self['addressFormatIdentifier'] = _byte_size(self['memoryAddress'])

            if self['lengthFormatIdentifier'] is None:
                self['lengthFormatIdentifier'] = _byte_size(self['memorySize'])

            address_and_length_format_identifier = (self['addressFormatIdentifier'] & 0x0F)
            address_and_length_format_identifier |= ((self['lengthFormatIdentifier'] << 4) & 0xF0)

            return ([self.SID,
                    self['dataFormatIdentifier'],
                    address_and_length_format_identifier] +
                    _to_bytes(self['memoryAddress'], self['addressFormatIdentifier'] - _byte_size(self['memoryAddress'])) +
                    _to_bytes(self['memorySize'], self['lengthFormatIdentifier'] - _byte_size(self['memorySize'])))

        def decode(self, data):
            self._check_sid(data)
            self['dataFormatIdentifier'] = data[1]
            self['lengthFormatIdentifier'] = (data[2] >> 4) & 0x0F
            self['addressFormatIdentifier'] = data[2] & 0x0F
            self['memoryAddress'] = data[3: 3 + address_bytes]
            self['memorySize'] = data[3 + address_bytes:
                                      3 + address_bytes + size_bytes]


class RequestDownload:
    """ RequestUpload service """
    SID = 0x34

    class Response(RequestTransfer.Response):
        def __init__(self):
            super(RequestDownload.Response, self).__init__('RequestDownload',
                                                           RequestDownload.SID)

    class Request(RequestTransfer.Request):
        def __init__(self, memory_address=0,
                     memory_size=0,
                     data_format_identifier=0,
                     address_format=None,
                     length_format=None):
            super(RequestDownload.Request, self).__init__(
                'RequestDownload',
                RequestDownload.SID,
                memory_address,
                memory_size,
                data_format_identifier,
                address_format_identifier=address_format,
                length_format_identifier=length_format)


class RequestUpload(RequestTransfer):
    """ RequestUpload service """
    SID = 0x35

    class Response(RequestTransfer.Response):
        def __init__(self):
            super(RequestUpload.Response, self).__init__('RequestUpload',
                                                         RequestUpload.SID)

    class Request(RequestTransfer.Request):
        def __init__(self, memory_address=0,
                     memory_size=0,
                     data_format_identifier=0,
                     address_format=None,
                     length_format=None):
            super(RequestUpload.Request, self).__init__(
                'RequestUpload',
                RequestUpload.SID,
                memory_address,
                memory_size,
                data_format_identifier,
                address_format_identifier=address_format,
                length_format_identifier=length_format)


class TransferData:
    """ TransferData service """
    SID = 0x36

    class Response(GenericResponse):
        def __init__(self):
            super(TransferData.Response, self).__init__('TransferData',
                                                        TransferData.SID)

        def decode(self, data):
            self._check_nrc(data)
            self['blockSequenceCounter'] = data[1]
            self['transferResponseParameterRecord'] = data[2:]

    class Request(GenericRequest):
        def __init__(self, block_sequence_counter=0,
                     transfer_request_parameter_record=None):
            super(TransferData.Request, self).__init__('TransferData',
                                                       TransferData.SID)

            if block_sequence_counter < 0 or block_sequence_counter > 0xFF:
                raise ValueError('blockSequenceCounter '
                                 'must be >= 0 and <= 0xFF')

            self['blockSequenceCounter'] = block_sequence_counter
            self['transferRequestParameterRecord'] = (
                transfer_request_parameter_record)

        def encode(self):
            return ([self.SID, self['blockSequenceCounter']] +
                    self['transferRequestParameterRecord'])

        def decode(self, data):
            self._check_sid(data)
            self['blockSequenceCounter'] = data[1]
            self['transferRequestParameterRecord'] = data[2:]


class RequestTransferExit:
    """ RequestTransferExit service """
    SID = 0x37

    class Response(GenericResponse):
        def __init__(self):
            super(RequestTransferExit.Response, self).__init__(
                'RequestTransferExit',
                RequestTransferExit.SID)

        def decode(self, data):
            self._check_nrc(data)
            self['transferResponseParameterRecord'] = data[1:]

    class Request(GenericRequest):
        def __init__(self, transfer_request_parameter_record=None):
            super(RequestTransferExit.Request, self).__init__(
                'RequestTransferExit',
                RequestTransferExit.SID)
            self['transferRequestParameterRecord'] = (
                transfer_request_parameter_record)

        def encode(self):
            return [self.SID] + self['transferRequestParameterRecord']

        def decode(self, data):
            self._check_sid(data)
            self['transferRequestParameterRecord'] = data[1:]


class UDSInterface:
    SERVICES = {
        DiagnosticSessionControl.SID: DiagnosticSessionControl,
        ECUReset.SID: ECUReset,
        SecurityAccess.SID: SecurityAccess,
        CommunicationControl.SID: CommunicationControl,
        TesterPresent.SID: TesterPresent,
        AccessTimingParameter.SID: AccessTimingParameter,
        SecuredDataTransmission.SID: SecuredDataTransmission,
        ControlDTCSetting.SID: ControlDTCSetting,
        ResponseOnEvent.SID: ResponseOnEvent,
        LinkControl.SID: LinkControl,

        ReadDataByIdentifier.SID: ReadDataByIdentifier,
        ReadMemoryByAddress.SID: ReadMemoryByAddress,
        ReadScalingDataByIdentifier.SID: ReadScalingDataByIdentifier,
        ReadDataByPeriodicIdentifier.SID: ReadDataByPeriodicIdentifier,
        DynamicallyDefineDataIdentifier.SID: DynamicallyDefineDataIdentifier,
        WriteDataByIdentifier.SID: WriteDataByIdentifier,
        WriteMemoryByAddress.SID: WriteMemoryByAddress,

        ReadDTCInformation.SID: ReadDTCInformation,

        InputOutputControlByIdentifier.SID: InputOutputControlByIdentifier,

        RoutineControl.SID: RoutineControl,

        RequestDownload.SID: RequestDownload,
        RequestUpload.SID: RequestUpload,
        TransferData.SID: TransferData,
        RequestTransferExit.SID: RequestTransferExit,
        }

    def __init__(self, dispatcher=False, tx_arb_id=0x7E0, rx_arb_id=0x7E8, extended_id = False, functional_timeout = 2):
        self.functional_timeout = functional_timeout
        if not isinstance(dispatcher, Dispatcher):
            # no dispatcher passed, I can't set a transport layer. These will be set from who is using
            pass
        elif extended_id:
            self.transport_layer = IsotpNormalFixedAddressing(dispatcher)
            self.transport_layer.tx_arb_id = tx_arb_id
            self.transport_layer.rx_arb_id = rx_arb_id
        else:
            self.transport_layer = IsotpNormalAddressing(dispatcher, tx_arb_id)
            self.transport_layer.rx_arb_id = rx_arb_id

    def request(self, service, timeout=0.5):
        self.transport_layer.send(service.encode())
        if self.transport_layer.N_TAtype == N_TAtype.physical:
            try:
                return self.decode_response(timeout=timeout)
            except ResponsePendingException as e:
                # If I get a response pending exception means that I have a new timeout to consider
                return self.decode_response(timeout=e.timeout)
        elif self.transport_layer.N_TAtype == N_TAtype.functional:
            return self.decode_responses(timeout)
        else:
            raise Exception("Unknown N_TAtype")

    def decode_request(self, timeout=0.5):
        data = self.transport_layer.recv(timeout=timeout)
        if data is None:
            return None

        try:
            req = self.SERVICES[data[0]].Request()
            req.decode(data)
        except KeyError:
            req = GenericRequest('Unknown Service', data[0])
            req['data'] = data[1:]
        return req

    def decode_response(self, timeout=0.5):
        data = self.transport_layer.recv(timeout=timeout)
        if data is None:
            return None

        # Data is already filtered from the PCI information by the transport_layer.recv() method
        if data[0] == 0x7F:
            raise NegativeResponseException.factory(data)
        try:
            resp = self.SERVICES[data[0] - 0x40].Response()
            resp.decode(data)
        except KeyError:
            resp = GenericResponse('Unknown Service', data[0])
            resp['data'] = data[1:]
        return resp

    def decode_responses(self,timeout):
        """
        In some cases, for example when using functional addressing, we may have more responses from different ECUs
        :param functional_timeout:
        :return:
        """

        resps = {}
        start = time.time()
        while time.time() - start <= self.functional_timeout:
            try:
                resp = self.decode_response(timeout)
            except ResponsePendingException as e:
                # If I get a response pending exception means that I have a new timeout to consider
                self.functional_timeout = e.timeout
            except NegativeResponseException as e:
                resp = self.SERVICES[e.sid].Response()
            if resp is not None:
                resps[self.transport_layer.last_arb_id] = resp
        return resps
