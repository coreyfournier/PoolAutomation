from IO.SmbusStub import SMBus
import DependencyContainer
from IO.I2cRelay import I2cRelay
logger = DependencyContainer.get_logger(__name__)

class I2cController(I2cRelay):
    def __init__(self, relayNumber:int, relayAddress:int, bus:SMBus) -> None:
        super().__init__(relayAddress,bus)
        self._relayNumber = relayNumber

    def on(self):
        super().on(self._relayNumber)

    def off(self):
        super().off(self._relayNumber)
    
    def isOn(self):
        return self.getRelayState(self._relayNumber)

    def destroy(self):
        super().destroy()
