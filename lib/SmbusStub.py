import DependencyContainer

logger = DependencyContainer.get_logger(__name__)

class SMBus:
    
    def __init__(self, busNumber) -> None:
        self._state = 0b11111111
        
    def write_byte_data(self, i2c_addr, register, value, force=None):
        self._state = value
        
        logger.info(f"Writing to {i2c_addr} value:{bin(value)}")
        
    def read_byte(self, address, force=None):
        return self._state