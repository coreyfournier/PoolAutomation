import DependencyContainer
from Devices.Pump import Pump

logger = DependencyContainer.get_logger(__name__)

class Pumps:
    def __init__(self, pumps:"list[Pump]") -> None:
        self._pumps:"dict[str, Pump]" = {}

        for pump in pumps:
            self._pumps[pump.name] = pump

    def get(self, name:str):
        if(name in self._pumps):
            return self._pumps[name]
        else:
            return None
    def getById(self, index:int):
        list = self.getAll()

        if(index <= len(list)):
            return list[index]
        else:
            return None

    def getAll(self):
        return [value for key, value in self._pumps.items()]