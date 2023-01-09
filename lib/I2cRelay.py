import smbus2
import DependencyContainer

logger = DependencyContainer.get_logger(__name__)

class I2cRelay:
    def __init__(self, relayAddress:int, bus:smbus2.SMBus) -> None:
        """Used to control an i2c relay. This for sure works on:
        https://www.amazon.com/dp/B07JGSNWFF?psc=1&ref=ppx_yo2ov_dt_b_product_details
        If you don't know the address of the relay you can find it here as well as configure the pi to enable i2c:
        https://learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/configuring-i2c
        This is created for an 8 relay device. Not sure if any modifications are required to work on smaller or larger devices.
        Args:
            relayAddress (int): Address of the relay. Mine defaults to 0x27. Look at the documentation for yours
            bus (smbus2.SMBus): EX: smbus2.SMBus(1) #1 is the bus of the pi
        """
        self._address = relayAddress
        self._bus:smbus2.SMBus = bus
        self._deviceRegister = 0xFF
        self._maxRelays = 8

        logger.debug(f"Address:{relayAddress} deviceRegister:{self._deviceRegister}")

    def _invertBits(self, number:int): 
        """Inverts the bits and returns

        Args:
            number (int): Some number

        Returns:
            _type_: converts 101 to 010
        """
        #0xFF ensurs the number is an unsigned integer
        return (~number & 0xFF)
    
    def Off(self, relayNumber):
        existingState = self._existing()
        #Invert the changed one and make sure it's an unsigned integer
        flippedRelay = self._getBitAddress(relayNumber)
        #Invert the relay value so it turns off the exising state
        newRelayState = (existingState & self._invertBits(flippedRelay))
        #Now flip the state of the bits as the device wants 1 as off and 0 as on
        newRelayState = self._invertBits(newRelayState)        
        logger.debug(f"Switching off ({relayNumber}) {bin(newRelayState)} Existing:{bin(existingState)} Address:{self._address:04x} Register:{self._deviceRegister:04x}")
        self._bus.write_byte_data(self._address, self._deviceRegister, newRelayState)

    def On(self, relayNumber):
        #Assuming it's an 8 channel relay
        existingState = self._existing()
        flippedRelay = self._getBitAddress(relayNumber)
        
        newRelayState = (existingState | flippedRelay)
        #Now flip the state of the bits as the device wants 1 as off and 0 as on. Also make sure it's the unsigned value
        newRelayState = self._invertBits(newRelayState)       
        logger.debug(f"Switching on ({relayNumber}) {bin(newRelayState)} Existing:{bin(existingState)} Address:{self._address:04x} Register:{self._deviceRegister:04x}")
        self._bus.write_byte_data(self._address, self._deviceRegister, newRelayState)

    def _existing(self):
        """Gets the normalized value. True for on False for Off. 

        Returns:
            int: True for on False for Off
        """
        return self._invertBits(self._bus.read_byte(self._address,0))

    def allOff(self):
        self._bus.write_byte_data(self._address, self._deviceRegister, 0b11111111)

    def _getBitAddress(self, relayNumber:int) -> int:
        """bit of the relay you want changed. You can see the literal change by using: bin(flippedRelay).
        This is the normalized value. True for on, False for Off

        Args:
            relayNumber (int): Number on the board

        Returns:
            int: This is the normalized value. True for on, False for Off
        """
        #The relays are numbered in the opposite direction
        position = (self._maxRelays - relayNumber)
        return (0b00000000 | (1<<(position)))

    def getRelayState(self, relayNumber) -> bool:
        """Gets the current state of the relay.

        Args:
            relayNumber (_type_): _description_

        Returns:
            bool: True it's on, False it's off
        """
        currentRelay = self._getBitAddress(relayNumber)

        #Filter out the other bits and then compare what's left to our relay
        return (self._invertBits(self._bus.read_byte(self._address, 0)) & currentRelay)  == currentRelay
