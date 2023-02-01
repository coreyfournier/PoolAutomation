import DependencyContainer
from Devices.Pump import Pump
from IO.PumpRepo import PumpRepo

logger = DependencyContainer.get_logger(__name__)

class Pumps:
    def __init__(self, pumpRepo:PumpRepo) -> None:
        self._pumps:"dict[str, Pump]" = {}

        self._pumps = pumpRepo.getPumps()

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