from Devices.Schedule import PumpSchedule

class ScheduleRepoStub:
    def __init__(self, schedules:"list[PumpSchedule]") -> None:
        self._schedules = schedules

    def getSchedules(self) -> "list[PumpSchedule]":
        return self._schedules

    def saveSchedules(self, schedules:"list[PumpSchedule]"):
        self._schedules = schedules
