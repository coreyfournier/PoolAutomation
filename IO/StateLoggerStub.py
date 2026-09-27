import datetime
import math
import random
import sqlite3
import threading
import DependencyContainer

logger = DependencyContainer.get_logger(__name__)


class StateLoggerStub():
    """An in memory state logger for running locally without a database.

    The same idea as the GPIO and temperature stubs. Everything that reads history, the stats
    chart and the trends on the temperature and chemistry panels, works off made up readings
    instead of being switched off. It mirrors StateLoggerMsSqlRepo so nothing above it can tell
    the difference.

    Nothing is written to disk, so the history starts over every time the app restarts.
    """

    #Matches the schema the real state loggers create.
    COLUMNS = (
        [f"temperature{index}" for index in range(1, 6)] +
        [f"pumpState{index}" for index in range(1, 6)] +
        [f"valveState{index}" for index in range(1, 6)] +
        [f"ScheduleActive{index}" for index in range(1, 4)] +
        [f"ActionActive{index}" for index in range(1, 6)] +
        ["Orp1", "Orp2", "PH1", "PH2"] +
        [f"Pressure{index}" for index in range(1, 5)]
    )

    #Sqlite compares dates as text, so everything has to be written the same way.
    DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"

    #How long the made up pump runs each day. The block ends at whatever time of day the app was
    #started, so the recent hours always have readings no matter when you run this. Everything
    #outside the block is logged with the pump off, which is what makes the filter on the trends
    #worth looking at locally.
    PUMP_RUN_HOURS = 9

    def __init__(self, seedDays:int = None, seedIntervalMinutes:int = 5) -> None:
        """
        Args:
            seedDays (int, optional): Days of history to invent. Defaults to one more day than the
                longest trend window, so both ends of every trend have something to average.
                Zero starts empty, which is what the tests want.
            seedIntervalMinutes (int, optional): Gap between the invented readings. Matches how
                often Plugins/StateLogging.py writes a real one.
        """
        from odata_query.grammar import ODataParser, ODataLexer

        self.__lexer = ODataLexer()
        self.__parser = ODataParser()
        #Sqlite objects belong to the thread that made them unless told otherwise, and the web
        #server reads this from request threads while the worker writes to it.
        self.__connection = sqlite3.connect(":memory:", check_same_thread = False)
        self.__lock = threading.Lock()
        self.__tblColumns = [column.lower() for column in self.COLUMNS] + ["createddate"]

        definitions = ",".join([f'"{column}"' for column in self.COLUMNS])
        self.__connection.execute(f"CREATE TABLE StateLogs({definitions}, CreatedDate TEXT)")

        if(seedDays == None):
            seedDays = DependencyContainer.trendDays + 1

        if(seedDays > 0):
            self._seed(seedDays, seedIntervalMinutes)

    def add(self, createdDate:datetime.datetime = None, **values):
        """Logs one row.

        Args:
            createdDate (datetime, optional): Defaults to now, the way the real loggers do it.
            **values: Column values. Anything that is not a column is ignored, so this keeps
                working when a caller passes something this schema does not have.
        """
        if(createdDate == None):
            createdDate = datetime.datetime.now()

        values = {column: value for column, value in values.items() if column in self.COLUMNS}
        names = ",".join([f'"{column}"' for column in list(values.keys()) + ["CreatedDate"]])
        placeholders = ",".join(["?"] * (len(values) + 1))
        parameters = list(values.values()) + [createdDate.strftime(self.DATE_FORMAT)]

        with self.__lock:
            self.__connection.execute(f"INSERT INTO StateLogs({names}) VALUES({placeholders})", parameters)

    def query(self, where:str, columns:"list[str]") -> list:
        """See StateLoggerMsSqlRepo.query.

        Args:
            where (str): Free text where statement. This is NOT validated!!!!!!!!!!
            columns (list[str]): columns are validated against the schema

        Raises:
            Exception: Columns not found

        Returns:
            list: Array of arrays. Columns are returned in the order in which they were selected.
        """
        if(len(columns) > 0):
            if(len(columns) == 1 and columns[0] == "*"):
                select = "*"
            else:
                for column in columns:
                    self._validateColumn(column)

                select = ",".join(columns)
        else:
            raise Exception("No columns to select")

        with self.__lock:
            cursor = self.__connection.execute(f"SELECT {select} FROM StateLogs WHERE {where}")
            return cursor.fetchall()

    def agg(self, where:str = None, columns:"list[str]" = None) -> list:
        """Averages the temperatures by hour, the same shape the real loggers return."""
        query = f"""SELECT
            ROUND(AVG(temperature1),1) AS temperature1,
            ROUND(AVG(temperature2),1) AS temperature2,
            ROUND(AVG(temperature3),1) AS temperature3,
            ROUND(AVG(temperature4),1) AS temperature4,
            CAST(strftime('%H', CreatedDate) AS INTEGER) AS Hour
                FROM StateLogs
                WHERE {where}
                GROUP BY strftime('%H', CreatedDate)
                ORDER BY strftime('%H', CreatedDate)"""

        logger.debug(query)

        with self.__lock:
            cursor = self.__connection.execute(query)
            #The caller formats the last column as a time, so it goes back as one rather than as text.
            return [tuple(row[:-1]) + (datetime.time(row[-1]),) for row in cursor.fetchall()]

    def averageBetween(self, column:str, start:datetime.datetime, end:datetime.datetime, pumpStateColumn:str = None, pumpOffValue:str = "OFF") -> float:
        """See StateLoggerMsSqlRepo.averageBetween."""
        self._validateColumn(column)

        filters = f'"{column}" IS NOT NULL AND CreatedDate >= ? AND CreatedDate < ?'
        parameters = [start.strftime(self.DATE_FORMAT), end.strftime(self.DATE_FORMAT)]

        if(pumpStateColumn != None):
            self._validateColumn(pumpStateColumn)
            filters += f' AND "{pumpStateColumn}" IS NOT NULL AND "{pumpStateColumn}" != ?'
            parameters.append(pumpOffValue)

        with self.__lock:
            cursor = self.__connection.execute(f'SELECT AVG("{column}") FROM StateLogs WHERE {filters}', parameters)
            row = cursor.fetchone()
            return None if row == None else row[0]

    def odataQueryToWhereStatement(self, query:str) -> str:
        from odata_query.sql import AstToSqlVisitor

        ast = self.__parser.parse(self.__lexer.tokenize(query))

        visitor = AstToSqlVisitor()
        #I have no idea why it does this
        return visitor.visit(ast).replace(" DATE ", "").replace(" TIMESTAMP ", "")

    def _validateColumn(self, column:str) -> None:
        """The column ends up in the statement, so it never gets there without being checked first."""
        if(column == None or column.lower() not in self.__tblColumns):
            raise Exception(f"Unknown column {column}")

    def _seed(self, days:int, intervalMinutes:int) -> None:
        """Invents a history so the trends and the stats chart have something to show right away.

        The readings drift up a little each day and rise and fall through each day, so both the
        short and the long trend come out with something in them.
        """
        #Whatever this install logs its readings to is what gets filled in.
        temperatureColumns = list(DependencyContainer.trendTemperatureColumns.values())
        chemistryColumns = DependencyContainer.trendChemistryColumns

        now = datetime.datetime.now()
        start = now - datetime.timedelta(days = days)
        interval = datetime.timedelta(minutes = intervalMinutes)
        at = start
        rows = 0

        while at <= now:
            hoursIn = (at - start).total_seconds() / 3600
            #A slow climb across the whole stretch, so three days ago reads cooler than today.
            drift = 0.5 * (hoursIn / 24)
            #Warmest late in the afternoon, coolest before dawn.
            swing = 2.5 * math.sin((at.hour + at.minute / 60 - 9) / 24 * 2 * math.pi)
            isRunning = self._pumpWasRunning(at, now)

            values = {
                #Each sensor sits at its own level so the cards do not all read the same.
                column: round(88 + index * 1.5 + drift + swing + random.uniform(-0.15, 0.15), 1)
                for index, column in enumerate(temperatureColumns)
            }

            if("ph" in chemistryColumns):
                values[chemistryColumns["ph"]] = round(7.4 + swing * 0.02 + random.uniform(-0.01, 0.01), 2)
            if("orp" in chemistryColumns):
                values[chemistryColumns["orp"]] = round(700 + swing * 5 + random.uniform(-1, 1), 2)

            values[DependencyContainer.trendPumpStateColumn] = "SPEED_2" if isRunning else DependencyContainer.trendPumpOffValue

            self.add(at, **values)
            at += interval
            rows += 1

        logger.info(f"State logger stub seeded with {rows} made up readings going back {days} days.")

    def _pumpWasRunning(self, at:datetime.datetime, seededTo:datetime.datetime) -> bool:
        """Was the made up pump running at this time of day.

        The block is measured backwards from the time of day the seeding ended rather than from a
        fixed hour. Run the app at ten at night and the last few hours still have readings, so the
        trends have something to show instead of looking broken.
        """
        minutesInADay = 24 * 60
        endOfBlock = seededTo.hour * 60 + seededTo.minute
        minutesBefore = (endOfBlock - (at.hour * 60 + at.minute)) % minutesInADay

        return minutesBefore < self.PUMP_RUN_HOURS * 60
