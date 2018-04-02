import serial

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

    def __init__(self, portInput):
        self.serialImpl = serial.Serial (port=portInput, baudrate=115200, timeout=10)

    # listens to the serial connection and automatically concatenates all the received
    # UTF-8 de- coded characters until a «»> symbol is observed, denoting the end of a
    # configuration command acknowledgment. Else, if no character has been received in a
    # 1 second time, it returns a «NULL\r» string;
    def receiveUntilGreaterThan(self):
        incomingString = ""
        while not(incomingString.endswith(">")):
            incomingString = incomingString + self.serialImpl.read().decode()
            if incomingString == "":
                incomingString = "NULL\r"
                break
        return incomingString

    def receiveUntilNewLine (self):
        incomingString = ""
        while not(incomingString.endswith("\r")):
            incomingString = incomingString + self.serialImpl.read().decode()
            if incomingString == "":
                incomingString = "NULL\r"
                break
        return incomingString

    # automatically inserts the carriage return symbol,
    # then sends the UTF-8 encoded string into the serial connection
    # with the OBDLink SX,
    # actually transmitting the command to the device.
    def send(self, outgoingString):
        outgoingString = outgoingString + "\r"
        self.serialImpl.write(outgoingString.encode())

    # Commands for ELM327 custom user1 CAN setup
    # ATPP2CSV60
    # ATPP2CON
    # ATPP2DSV0A
    # ATPP2DON
    def setup(self):
        # reset OBDLink SX
        self.send("ATZ")
        if self.receiveUntilGreaterThan() != "ATZ\r\r\rELM327 v1.3a\r\r>":
            print("ATZ failed")
            return
        self.send("ATSPB")
        if self.receiveUntilGreaterThan()!="ATSPB\rOK\r\r>":
            print("ATSPB failed")
            return
        # sets the previously tuned custom user1 CAN profile
        self.send("ATD1")
        if self.receiveUntilGreaterThan()!="ATD1\rOK\r\r>":
            print("ATD1 failed")
            return
        self.send("ATH1")
        if self.receiveUntilGreaterThan()!="ATH1\rOK\r\r>":
            print("ATH1 failed")
            return
        self.send("ATAL")
        if self.receiveUntilGreaterThan()!="ATAL\rOK\r\r>":
            print("ATAL failed")
            return
        self.send("STCMM1")
        if self.receiveUntilGreaterThan()!="STCMM1\rOK\r\r>":
            print("STCMM1 failed")
            return

    def startLogging(self):
        self.send("STMA")
        if self.receiveUntilNewLine()!="STMA\r":
            print("StartLogging failed")
            return

    def getFrame(self):
        incomingString = self.receiveUntilNewLine()
        withoutSpaces = incomingString.replace(" ", "")
        withoutNewLine = withoutSpaces.replace("\r", "")
        return withoutNewLine

    def stopLogging(self):
        self.send("")
        if self.receiveUntilGreaterThan()!="\r>":
            print("StopLogging failed")
            return

    def sendFrame(self, frame):
        first2hexesId = frame[:2]
        last6hexesId = frame[2:8]
        dataField = frame[9:]
        self.send("ATCP"+first2hexesId)
        if self.receiveUntilGreaterThan()!="ATCP"+first2hexesId+"\rOK\r\r>":
            print("First2hexesId set failed")
            return
        self.send("ATSH"+last6hexesId)
        if self.receiveUntilGreaterThan()!="ATSH"+last6hexesId+"\rOK\r\r>":
            print("Last6hexesId set failed")
            return
        self.send(dataField)
        if self.receiveUntilGreaterThan()[:len(dataField)]!=dataField:
            print("DataField send failed")
            return
