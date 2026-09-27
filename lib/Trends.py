import datetime
from dataclasses import dataclass
import DependencyContainer

logger = DependencyContainer.get_logger(__name__)


@dataclass
class Trend:
    """How much a reading moved over a window of time.

    A trend is only ever a best effort. When there is no state logger, or the pump never ran
    during one of the windows, change is None and the UI leaves it off the panel.
    """
    #How far back the window looks.
    hours:int
    #The averaged value at the start of the window.
    start:float = None
    #The averaged value at the end of the window.
    end:float = None
    #end - start. None when either side had nothing to average.
    change:float = None

    def to_dict(self):
        return {
            "hours": self.hours,
            "start": self.start,
            "end": self.end,
            "change": self.change
        }


class TrendCalculator:
    """Calculates trends from the state log.

    The devices themselves know nothing about the database. This sits between them and reads
    whatever the state logger happens to be, so an install without a database keeps working
    and simply has no trends.
    """

    def __init__(self, stateLogger = None, maxDigits:int = 1) -> None:
        """
        Args:
            stateLogger: Anything with averageBetween(). Defaults to whatever is configured.
            maxDigits (int): Digits to round the change to.
        """
        self._stateLogger = DependencyContainer.stateLogger if stateLogger == None else stateLogger
        self._maxDigits = maxDigits

    @property
    def isAvailable(self) -> bool:
        """True when trends can be calculated. False means no database is configured for this install."""
        return self._stateLogger != None and hasattr(self._stateLogger, "averageBetween")

    def get(self, column:str, now:datetime.datetime = None) -> "list[Trend]":
        """Gets the short and long term trend for a single logged column.

        Args:
            column (str): Column in the state log. None or unknown gives back nothing.
            now (datetime): End of the window. Defaults to right now. Mostly here for testing.

        Returns:
            list[Trend]: Empty when trends are not available for this install.
        """
        if(not self.isAvailable or column == None):
            return []

        if(now == None):
            now = datetime.datetime.now()

        return [
            self._shortTerm(column, now),
            self._longTerm(column, now)
        ]

    def getAll(self, columnsByKey:"dict[any,str]", now:datetime.datetime = None) -> "dict[any,list[Trend]]":
        """Gets the trends for several columns at once, keyed the same way they were handed in."""
        if(not self.isAvailable):
            return {}

        if(now == None):
            now = datetime.datetime.now()

        return {key: self.get(column, now) for key, column in columnsByKey.items()}

    def _shortTerm(self, column:str, now:datetime.datetime) -> Trend:
        """Compares the oldest hour of the window to the newest hour of the window."""
        bucket = datetime.timedelta(hours = DependencyContainer.trendBucketHours)
        windowStart = now - datetime.timedelta(hours = DependencyContainer.trendHours)

        return self._build(
            DependencyContainer.trendHours,
            column,
            windowStart, windowStart + bucket,
            now - bucket, now)

    def _longTerm(self, column:str, now:datetime.datetime) -> Trend:
        """Compares the same block of hours on both days.

        Using the same block matters. Comparing the middle of the afternoon to the middle of
        the night says more about the sun than it does about the pool.
        """
        window = datetime.timedelta(hours = DependencyContainer.trendHours)
        past = now - datetime.timedelta(days = DependencyContainer.trendDays)

        return self._build(
            DependencyContainer.trendDays * 24,
            column,
            past - window, past,
            now - window, now)

    def _build(self, hours:int, column:str, startFrom:datetime.datetime, startTo:datetime.datetime, endFrom:datetime.datetime, endTo:datetime.datetime) -> Trend:
        trend = Trend(hours)

        try:
            trend.start = self._average(column, startFrom, startTo)
            trend.end = self._average(column, endFrom, endTo)
        except Exception:
            #A trend is never worth taking the page down over.
            logger.exception(f"Failed to calculate the trend for '{column}'.")
            return trend

        if(trend.start != None and trend.end != None):
            trend.change = round(trend.end - trend.start, self._maxDigits)

        return trend

    def _average(self, column:str, start:datetime.datetime, end:datetime.datetime) -> float:
        value = self._stateLogger.averageBetween(
            column,
            start,
            end,
            DependencyContainer.trendPumpStateColumn,
            DependencyContainer.trendPumpOffValue)

        return None if value == None else round(float(value), self._maxDigits)
