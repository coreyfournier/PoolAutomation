import datetime
import DependencyContainer
from Plugins.ChemistryAlerts import ChemistryAlerts
from Devices.Pump import Speed
from Devices.PoolChemistry import PoolChemistry
from Events.OrpChangeEvent import OrpChangeEvent
from Events.PhChangeEvent import PhChangeEvent
from Events.OrpHighEvent import OrpHighEvent
from Events.OrpLowEvent import OrpLowEvent
from Events.PhHighEvent import PhHighEvent
from Events.PhLowEvent import PhLowEvent
from lib.Actions import Actions

def setup(recorder, pumpRunningMinutes:float = 10) -> ChemistryAlerts:
    plugin = ChemistryAlerts()
    DependencyContainer.actions = Actions([plugin.getAction(), recorder.getAction()])
    if(pumpRunningMinutes != None):
        #Same as the pump having been turned on that long ago
        plugin.pumpOnSinceDateTime = datetime.datetime.now() - datetime.timedelta(minutes = pumpRunningMinutes)
    return plugin

def orpReading(orp:float):
    DependencyContainer.actions.nofityListners(OrpChangeEvent(None, True, None, PoolChemistry(80, orp, 7.4)))

def phReading(ph:float):
    DependencyContainer.actions.nofityListners(PhChangeEvent(None, True, None, PoolChemistry(80, 450, ph)))

def alerts(recorder) -> "list[str]":
    alertTypes = [OrpHighEvent, OrpLowEvent, PhHighEvent, PhLowEvent]
    return [type(x).__name__ for x in recorder.events if type(x) in alertTypes]

def test_lowOrp(recorder):
    setup(recorder)
    orpReading(250)
    assert alerts(recorder) == ["OrpLowEvent"]

def test_highOrp(recorder):
    setup(recorder)
    orpReading(700)
    assert alerts(recorder) == ["OrpHighEvent"]

def test_lowPh(recorder):
    setup(recorder)
    phReading(6.8)
    assert alerts(recorder) == ["PhLowEvent"]

def test_highPh(recorder):
    setup(recorder)
    phReading(8.2)
    assert alerts(recorder) == ["PhHighEvent"]

def test_normalReadingsDoNotAlert(recorder):
    setup(recorder)
    orpReading(450)
    phReading(7.4)
    #The limits themselves are still normal
    orpReading(300)
    orpReading(600)
    phReading(7)
    phReading(8)
    assert alerts(recorder) == []

def test_alertsOnceUntilBackToNormal(recorder):
    """A reading that stays out of range doesn't keep alerting. Back in range resets it.
    """
    setup(recorder)
    orpReading(250)
    orpReading(240)
    orpReading(230)
    assert alerts(recorder) == ["OrpLowEvent"]

    orpReading(450)
    orpReading(250)
    assert alerts(recorder) == ["OrpLowEvent", "OrpLowEvent"]

def test_orpAndPhAreTrackedSeparately(recorder):
    setup(recorder)
    orpReading(250)
    phReading(8.2)
    assert alerts(recorder) == ["OrpLowEvent", "PhHighEvent"]

def test_ignoredUntilThePumpHasRunLongEnough(recorder):
    """Still water gives bad readings, so the pump has to run for a while first
    """
    setup(recorder, pumpRunningMinutes = 2)
    orpReading(250)
    phReading(8.2)
    assert alerts(recorder) == []

def test_ignoredWhileThePumpIsOff(recorder, mainPump):
    setup(recorder)
    mainPump.on(Speed.SPEED_2)
    mainPump.off()

    orpReading(250)
    assert alerts(recorder) == []

def test_pumpStartingStartsTheClock(recorder, mainPump):
    plugin = setup(recorder, pumpRunningMinutes = None)

    mainPump.on(Speed.SPEED_2)

    assert plugin.pumpOnSinceDateTime != None
    orpReading(250)
    assert alerts(recorder) == [], "It only just started"

def test_speedChangeDoesNotRestartTheClock(recorder, mainPump):
    plugin = setup(recorder, pumpRunningMinutes = None)
    mainPump.on(Speed.SPEED_2)
    startedAt = plugin.pumpOnSinceDateTime

    mainPump.on(Speed.SPEED_4)

    assert plugin.pumpOnSinceDateTime == startedAt
