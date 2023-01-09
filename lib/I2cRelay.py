import smbus2
class I2cRelay:
    def __init__(self, relayAddress:int, bus:smbus2.SMBus) -> None:
        """Used to control an i2c relay.
        If you don't know the address of the relay you can find it here:
        https://learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/configuring-i2c
        This will also show you how to enable it

        Args:
            relayAddress (int): Address of the relay
            bus (smbus2.SMBus): EX: smbus2.SMBus(1) #1 is the bus of the pi
        """
        self.address = relayAddress
        self.bus:smbus2.SMBus = bus
        self.deviceRegister = 0xFF

    def On(self, relayNumber):
        #Assuming it's an 8 channel relay
        #shift the bit 
        #Need to read from the device
        #existingState = 0b00000000
        existingState = self.bus.read_byte(self.address,0)
        bitMask = 0b11111111
        #bus.write_byte_data(address, 254,  | 0b11111011)
        
        flippedRelay = self._getBitAddress(relayNumber)
        
        newRelayState = bitMask & (existingState | flippedRelay)
        #Now flip the state of the bits as the device wants 1 as off and 0 as on
        newRelayState = ~newRelayState        
        self.bus.write_byte_data(self.address, self.deviceRegister, newRelayState)

    def allOff(self):
        self.bus.write_byte_data(self.address, self.deviceRegister, 0b11111111)

    def _getBitAddress(self, relayNumber:int) -> int:
        """bit of the relay you want changed. You can see the literal change by using: bin(flippedRelay)

        Args:
            relayNumber (int): _description_

        Returns:
            int: _description_
        """
        return (0b00000000 | (1<<(relayNumber-1)))

    def getRelayState(self, relayNumber) -> bool:
        
        return self.bus.read_byte(self.address, 0) & self._getBitAddress(relayNumber)    
