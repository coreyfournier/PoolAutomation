import duckdb
import datetime

class StateLoggerRepo():

    def __init__(self, databaseFile:str) -> None:
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
            valveState1 VARCHAR(10),
            valveState2 VARCHAR(10),
            valveState3 VARCHAR(10),
            valveState4 VARCHAR(10),
            valveState5 VARCHAR(10),
            ScheduleActive1 TINYINT,
            ScheduleActive2 TINYINT,
            ScheduleActive3 TINYINT,
            ActionActive1 VARCHAR(20),
            ActionActive2 VARCHAR(20),
            ActionActive3 VARCHAR(20),
            ActionActive4 VARCHAR(20),
            ActionActive5 VARCHAR(20),
            CreatedDate TIMESTAMP
            )
        """

        self.__connection.execute(tableScript)

        self.__connection.execute("DESCRIBE SELECT * FROM StateLogs")
        self.__tblColumns = [x[0].lower() for x in self.__connection.fetchall()]

    def Add(self,
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
        ActionActive5:str = None
    ):
        result = self.__connection.execute(f"INSERT INTO StateLogs VALUES({'?,'*23}?)",
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
            list: Array of arrays. I THINK in the order in which they were selected
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

        