import datetime

class StateLoggerDuckDbRepo():
    def __init__(self, databaseFile:str) -> None:
        import duckdb
        self.__connection = duckdb.connect(databaseFile, read_only=False)

        tableScript = """CREATE TABLE IF NOT EXISTS StateLogs(
            temperature1 REAL,
            temperature2 REAL,
            temperature3 REAL,
            temperature4 REAL,
            temperature5 REAL,
            pumpState1 VARCHAR(10),
            pumpState2 VARCHAR(10),
            pumpState3 VARCHAR(10),
            pumpState4 VARCHAR(10),
            pumpState5 VARCHAR(10),
            valveState1 BOOLEAN,
            valveState2 BOOLEAN,
            valveState3 BOOLEAN,
            valveState4 BOOLEAN,
            valveState5 BOOLEAN,
            ScheduleActive1 BOOLEAN,
            ScheduleActive2 BOOLEAN,
            ScheduleActive3 BOOLEAN,
            ActionActive1 VARCHAR(20),
            ActionActive2 VARCHAR(20),
            ActionActive3 VARCHAR(20),
            ActionActive4 VARCHAR(20),
            ActionActive5 VARCHAR(20),
            Orp1 REAL,
            Orp2 REAL,
            PH1 REAL,
            PH2 REAL,
            Pressure1 REAL,
            Pressure2 REAL,
            Pressure3 REAL,
            Pressure4 REAL,
            CreatedDate TIMESTAMP
            )
        """

        self.__connection.execute(tableScript)

        self.__connection.execute("DESCRIBE SELECT * FROM StateLogs")
        self.__tblColumns = [x[0].lower() for x in self.__connection.fetchall()]

    def add(self,
        temperature1:float = None,
        temperature2:float = None,
        temperature3:float = None,
        temperature4:float = None,
        temperature5:float = None,
        pumpState1:str = None,
        pumpState2:str = None,
        pumpState3:str = None,
        pumpState4:str = None,
        pumpState5:str = None,
        valveState1:str = None,
        valveState2:str = None,
        valveState3:str = None,
        valveState4:str = None,
        valveState5:str = None,
        ScheduleActive1:int = None,
        ScheduleActive2:int = None,
        ScheduleActive3:int = None,
        ActionActive1:str = None,
        ActionActive2:str = None,
        ActionActive3:str = None,
        ActionActive4:str = None,
        ActionActive5:str = None,
        Orp1:float = None,
        Orp2:float = None,
        PH1:float = None,
        PH2:float = None,
        Pressure1:float = None,
        Pressure2:float = None,
        Pressure3:float = None,
        Pressure4:float = None
    ):
        result = self.__connection.execute(f"INSERT INTO StateLogs VALUES({'?,'*31}?)",
            [temperature1,
            temperature2,
            temperature3,
            temperature4,
            temperature5,
            pumpState1,
            pumpState2,
            pumpState3,
            pumpState4,
            pumpState5,
            valveState1,
            valveState2,
            valveState3,
            valveState4,
            valveState5,
            ScheduleActive1,
            ScheduleActive2,
            ScheduleActive3,
            ActionActive1,
            ActionActive2,
            ActionActive3,
            ActionActive4,
            ActionActive5,
            Orp1,
            Orp2,
            PH1,
            PH2,
            Pressure1,
            Pressure2,
            Pressure3,
            Pressure4,
            datetime.datetime.now()
            ])

    def query(self, where:str, columns:"list[str]") -> list:
        """_summary_

        Args:
            where (str): Free text where statement. This is NOT validated!!!!!!!!!!
            columns (list[str]): columns are validated against the schema

        Raises:
            Exception: Columns not found

        Returns:
            list: Array of arrays. Columns are returned in the order in which they were selected.
        """
        conn = self.__connection.cursor()
        if(len(columns) > 0):
            if(len(columns) == 1 and columns[0] == "*"):
                select = "*"
            else:
                for col in columns:
                    if(col.lower() not in self.__tblColumns):
                        raise Exception(f"Unknown column {col}")

                select = ",".join(columns)
        else:
            raise Exception("No columns to select")
                
        conn.execute(f"SELECT {select} FROM StateLogs WHERE {where}")
        return conn.fetchall()

    def averageBetween(self, column:str, start:datetime.datetime, end:datetime.datetime, pumpStateColumn:str = None, pumpOffValue:str = "OFF") -> float:
        """Averages a single column over a window of time.

        Args:
            column (str): Column to average. Validated against the schema.
            start (datetime): Start of the window. Inclusive.
            end (datetime): End of the window. Exclusive.
            pumpStateColumn (str, optional): When given, readings taken while that pump was off are skipped.
                The water has to be moving for a reading to mean anything. Validated against the schema.
            pumpOffValue (str, optional): Value the pump column holds when it is off. Defaults to "OFF".

        Raises:
            Exception: Columns not found

        Returns:
            float: None when nothing was logged in the window.
        """
        self._validateColumn(column)

        filters = f'"{column}" IS NOT NULL AND CreatedDate >= ? AND CreatedDate < ?'

        if(pumpStateColumn != None):
            self._validateColumn(pumpStateColumn)
            filters += f' AND "{pumpStateColumn}" IS NOT NULL AND "{pumpStateColumn}" != ?'
            parameters = [start, end, pumpOffValue]
        else:
            parameters = [start, end]

        conn = self.__connection.cursor()
        conn.execute(f'SELECT AVG("{column}") FROM StateLogs WHERE {filters}', parameters)
        row = conn.fetchone()
        return None if row == None else row[0]

    def _validateColumn(self, column:str) -> None:
        """The column ends up in the statement, so it never gets there without being checked first."""
        if(column == None or column.lower() not in self.__tblColumns):
            raise Exception(f"Unknown column {column}")

    def agg(self, where:str=None,columns:"list[str]" = None) -> list:
        conn = self.__connection.cursor()
        conn.execute(f"SELECT ROUND(AVG(temperature1),1), ROUND(AVG(temperature2),1), ROUND(AVG(temperature3),1), ROUND(AVG(temperature4),1), date_part('hour', CreatedDate) AS Hour FROM StateLogs GROUP BY date_part('hour', CreatedDate)")
        return conn.fetchall()
        