from pyvit.proto.isotp import IsotpInterface


class NegativeResponseException(Exception):
    def __init__(self, nrc_data):
        # TODO: parse the NRC data
        super.__init__()


class TimeoutException(Exception):
    pass


class UDS:
    def _check_response(data, service_id):
        """ Generic function for checking received data is valid. If data is
        not received, a timeout is raised. If an negative response was received
        an approproate exception is raised """

        if data is None:
            raise TimeoutException("No data received")

        if data[0] != self.SERVICE_ID + 0x40:
            raise NegativeResponseException()

    class DiagnosticSessionControl:
        """ DiagnsoticSessionControl service """
        SERVICE_ID = 0x10

        class DiagnosticSessionType:
            # 0x00: ISOASAEReserved
            defaultSession = 0x01
            programmingSession = 0x02
            extendedDiagnosticSession = 0x03
            safetySystemDiagnosticSession = 0x04
            # 0x05 - 0x3F: ISOSAEReserved
            # 0x40 - 0x5F: vehicleManufacturerSpecific
            # 0x60 - 0x7E: vehicleManufacturerSpecific
            # 0x7F: ISOASAEReserved

        def __init__(self, diagnostic_session_type):
            self.diagnostic_session_type = diagnostic_session_type

        def encode(self):
            return [self.SERVICE_ID, self.diagnostic_session_type]

        def decode(self, data):
            UDS._check_response(data, self.SERVICE_ID)
            # TODO
            return data

    class ECUReset:
        """ ECUReset service """
        SERVICE_ID = 0x11

        class ResetType:
            # 0x00: ISOASAEReserved
            hardReset = 0x01
            keyOffOnReset = 0x02
            softReset = 0x03
            enableRapidPowerShutDown = 0x04
            disableRapidPowerShutDown = 0x05
            # 0x06 - 0x3F: ISOSAEReserved
            # 0x40 - 0x5F: vehicleManufacturerSpecific
            # 0x60 - 0x7E: vehicleManufacturerSpecific
            # 0x7F: ISOASAEReserved

        def __init__(self, reset_type):
            self.reset_type = reset_type

        def encode(self):
            return [self.SERVICE_ID, self.reset_type]

        def decode(self, data):
            UDS._check_response(data, self.SERVICE_ID)
            # TODO
            return data

    class SecurityAccess:
        """ SecurityAccess service """
        SERVICE_ID = 0x27

        def __init__(self):
            raise NotImplementedError("Service not implemented.")

    class CommunicationControl:
        """ CommunicationControl service """
        SERVICE_ID = 0x28

        def __init__(self):
            raise NotImplementedError("Service not implemented.")

    class TesterPresent:
        """ TesterPresent service """
        SERVICE_ID = 0x3E

        def __init__(self):
            raise NotImplementedError("Service not implemented.")

    class AccessTimingParameter:
        """ AccessTimingParameter service """
        SERVICE_ID = 0x83

        def __init__(self):
            raise NotImplementedError("Service not implemented.")

    class SecuredDataTransmission:
        """ SecuredDataTransmission service """
        SERVICE_ID = 0x84

        def __init__(self):
            raise NotImplementedError("Service not implemented.")

    class ControlDTCSetting:
        """ ControlDTCSetting service """
        SERVICE_ID = 0x85

        def __init__(self):
            raise NotImplementedError("Service not implemented.")

    class ResponseOnEvent:
        """ ResponseOnEvent service """
        SERVICE_ID = 0x86

        def __init__(self):
            raise NotImplementedError("Service not implemented.")

    class LinkControl:
        """ ResponseOnEvent service """
        SERVICE_ID = 0x87

        def __init__(self):
            raise NotImplementedError("Service not implemented.")

    class ReadDataByIdentifier:
        """ ReadDataByIdentifier service """
        SERVICE_ID = 0x22

        def __init__(self):
            raise NotImplementedError("Service not implemented.")

    class ReadMemoryByAddress:
        """ ReadMemoryByAddress service """
        SERVICE_ID = 0x23

        def __init__(self):
            raise NotImplementedError("Service not implemented.")

    class ReadScalingDataByIdentifier:
        """ ReadScalingDataByIdentifier service """
        SERVICE_ID = 0x24

        def __init__(self):
            raise NotImplementedError("Service not implemented.")

    class ReadDataByPeriodicIdentifier:
        """ ReadDataByPeriodicIdentifier service """
        SERVICE_ID = 0x2A

        def __init__(self):
            raise NotImplementedError("Service not implemented.")

    class DynamicallyDefineDataIdentifier:
        """ DynamicallyDefineDataIdentifier service """
        SERVICE_ID = 0x2C

        def __init__(self):
            raise NotImplementedError("Service not implemented.")

    class WriteDataByIdentifier:
        """ WriteDataByIdentifier service """
        SERVICE_ID = 0x2E

        def __init__(self):
            raise NotImplementedError("Service not implemented.")

    class WriteMemoryByAddress:
        """ WriteMemoryByAddress service """
        SERVICE_ID = 0x3D

        def __init__(self):
            raise NotImplementedError("Service not implemented.")

    class ClearDiagnosticInformation:
        """ ClearDiagnosticInformation service """
        SERVICE_ID = 0x14

        def __init__(self):
            raise NotImplementedError("Service not implemented.")

    class ReadDTCInformation:
        """ WriteMemoryByAddress service """
        SERVICE_ID = 0x19

        def __init__(self):
            raise NotImplementedError("Service not implemented.")

    class InputOutputControlByIdentifier:
        """ InputOutputControlByIdentifier service """
        SERVICE_ID = 0x2F

        def __init__(self):
            raise NotImplementedError("Service not implemented.")

    class RoutineControl:
        """ RoutineControl service """
        SERVICE_ID = 0x31

        def __init__(self):
            raise NotImplementedError("Service not implemented.")

    class RequestDownload:
        """ RequestDownload service """
        SERVICE_ID = 0x34

        def __init__(self):
            raise NotImplementedError("Service not implemented.")

    class RequestUpload:
        """ RequestUpload service """
        SERVICE_ID = 0x35

        def __init__(self):
            raise NotImplementedError("Service not implemented.")

    class TransferData:
        """ TransferData service """
        SERVICE_ID = 0x36

        def __init__(self):
            raise NotImplementedError("Service not implemented.")

    class RequestTransferExit:
        """ RequestTransferExit service """
        SERVICE_ID = 0x37

        def __init__(self):
            raise NotImplementedError("Service not implemented.")


class UDSInterface(IsotpInterface):
    def __init__(self, dispatcher, tx_arb_id=0x7E0, rx_arb_id=0x7E8):
        super().__init__(dispatcher, tx_arb_id, rx_arb_id)

    def request(self, service, timeout=0.5):
        self.send(service.encode())
        data = self.recv(timeout=timeout)
        return service.decode(data)
