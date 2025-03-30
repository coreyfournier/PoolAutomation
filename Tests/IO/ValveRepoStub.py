from Devices.Valve import Valve
from IO.IValveRepo import IValveRepo

class ValveRepoStub(IValveRepo):
    def __init__(self, valves:"list[Valve]") -> None:
        self._valves:"dict[str, Valve]" = {}

        for valve in valves:
            self._valves[valve.name] = valve


    def getValves(self) -> "dict[str, Valve]":               
        return self._valves
        