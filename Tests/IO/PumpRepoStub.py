from Devices.Pump import *
from Devices.RelayPump import *
from IO.GpioController import *
from IO.I2cController import *
from IO.I2cRelay import *
from IO.IPumpRepo import IPumpRepo


class PumpRepoStub(IPumpRepo):
    def __init__(self, pumps:"list[Pump]") -> None:
        
        self._pumps:"dict[str, Pump]" = {}

        for pump in pumps:
            self._pumps[pump.name] = pump

    def getPumps(self) -> "dict[str, Pump]":               
        return self._pumps