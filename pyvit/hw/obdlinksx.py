import serial, sys

from pyvit import can


class OBDLinkSXDev:
    # It instantiates a new object,
    # opens a serial connection with the device
    # (whose serial port must be declared by the user, whose bitrate is set to 2 Mbps -
    # maximum device serial communication speed, which must previously have been set on the device by the user following the procedure defined in Listing 5.1 -
    # and whose read timeout is set at 1 second again in order to avoid a device hang up in the case of a target frame) and sets the device serial port attribute to point to that serial connection.
    #
    # Commands for Communication baud rate setup, Listing 5.1
    # ST BRT 5000
    # ST SBR 2000000
    # ATI
    # ST WBR QUESTO RENDE DEFINITIVE LE IMPOSTAZIONI
    debug = False
    debugPower = True
    bitrate = 500000

    def __init__(self, portInput, baudrate=115200, timeout=10):
        self.serialImpl = serial.Serial (port=portInput, baudrate=baudrate, timeout=timeout)
        self.reset()
        self.dev_running = False

    def start(self):
        self.reset()
        self.set_bitrate(self.bitrate)
        self.setup()
        self.startLogging()
        self.dev_running = True

    def stop(self):
        self.stopLogging()
        self.dev_running = False

    def set_bitrate(self, bitrate):
        if self.dev_running:
            raise RuntimeError("Can't set bitret with device running")
        self.bitrate = bitrate
        # set the CAN bus bitrate
        if bitrate == 0:
            # Autodetect speed
            command = 'ATSP0'
        # elif bitrate == 20000:
        #     self._dev_write('S1\r')
        # elif bitrate == 50000:
        #     self._dev_write('S2\r')
        # elif bitrate == 100000:
        #     self._dev_write('S3\r')
        # elif bitrate == 125000:
        #     self._dev_write('S4\r')
        # elif bitrate == 250000:
        #     self._dev_write('S5\r')
        elif bitrate == 500000:
            command = 'ATSP6'
        # elif bitrate == 750000:
        #     self._dev_write('S7\r')
        # elif bitrate == 1000000:
        #     self._dev_write('S8\r')
        # elif bitrate == 83000:
        #     self._dev_write('S9\r')
        # elif bitrate == 800000:
        #     self._dev_write('Sa\r')
        else:
            raise ValueError("Bitrate not supported")
        self._dev_write(command)
        #TODO: memorize if is used 11b or 29b IDs
        # interrogare con STPRSa per sapere il protocollo usato
        if not self.receiveUntilGreaterThan().endswith("%s\rOK\r\r>" % command):
            raise RuntimeError("%s failed" % command)
            return


    # listens to the serial connection and automatically concatenates all the received
    # UTF-8 de- coded characters until a «»> symbol is observed, denoting the end of a
    # configuration command acknowledgment. Else, if no character has been received in a
    # 1 second time, it returns a «NULL\r» string;
    def receiveUntilGreaterThan(self):
        incomingString = ""
        while not(incomingString.endswith(">")):
            incomingString = incomingString + self.serialImpl.read().decode()
            if incomingString == "":
                incomingString = "NULL>"
                break
        if self.debugPower:
            print("RECEIVEDUNTILGREATERTHAN: %s" % incomingString.encode())
        return incomingString

    def receiveUntilNewLine (self):
        incomingString = ""
        while not(incomingString.endswith("\r")):
            # self._lock.acquire()
            # self._lock.release()
            incomingString = incomingString + self.serialImpl.read().decode()
            if incomingString == "":
                incomingString = "NULL\r"
                break
            elif incomingString == "\r":
                incomingString = ""

        if self.debugPower:
            print("RECEIVEDUNTILNEWLINE: %s" % incomingString.encode())
        if "ER" in incomingString or "FUL" in incomingString:
            incomingString = "NULL\r"
        return incomingString

    # automatically inserts the carriage return symbol,
    # then sends the UTF-8 encoded string into the serial connection
    # with the OBDLink SX,
    # actually transmitting the command to the device.
    def _dev_write(self, outgoingString):
        outgoingString = outgoingString + "\r"
        if self.debugPower:
            print("OUTGOINGSTRING: %s" % outgoingString.encode())
        self.serialImpl.write(outgoingString.encode())

    def reset(self):
        # reset OBDLink SX
        self._dev_write("ATZ")
        strrec = self.receiveUntilGreaterThan()
        if not strrec.endswith("ATZ\r\r\rELM327 v1.3a\r\r>"):
            raise RuntimeError("ATZ failed")
            return
        sys.stdout.flush()

    # Commands for ELM327 custom user1 CAN setup
    # ATPP2CSV60
    # ATPP2CON
    # ATPP2DSV0A
    # ATPP2DON
    def setup(self):
        # self._dev_write("ATSPB")
        # if self.receiveUntilGreaterThan()!="ATSPB\rOK\r\r>":
        #     raise RuntimeError("ATSPB failed")
        #     return
        # sets the previously tuned custom user1 CAN profile
        self._dev_write("ATD1")
        if not self.receiveUntilGreaterThan().endswith("ATD1\rOK\r\r>"):
            raise RuntimeError("ATD1 failed")
            return
        self._dev_write("ATV1")
        if not self.receiveUntilGreaterThan().endswith("ATV1\rOK\r\r>"):
            raise RuntimeError("ATV1 failed")
            return
        self._dev_write("ATCAF0")
        if not self.receiveUntilGreaterThan().endswith("ATCAF0\rOK\r\r>"):
            raise RuntimeError("ATCAF0 failed")
            return
        self._dev_write("ATH1")
        if not self.receiveUntilGreaterThan().endswith("ATH1\rOK\r\r>"):
            raise RuntimeError("ATH1 failed")
            return
        self._dev_write("ATAL")
        if not self.receiveUntilGreaterThan().endswith("ATAL\rOK\r\r>"):
            raise RuntimeError("ATAL failed")
            return
        self._dev_write("STCMM1")
        if not self.receiveUntilGreaterThan().endswith("STCMM1\rOK\r\r>"):
            raise RuntimeError("STCMM1 failed")
            return

    def startLogging(self):
        self._dev_write("STMA")
        if self.receiveUntilNewLine()!="STMA\r":
            raise RuntimeError("StartLogging failed")
        return

    def recv(self):
        incomingString = self.receiveUntilNewLine()
        withoutSpaces = incomingString.replace(" ", "")
        withoutNewLine = withoutSpaces.replace("\r", "")
        if withoutNewLine == 'NULL':
            return None
        arb_id = withoutNewLine[:3]
        # skip one position because it contains the dlc
        data = [int(withoutNewLine[i:i+2], 16) for i in range(4, len(withoutNewLine), 2)]
        frame = can.Frame(int(arb_id, 16), data)
        if self.debug:
            print("RECV: %s" % frame)
        return frame

    def stopLogging(self):
        self._dev_write("")
        ret = self.receiveUntilGreaterThan()
        if not ret.endswith("\r>") and not ret.endswith(">"):
            raise RuntimeError("StopLogging failed")
            return

    def send(self, frame):
        if self.debug:
            print("SEND: %s" % frame)
        self.sendFrame("%x%s" % (frame.arb_id, ''.join(('%02X' % b) for b in frame.data)))

    def sendFrame(self, frame):
        self.stopLogging()
        #TODO: handle 29b IDs
        first2hexesId = frame[:2]
        # last6hexesId = frame[2:8]
        last6hexesId = frame[:3]
        dataField = frame[3:]
        # self._dev_write("ATCP"+first2hexesId)
        # if self.receiveUntilGreaterThan()!="ATCP"+first2hexesId+"\rOK\r\r>":
        #     raise RuntimeError("First2hexesId set failed")
        #     return
        self._dev_write("ATSH"+last6hexesId)
        if not self.receiveUntilGreaterThan().endswith("ATSH"+last6hexesId+"\rOK\r\r>"):
            raise RuntimeError("Last6hexesId set failed")
            return
        self._dev_write(dataField)
        if not self.receiveUntilGreaterThan()[:len(dataField)].endswith(dataField):
            raise RuntimeError("DataField send failed")
            return

        self.startLogging()
