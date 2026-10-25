from datetime import datetime
import DependencyContainer
from Devices.Pump import Speed
from Devices.Schedule import PumpSchedule, PumpControl
from Devices.Schedules import Schedules
from Events.ScheduleChangeEvent import ScheduleChangeEvent
from lib.Action import Action
from lib.Actions import Actions
from Tests.IO.ScheduleRepoStub import ScheduleRepoStub

#Year 1970 on the start and 2100 on the end mean "every day", only the time matters
def dailySchedule(name:str, startHour:int, endHour:int, speedName:str = "SPEED_2", isActive:bool = True, pumpName:str = "main") -> PumpSchedule:
    return PumpSchedule(
        id = 1,
        name = name,
        pumps = [PumpControl(1, pumpName, speedName, "Main")],
        isActive = isActive,
        startTime = datetime(DependencyContainer.MIN_YEAR, 1, 1, startHour, 0),
        endTime = datetime(DependencyContainer.MAX_YEAR, 1, 1, endHour, 0))

def setup(recorder, *schedules:PumpSchedule) -> "tuple[Schedules, Action]":
    """Registers the schedules plus an action that can override them
    """
    override = Action("test-override", "Test Override")
    DependencyContainer.actions = Actions([override, recorder.getAction()])
    DependencyContainer.schedules = Schedules(ScheduleRepoStub(list(schedules)))
    return DependencyContainer.schedules, override

def at(hour:int, minute:int = 0, day:int = 25) -> datetime:
    return datetime(2026, 10, day, hour, minute)

def test_startsInsideTheWindow(mainPump, recorder):
    schedules, override = setup(recorder, dailySchedule("Morning", 8, 10))

    schedules.checkSchedule(at(9))

    assert mainPump.currentSpeed == Speed.SPEED_2
    assert schedules.get()[0].isRunning
    assert len(recorder.ofType(ScheduleChangeEvent)) == 1, "The UI is told the schedule started"

def test_doesNothingBeforeTheWindow(mainPump, recorder):
    schedules, override = setup(recorder, dailySchedule("Morning", 8, 10))

    schedules.checkSchedule(at(7, 59))

    assert mainPump.currentSpeed == Speed.OFF
    assert not schedules.get()[0].isRunning
    assert recorder.ofType(ScheduleChangeEvent) == []

def test_turnsThePumpOffWhenItEnds(mainPump, recorder):
    schedules, override = setup(recorder, dailySchedule("Morning", 8, 10))
    schedules.checkSchedule(at(9))

    schedules.checkSchedule(at(10, 1))

    assert mainPump.currentSpeed == Speed.OFF
    assert not schedules.get()[0].isRunning
    assert len(recorder.ofType(ScheduleChangeEvent)) == 2, "The UI is told it started and then stopped"

def test_endMinuteIsStillInside(mainPump, recorder):
    """The end time runs to the end of its minute (second 59)
    """
    schedules, override = setup(recorder, dailySchedule("Morning", 8, 10))

    schedules.checkSchedule(datetime(2026, 10, 25, 10, 0, 30))

    assert mainPump.currentSpeed == Speed.SPEED_2

def test_inactiveScheduleNeverRuns(mainPump, recorder):
    schedules, override = setup(recorder, dailySchedule("Morning", 8, 10, isActive = False))

    schedules.checkSchedule(at(9))

    assert mainPump.currentSpeed == Speed.OFF
    assert not schedules.get()[0].isRunning

def test_doesNotFightManualChanges(mainPump, recorder):
    """Once a schedule is running, it only sets the speed again when it starts over
    """
    schedules, override = setup(recorder, dailySchedule("Morning", 8, 10))
    schedules.checkSchedule(at(9))

    mainPump.on(Speed.SPEED_4)
    schedules.checkSchedule(at(9, 30))

    assert mainPump.currentSpeed == Speed.SPEED_4

def test_runsEveryDay(mainPump, recorder):
    schedules, override = setup(recorder, dailySchedule("Morning", 8, 10))

    for day in [1, 15, 28]:
        schedules.checkSchedule(at(9, day = day))
        assert mainPump.currentSpeed == Speed.SPEED_2, f"Should run on day {day}"
        schedules.checkSchedule(at(11, day = day))
        assert mainPump.currentSpeed == Speed.OFF

def test_scheduleWithDatesOnlyRunsThen(mainPump, recorder):
    oneDay = PumpSchedule(
        id = 1,
        name = "Party",
        pumps = [PumpControl(1, "main", "SPEED_4", "Main")],
        startTime = datetime(2026, 10, 31, 18, 0),
        endTime = datetime(2026, 10, 31, 23, 0))
    schedules, override = setup(recorder, oneDay)

    schedules.checkSchedule(at(19, day = 30))
    assert mainPump.currentSpeed == Speed.OFF

    schedules.checkSchedule(at(19, day = 31))
    assert mainPump.currentSpeed == Speed.SPEED_4

def test_overrideStopsTheSchedule(mainPump, recorder):
    """When an action overrides the schedule, it owns the pump. The schedule lets go without turning it off.
    """
    schedules, override = setup(recorder, dailySchedule("Morning", 8, 10))
    schedules.checkSchedule(at(9))

    override.overrideSchedule = True
    mainPump.on(Speed.SPEED_3)
    schedules.checkSchedule(at(9, 5))

    assert not schedules.get()[0].isRunning
    assert mainPump.currentSpeed == Speed.SPEED_3

def test_overridePreventsStarting(mainPump, recorder):
    schedules, override = setup(recorder, dailySchedule("Morning", 8, 10))
    override.overrideSchedule = True

    schedules.checkSchedule(at(9))

    assert mainPump.currentSpeed == Speed.OFF
    assert not schedules.get()[0].isRunning

def test_resumesWhenOverrideEnds(mainPump, recorder):
    schedules, override = setup(recorder, dailySchedule("Morning", 8, 10))
    override.overrideSchedule = True
    schedules.checkSchedule(at(9))

    override.overrideSchedule = False
    schedules.checkSchedule(at(9, 5))

    assert mainPump.currentSpeed == Speed.SPEED_2
    assert schedules.get()[0].isRunning

def test_unknownPumpDoesNotStopOtherSchedules(mainPump, recorder):
    schedules, override = setup(recorder,
        dailySchedule("Missing pump", 6, 7, pumpName = "spa"),
        dailySchedule("Morning", 8, 10))

    schedules.checkSchedule(at(6, 30))
    schedules.checkSchedule(at(9))

    assert mainPump.currentSpeed == Speed.SPEED_2

def test_runningEntityShowsTheRunningSchedule(mainPump, recorder):
    schedules, override = setup(recorder, dailySchedule("Morning", 8, 10))
    running = schedules.getEntities()[0]

    assert running.getValue() == "None"
    schedules.checkSchedule(at(9))
    assert running.getValue() == "Morning"
