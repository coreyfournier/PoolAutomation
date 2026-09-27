import datetime
import DependencyContainer
from lib.Trends import TrendCalculator
from IO.StateLoggerStub import StateLoggerStub

DependencyContainer.logServerName = "none"

#A fixed point in time so the windows land on whole hours and the test reads easily.
NOW = datetime.datetime(2026, 9, 26, 15, 0, 0)
POOL = "temperature4"


def logHour(logger:StateLoggerStub, at:datetime.datetime, temperature:float, pumpState:str = "SPEED_2", minutes:"list[int]" = [0, 30]):
    """Logs a reading a few times inside one hour, the way the state logger does."""
    for minute in minutes:
        logger.add(at + datetime.timedelta(minutes = minute), temperature4 = temperature, pumpState1 = pumpState)


def test_noStateLoggerMeansNoTrends():
    """An install without a database still works, it just has nothing to trend."""
    #Given: no state logger is configured
    calculator = TrendCalculator(None)

    #When / Then: nothing is available and nothing is calculated
    assert calculator.isAvailable == False
    assert calculator.get(POOL, NOW) == []
    assert calculator.getAll({1: POOL}, NOW) == {}


def test_shortTermComparesOldestHourToNewestHour():
    #Given: the pool warmed from 80 to 83 over the last three hours
    logger = StateLoggerStub(seedDays = 0)
    logHour(logger, NOW - datetime.timedelta(hours = 3), 80.0)
    logHour(logger, NOW - datetime.timedelta(hours = 2), 81.0)
    logHour(logger, NOW - datetime.timedelta(hours = 1), 83.0)

    #When: the trends are calculated
    short = TrendCalculator(logger).get(POOL, NOW)[0]

    #Then: the oldest hour and the newest hour of the window are compared
    assert short.hours == DependencyContainer.trendHours
    assert short.start == 80.0
    assert short.end == 83.0
    assert short.change == 3.0


def test_readingsAreAveragedWithinTheHour():
    #Given: the readings inside each hour move around
    logger = StateLoggerStub(seedDays = 0)
    logger.add(NOW - datetime.timedelta(hours = 3), temperature4 = 79.0, pumpState1 = "SPEED_2")
    logger.add(NOW - datetime.timedelta(hours = 3) + datetime.timedelta(minutes = 30), temperature4 = 81.0, pumpState1 = "SPEED_2")
    logger.add(NOW - datetime.timedelta(minutes = 50), temperature4 = 84.0, pumpState1 = "SPEED_2")
    logger.add(NOW - datetime.timedelta(minutes = 10), temperature4 = 86.0, pumpState1 = "SPEED_2")

    #When: the trend is calculated
    short = TrendCalculator(logger).get(POOL, NOW)[0]

    #Then: each end of the window is an average rather than a single reading
    assert short.start == 80.0
    assert short.end == 85.0
    assert short.change == 5.0


def test_readingsTakenWhileThePumpWasOffAreIgnored():
    """Water has to be moving past the sensor for the reading to mean anything."""
    #Given: the pump was off for the oldest hour and the readings were wrong because of it
    logger = StateLoggerStub(seedDays = 0)
    logHour(logger, NOW - datetime.timedelta(hours = 3), 60.0, pumpState = "OFF")
    logHour(logger, NOW - datetime.timedelta(hours = 1), 83.0)

    #When: the trend is calculated
    short = TrendCalculator(logger).get(POOL, NOW)[0]

    #Then: there was nothing usable at the start, so there is no trend to show
    assert short.start == None
    assert short.end == 83.0
    assert short.change == None


def test_longTermComparesTheSameBlockOfHours():
    """Comparing the afternoon to the middle of the night would say more about the sun than the pool."""
    #Given: readings across today and three days ago, including hours outside the window
    logger = StateLoggerStub(seedDays = 0)
    past = NOW - datetime.timedelta(days = DependencyContainer.trendDays)
    #Three days ago, inside the same three hour block
    logHour(logger, past - datetime.timedelta(hours = 3), 78.0)
    logHour(logger, past - datetime.timedelta(hours = 1), 78.0)
    #Three days ago, overnight and much colder. This must not be picked up.
    logHour(logger, past - datetime.timedelta(hours = 10), 55.0)
    #Today, inside the block
    logHour(logger, NOW - datetime.timedelta(hours = 3), 82.0)
    logHour(logger, NOW - datetime.timedelta(hours = 1), 82.0)

    #When: the trends are calculated
    long = TrendCalculator(logger).get(POOL, NOW)[1]

    #Then: only the matching block of hours is compared
    assert long.hours == DependencyContainer.trendDays * 24
    assert long.start == 78.0
    assert long.end == 82.0
    assert long.change == 4.0


def test_aBrokenDatabaseDoesNotBreakThePanel():
    #Given: a state logger that fails every query
    class Broken:
        def averageBetween(self, *args, **kwargs):
            raise Exception("The database is down")

    #When: the trends are calculated
    trends = TrendCalculator(Broken()).get(POOL, NOW)

    #Then: the windows come back empty instead of taking the page down
    assert [trend.change for trend in trends] == [None, None]


def test_getAllKeepsTheKeysItWasGiven():
    #Given: two readings logged to two different columns
    logger = StateLoggerStub(seedDays = 0)
    for hours, ph, orp in [(3, 7.2, 700.0), (1, 7.6, 750.0)]:
        at = NOW - datetime.timedelta(hours = hours)
        logger.add(at, PH1 = ph, Orp1 = orp, pumpState1 = "SPEED_2")
        logger.add(at + datetime.timedelta(minutes = 30), PH1 = ph, Orp1 = orp, pumpState1 = "SPEED_2")

    #When: they are asked for together
    trends = TrendCalculator(logger, maxDigits = 2).getAll({"ph": "PH1", "orp": "Orp1"}, NOW)

    #Then: they come back under the same keys
    assert trends["ph"][0].change == 0.4
    assert trends["orp"][0].change == 50.0


def test_anUnknownColumnHasNoTrend():
    #Given: a sensor that is not logged to any column
    #When: no column is handed in
    trends = TrendCalculator(StateLoggerStub(seedDays = 0)).get(None, NOW)

    #Then: it simply has no trend
    assert trends == []
