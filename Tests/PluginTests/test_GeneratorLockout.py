import DependencyContainer
from Plugins.GeneratorLockout import GeneratorLockout
from Devices.Pump import Speed
from Events.TimerEvent import TimerEvent
from lib.Actions import Actions
from lib.Variables import Variables
from Tests.IO.VariableRepoStub import VariableRepoStub
from IO.VariableRepo import VariableRepo
from Tests.IO.GeneratorStub import GeneratorStub

def startUp(generatorOn:bool, variablesFile:str = None):
    """Same order as Configuration.configure: action, then variables, then startup

    Args:
        variablesFile (str, optional): Loads and saves the variables in this file, like on the pi. Defaults to not saving.
    """
    DependencyContainer.variables = Variables(None, VariableRepoStub() if variablesFile == None else VariableRepo(variablesFile))
    DependencyContainer.actions = Actions([])

    plugin = GeneratorLockout()
    #Set after creating the plugin, because it creates the real generator when GENERATOR_DATA_URL is set
    DependencyContainer.generator = GeneratorStub(generatorOn)
    action = plugin.getAction()
    DependencyContainer.actions.add(action)
    for variable in plugin.getVariables():
        DependencyContainer.variables.addVariable(variable)
    plugin.startup(None, None)
    return plugin, action

def lockedOut() -> bool:
    return DependencyContainer.variables.get("generator-lockout-activated").value

def timer(secondsPassedTheHour:int):
    DependencyContainer.actions.nofityListners(TimerEvent(None, False, None, secondsPassedTheHour))

def test_startingOnTheGeneratorLocksOutThePump(mainPump):
    """Power goes out, the generator starts, then the pi boots. The schedule must not run the pump.
    """
    plugin, action = startUp(generatorOn = True)

    assert lockedOut()
    assert action.overrideSchedule

def test_restartOnTheGeneratorLocksOut(mainPump, tmp_path):
    """The last run saved it unlocked. The action starts from that saved value, so startup has to correct it.
    """
    variablesFile = str(tmp_path / "variables.json")
    startUp(generatorOn = False, variablesFile = variablesFile)

    plugin, action = startUp(generatorOn = True, variablesFile = variablesFile)

    assert lockedOut()
    assert action.overrideSchedule

def test_restartOnMainsPowerUnlocks(mainPump, tmp_path):
    """The last run saved it locked out, but the power is back on
    """
    variablesFile = str(tmp_path / "variables.json")
    startUp(generatorOn = True, variablesFile = variablesFile)

    plugin, action = startUp(generatorOn = False, variablesFile = variablesFile)

    assert not lockedOut()
    assert not action.overrideSchedule

def test_startingOnMainsPower(mainPump):
    plugin, action = startUp(generatorOn = False)

    assert not lockedOut()
    assert not action.overrideSchedule

def test_lockingOutTurnsThePumpOff(mainPump):
    plugin, action = startUp(generatorOn = False)
    mainPump.on(Speed.SPEED_2)

    DependencyContainer.variables.get("generator-lockout-activated").value = True

    assert mainPump.currentSpeed == Speed.OFF
    assert action.overrideSchedule

def test_unlocksOnceTheGeneratorIsOff(mainPump):
    plugin, action = startUp(generatorOn = False)
    DependencyContainer.variables.get("generator-lockout-activated").value = True

    timer(300)

    assert not lockedOut()
    assert not action.overrideSchedule

def test_staysLockedWhileTheGeneratorRuns(mainPump):
    plugin, action = startUp(generatorOn = True)
    DependencyContainer.variables.get("generator-lockout-activated").value = True

    timer(300)

    assert lockedOut()
    assert action.overrideSchedule

def test_checksTheGeneratorEveryFiveMinutes(mainPump):
    plugin, action = startUp(generatorOn = True)
    DependencyContainer.variables.get("generator-lockout-activated").value = True
    checksAtStartup = DependencyContainer.generator.checks

    for seconds in range(5, 300, 5):
        timer(seconds)
    assert DependencyContainer.generator.checks == checksAtStartup, "Nothing between the five minute marks"

    timer(300)
    assert DependencyContainer.generator.checks == checksAtStartup + 1

def test_doesNotAskTheGeneratorWhenNotLockedOut(mainPump):
    plugin, action = startUp(generatorOn = False)
    checksAtStartup = DependencyContainer.generator.checks

    timer(300)

    assert DependencyContainer.generator.checks == checksAtStartup
