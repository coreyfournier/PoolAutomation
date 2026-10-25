import datetime
import DependencyContainer
from Plugins.QuickClean import QuickClean
from Devices.Pump import Speed
from Devices.Schedule import PumpSchedule, PumpControl
from Devices.Schedules import Schedules
from lib.Actions import Actions
from lib.Variables import Variables
from lib.Variable import Variable
from Tests.IO.VariableRepoStub import VariableRepoStub
from Tests.IO.ScheduleRepoStub import ScheduleRepoStub

def setup():
    """Wires up the plugin the way Configuration does. No schedules unless a test adds them.
    """
    DependencyContainer.schedules = None
    DependencyContainer.variables = Variables(None, VariableRepoStub())
    plugin = QuickClean()
    for variable in plugin.getVariables():
        DependencyContainer.variables.addVariable(variable)

    action = plugin.getAction()
    DependencyContainer.actions = Actions([action])
    return plugin, action

def variable(name:str):
    return DependencyContainer.variables.get(name)

def test_runsThePumpForTheHoursAsked(mainPump):
    plugin, action = setup()
    before = datetime.datetime.now()

    variable("quick-clean-expires-in-hours").value = 2.0

    assert mainPump.currentSpeed == Speed.SPEED_1
    assert action.overrideSchedule, "The schedule must not turn the pump off during a quick clean"
    assert variable("quick-clean-on").value
    expiresOn = datetime.datetime.fromisoformat(variable("quick-clean-expires-on").value)
    assert before + datetime.timedelta(hours = 2) <= expiresOn <= datetime.datetime.now() + datetime.timedelta(hours = 2)
    assert not variable("quick-clean-expires-on").hasExpired

def test_settingZeroHoursStopsIt(mainPump):
    plugin, action = setup()
    variable("quick-clean-expires-in-hours").value = 2.0

    variable("quick-clean-expires-in-hours").value = 0.0

    assert mainPump.currentSpeed == Speed.OFF
    assert not action.overrideSchedule
    assert not variable("quick-clean-on").value

def test_stopsWhenTheTimeIsUp(mainPump):
    """The worker checks for expired variables. Once quick clean expires, everything is put back.
    """
    plugin, action = setup()
    variable("quick-clean-expires-in-hours").value = 2.0

    #Pretend the two hours have passed
    variable("quick-clean-expires-on").setValueNoNotify((datetime.datetime.now() - datetime.timedelta(minutes = 1)).isoformat())
    DependencyContainer.variables.checkForExpiredVariables()

    assert mainPump.currentSpeed == Speed.OFF
    assert not action.overrideSchedule
    assert not variable("quick-clean-on").value

def test_notStoppedEarly(mainPump):
    plugin, action = setup()
    variable("quick-clean-expires-in-hours").value = 2.0

    DependencyContainer.variables.checkForExpiredVariables()

    assert mainPump.currentSpeed == Speed.SPEED_1
    assert variable("quick-clean-on").value

def test_leavesThePumpOnIfAScheduleIsRunning(mainPump):
    """When it ends during a schedule, the pump is the schedule's again, so it stays on
    """
    plugin, action = setup()
    running = PumpSchedule(id = 1, name = "Morning", pumps = [PumpControl(1, "main", "SPEED_2", "Main")],
        startTime = datetime.datetime(DependencyContainer.MIN_YEAR, 1, 1, 0, 0),
        endTime = datetime.datetime(DependencyContainer.MAX_YEAR, 1, 1, 23, 59),
        isRunning = True)
    DependencyContainer.schedules = Schedules(ScheduleRepoStub([running]))
    variable("quick-clean-expires-in-hours").value = 2.0

    variable("quick-clean-expires-in-hours").value = 0.0

    assert mainPump.currentSpeed != Speed.OFF, "A schedule is running, so the pump isn't turned off"
    assert not action.overrideSchedule

def test_otherVariablesAreIgnored(mainPump):
    plugin, action = setup()
    DependencyContainer.variables.addVariable(Variable("unrelated-hours", "Unrelated", float, value = 0.0))

    variable("unrelated-hours").value = 2.0

    assert mainPump.currentSpeed == Speed.OFF
    assert not action.overrideSchedule
    assert not variable("quick-clean-on").value
