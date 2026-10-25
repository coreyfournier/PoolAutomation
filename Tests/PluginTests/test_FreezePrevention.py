import DependencyContainer
from Plugins.FreezePrevention import FreezePrevention
from Devices.Pump import Speed
from Devices.TemperatureBase import TemperatureChangeEvent
from lib.Actions import Actions
from lib.Variables import Variables
from Tests.IO.VariableRepoStub import VariableRepoStub
from Tests.Devices.TemperatureStub import TemperatureStub
from Tests.IO.ScheduleRepoStub import ScheduleRepoStub
from Devices.Schedule import PumpSchedule, PumpControl
from Devices.Schedules import Schedules
from lib.Action import Action
from datetime import datetime

def fToC(f:float) -> float:
    return (f - 32) * 5 / 9

def setup(enabled:bool = True, freezeAtF:float = 35.0):
    """Wires up the plugin the way Configuration does
    """
    DependencyContainer.temperatureUnit = 'f'
    #No schedules unless a test adds them
    DependencyContainer.schedules = None
    DependencyContainer.variables = Variables(None, VariableRepoStub())
    plugin = FreezePrevention()
    for variable in plugin.getVariables():
        DependencyContainer.variables.addVariable(variable)
    DependencyContainer.variables.get("freeze-prevention-enabled").value = enabled
    DependencyContainer.variables.get("freeze-prevention-temperature").value = freezeAtF

    action = plugin.getAction()
    DependencyContainer.actions = Actions([action])
    return plugin, action

def temperatureChanged(name:str, f:float) -> TemperatureStub:
    sensor = TemperatureStub(3, name, name, name, name)
    sensor.set(fToC(f))
    DependencyContainer.actions.nofityListners(TemperatureChangeEvent(None, True, None, sensor))
    return sensor

def isOn() -> bool:
    return DependencyContainer.variables.get("freeze-prevention-on").value

def test_runsThePumpWhenFreezing(mainPump):
    plugin, action = setup()

    temperatureChanged("ambient", 30)

    assert mainPump.currentSpeed == Speed.SPEED_3
    assert action.overrideSchedule, "The schedule must not turn the pump off while it's freezing"
    assert isOn()

def test_atTheLimitCountsAsFreezing(mainPump):
    plugin, action = setup(freezeAtF = 35.0)

    temperatureChanged("ambient", 35.0)

    assert mainPump.currentSpeed == Speed.SPEED_3

def test_doesNothingWhenDisabled(mainPump):
    plugin, action = setup(enabled = False)

    temperatureChanged("ambient", 20)

    assert mainPump.currentSpeed == Speed.OFF
    assert not action.overrideSchedule
    assert not isOn()

def test_doesNothingAboveFreezing(mainPump):
    plugin, action = setup()

    temperatureChanged("ambient", 50)

    assert mainPump.currentSpeed == Speed.OFF
    assert not action.overrideSchedule

def test_onlyTheAmbientSensorCounts(mainPump):
    """A cold roof or solar sensor is not the air temperature
    """
    plugin, action = setup()

    temperatureChanged("roof", 20)
    temperatureChanged("solar-heat", 20)

    assert mainPump.currentSpeed == Speed.OFF
    assert not isOn()

def test_turnsThePumpOffWhenItWarmsUp(mainPump):
    """Nothing else wants the pump, so it's turned off
    """
    plugin, action = setup()
    temperatureChanged("ambient", 30)

    temperatureChanged("ambient", 40)

    assert mainPump.currentSpeed == Speed.OFF
    assert not action.overrideSchedule
    assert not isOn()

def test_leavesThePumpToARunningSchedule(mainPump):
    plugin, action = setup()
    temperatureChanged("ambient", 30)
    DependencyContainer.schedules = Schedules(ScheduleRepoStub([
        PumpSchedule(id = 1, name = "Morning", pumps = [PumpControl(1, "main", "SPEED_2", "Main")],
            startTime = datetime(DependencyContainer.MIN_YEAR, 1, 1, 0, 0),
            endTime = datetime(DependencyContainer.MAX_YEAR, 1, 1, 23, 59),
            isRunning = True)
    ]))

    temperatureChanged("ambient", 40)

    assert mainPump.currentSpeed != Speed.OFF
    assert not action.overrideSchedule

def test_leavesThePumpToAnotherOverride(mainPump):
    """Something else (quick clean ...) is still holding the pump
    """
    plugin, action = setup()
    quickClean = Action("quick-clean", "Quick Clean")
    DependencyContainer.actions.add(quickClean)
    DependencyContainer.schedules = Schedules(ScheduleRepoStub([]))
    temperatureChanged("ambient", 30)
    quickClean.overrideSchedule = True

    temperatureChanged("ambient", 40)

    assert mainPump.currentSpeed != Speed.OFF
    assert not action.overrideSchedule

def test_doesNotKeepChangingThePumpWhileFreezing(mainPump):
    """Someone can change the speed while it's freezing and the next reading leaves it alone
    """
    plugin, action = setup()
    temperatureChanged("ambient", 30)

    mainPump.on(Speed.SPEED_4)
    temperatureChanged("ambient", 28)

    assert mainPump.currentSpeed == Speed.SPEED_4

def test_keepsTheOverrideAfterARestart(mainPump):
    """If the app restarts while it's freezing, the schedule is still not allowed to run
    """
    plugin, action = setup()
    DependencyContainer.variables.get("freeze-prevention-on").value = True

    assert plugin.getAction().overrideSchedule
