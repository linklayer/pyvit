"""
Details on how addressing works for ISOTP can be seen in ISO 15765-2
"""

from pyvit.proto.isotp import IsotpInterface
from abc import ABC, abstractmethod
from enum import Enum, auto


class Mtype(Enum):
    diagnostics = auto()
    remote_diagnostics = auto()


class N_TAtype(Enum):
    functional = auto()
    physical = auto()


class AddressingType(Enum):
    # CAN ID 11b, for each combination of N_SA, N_TA, N_TAtype, Mtype a unique CAN identifier is asigned
    NormalAddressing = auto()
    # CAN ID 29b, mapping between addressing fields and CAN ID bits is specified
    # 28-26: priority bits, usually (110)bin -> (6)hex
    # 25,24: bits R (reserved) and DP (data page), set to 0
    # 23-16: bits PF (protocol data unit format) depends on N_TAtype.
        # if N_TAtype.physical then (218)dec, if N_TAtype.functional then (219)dec
    # 15-8: N_TA
    # 7-0: N_SA
    NormalFixedAddressing = auto()
    # suppose CAN ID 11b, for each combination of N_SA, N_TAtype, Mtype a unique CAN identifier is assigned
    # N_TA is placed in the first byte of data, N_PCI info and N_Data are placed after
    ExtendedAddressing = auto()
    # MType is set to Mtype.remote_diagnostics
    # if CAN ID 29b
        # 28-26: priority bits, usually (110)bin -> (6)hex
        # 25,24: bits R (reserved) and DP (data page), set to 0
        # 23-16: bits PF (protocol data unit format) depends on N_TAtype.
            # if N_TAtype.physical then (206)dec, if N_TAtype.functional then (205)dec
        # 15-8: N_TA
        # 7-0: N_SA
        # N_AE is placed in the first byte of data, N_PCI info and N_Data are placed after
    # if CAN ID 11b
        # for each combination of N_SA, N_TA, N_TAtype a unique CAN identifier is assigned
        # N_AE is placed in the first byte of data, N_PCI info and N_Data are placed after
    MixedAddressing = auto()


class IsotpAddressing(IsotpInterface,ABC):
    # protocol data unit format according to addressing mode
    PF = {
        AddressingType.NormalFixedAddressing: {N_TAtype.functional: 219, N_TAtype.physical: 218},
        AddressingType.MixedAddressing: {N_TAtype.functional: 205, N_TAtype.physical: 206},
    }
    EXTENDED_ID = {
        AddressingType.NormalAddressing: False,
        AddressingType.NormalFixedAddressing: True,
        AddressingType.ExtendedAddressing: False,
        AddressingType.MixedAddressing: False # in this case has to be interpreted as default value, could be also True
    }

    def __init__(self, dispatcher, n_sa = 0x00, n_ta = 0x00, n_ae = False, mtype = Mtype.diagnostics, n_tatype = N_TAtype.physical,
                 addressingType = AddressingType.NormalAddressing, extended_id = False, rx_filter_func = False):
            self.addressingType = addressingType
            self.N_SA = n_sa
            self.N_AE = n_ae
            self.MType = mtype
            self.N_TAtype = n_tatype
            self.extended_id = extended_id or self.EXTENDED_ID[self.addressingType]
            self.N_TA = n_ta
            super().__init__(dispatcher, self.compute_tx_arb_id(), self.compute_rx_arb_id(), extended_id = self.extended_id, rx_filter_func = rx_filter_func)

    @property
    def N_TA(self):
        return self.__N_TA

    @N_TA.setter
    def N_TA(self,value):
        self.__N_TA = value
        # If target address changes I have to recompute the arbitration IDs
        self.tx_arb_id = self.compute_tx_arb_id()
        self.rx_arb_id = self.compute_rx_arb_id()

    @abstractmethod
    def compute_tx_arb_id(self):
        pass

    @abstractmethod
    def compute_rx_arb_id(self):
        pass

    def parse_frame(self,frame):
        return super(IsotpAddressing, self).parse_frame(frame)


class IsotpMixedAddressing (IsotpAddressing):
    def __init__(self, dispatcher, n_sa=0x00, n_ta=0x00, n_ae=False, mtype=Mtype.diagnostics,
                 n_tatype=N_TAtype.physical, rx_filter_func=False):
        # in this case first byte is used for addressing purpose, space for data is only 6 bytes
        self.sf_data_len_limit = 6
        super().__init__(dispatcher, n_sa, n_ta, n_ae, mtype, n_tatype, AddressingType.MixedAddressing, True,
                         rx_filter_func)

    def compute_tx_arb_id(self):
        # compose the N_AI fields to get the 29b CAN ID
        # print("%X" % (self.P & 0b111))
        # print("%X" % ((self.P & 0b111) << 1))
        # print("%X" % ((((self.P & 0b111) << 1)| self.R) << 1 | self.DP))
        # print("%X" % (((((self.P & 0b111) << 1) | self.R) << 1) | self.DP))
        return (((((((((((self.P & 0b111) << 1) | self.R) << 1) | self.DP) << 8) | self.PF[self.addressingType][
            self.N_TAtype]) << 8) | self.N_TA) << 8) | self.N_SA)

    def compute_rx_arb_id(self):
        # compose the N_AI fields to get the 29b CAN ID of the response message
        # N_TAtype should be always physical
        # N_TA and N_SA are reversed respect to tx_arb_id
        return (((((((((((self.P & 0b111) << 1) | self.R) << 1) | self.DP) << 8) | self.PF[self.addressingType][
            self.N_TAtype]) << 8) | self.N_SA) << 8) | self.N_TA)

    def parse_frame(self, frame):
        # In case of mixed addressing first byte of data is the remote address
        frame.data.pop(0)
        return super(IsotpAddressing, self).parse_frame(frame)

    def get_base_frame_data(self):
        # In case of mixed addressing first byte of data is the remote address
        return [self.N_AE]


class IsotpExtendedAddressing (IsotpAddressing):
    def __init__(self, dispatcher, n_sa=0x00, n_ta=0x00, n_ae=False, mtype=Mtype.diagnostics,
                 n_tatype=N_TAtype.physical, rx_filter_func=False):
        # in this case first byte is used for addressing purpose, space for data is only 6 bytes
        self.sf_data_len_limit = 6
        super().__init__(dispatcher, n_sa, n_ta, n_ae, mtype, n_tatype, AddressingType.ExtendedAddressing, False,
                         rx_filter_func)

    def compute_tx_arb_id(self):
        return self._tx_arb_id


    def compute_rx_arb_id(self):
        return self._rx_arb_id

    def parse_frame(self, frame):
        # In case of extended addressing first byte of data is the target address
        frame.data.pop(0)
        return super(IsotpAddressing, self).parse_frame(frame)

    def get_base_frame_data(self):
        # In case of extended addressing first byte of data is the target address
        return [self.N_TA]

class IsotpNormalFixedAddressing (IsotpAddressing):
    # priority 3 bits
    P = 6
    # reserved 1 bit
    R = 0
    # data page 1 bit
    DP = 0
    def __init__(self, dispatcher, n_sa=0x00, n_ta=0x00, n_ae=False, mtype=Mtype.diagnostics,
                 n_tatype=N_TAtype.physical, rx_filter_func=False):
        super().__init__(dispatcher, n_sa, n_ta, n_ae, mtype, n_tatype, AddressingType.NormalFixedAddressing, True, rx_filter_func)

    def compute_tx_arb_id(self):
        # compose the N_AI fields to get the 29b CAN ID
        # print("%X" % (self.P & 0b111))
        # print("%X" % ((self.P & 0b111) << 1))
        # print("%X" % ((((self.P & 0b111) << 1)| self.R) << 1 | self.DP))
        # print("%X" % (((((self.P & 0b111) << 1) | self.R) << 1) | self.DP))
        return (((((((((((self.P & 0b111) << 1) | self.R) << 1) | self.DP) << 8) | self.PF[self.addressingType][
            self.N_TAtype]) << 8) | self.N_TA) << 8) | self.N_SA)

    def compute_rx_arb_id(self):
        # compose the N_AI fields to get the 29b CAN ID of the response message
        # N_TAtype should be always physical
        # N_TA and N_SA are reversed respect to tx_arb_id
        return (((((((((((self.P & 0b111) << 1) | self.R) << 1) | self.DP) << 8) | self.PF[self.addressingType][
            self.N_TAtype]) << 8) | self.N_SA) << 8) | self.N_TA)


class IsotpNormalAddressing (IsotpAddressing):
    def __init__(self, dispatcher, tx_arb_id, rx_arb_id = False, n_tatype = N_TAtype.physical, rx_filter_func = False):
        self._rx_arb_id = rx_arb_id
        self._tx_arb_id = tx_arb_id
        super().__init__(dispatcher, n_tatype = n_tatype, addressingType = AddressingType.NormalAddressing,
                         extended_id = False, rx_filter_func = rx_filter_func)

    def compute_tx_arb_id(self):
        return self._tx_arb_id


    def compute_rx_arb_id(self):
        return self._rx_arb_id
