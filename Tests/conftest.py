import pytest
import DependencyContainer
from Devices.Pump import Speed
from Devices.Pumps import Pumps
from Devices.RelayPump import RelayPump
from IO.GpioStub import GpioStub
from IO.GpioController import GpioController
from lib.Action import Action
from Events.Event import Event
from Tests.IO.PumpRepoStub import PumpRepoStub

DependencyContainer.logServerName = "none"

#Globals in DependencyContainer that tests set
_containerState = ["lights", "pumps", "schedules", "temperatureDevices", "actions", "variables", "valves",
    "stateLogger", "enviromentalSensor", "generator", "plugins", "temperatureUnit"]

@pytest.fixture(autouse=True)
def restoreDependencyContainer():
    """Tests set the globals in DependencyContainer. Puts them back afterwards, so one test can't change the
    outcome of another.
    """
    saved = {name: getattr(DependencyContainer, name) for name in _containerState}
    yield
    for name, value in saved.items():
        setattr(DependencyContainer, name, value)

@pytest.fixture
def mainPump() -> RelayPump:
    """The "main" pump the plugins look for, with every speed wired to a stubbed relay. Starts off.
    """
    GPIO = GpioStub()
    pump = RelayPump(1, "main", "Main", {
        Speed.SPEED_1: GpioController(GPIO, 17),
        Speed.SPEED_2: GpioController(GPIO, 27),
        Speed.SPEED_3: GpioController(GPIO, 22),
        Speed.SPEED_4: GpioController(GPIO, 5)
    })
    DependencyContainer.pumps = Pumps(PumpRepoStub([pump]))
    return pump

class EventRecorder:
    """Registered as an action, so it hears every event raised
    """
    def __init__(self) -> None:
        self.events:"list[Event]" = []

    def getAction(self) -> Action:
        return Action("event-recorder", "Event Recorder", self.events.append)

    def ofType(self, eventType:type) -> "list[Event]":
        return [x for x in self.events if type(x) == eventType]

@pytest.fixture
def recorder() -> EventRecorder:
    return EventRecorder()
