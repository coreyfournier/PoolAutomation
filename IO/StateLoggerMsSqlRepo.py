import datetime
import pytds
import DependencyContainer
import re

logger = DependencyContainer.get_logger(__name__)

class StateLoggerMsSqlRepo():
    """
    Example command to start sql on docker
    sudo docker run -v "/volume1/docker/mssql/data:/var/opt/mssql/data" -v "/volume1/docker/mssql/log:/var/opt/mssql/log" -v "/volume1/docker/mssql/backups:/var/backups" -v "/volume1/docker/mssql/secrets:/var/opt/mssql/secrets" -e "ACCEPT_EULA=Y" -e "MSSQL_PID=standard" -e "SA_PASSWORD=**********" -e "MSSQL_AGENT_ENABLED=True" -e "TZ=America/Chicago" -p 1433:1433 -d mcr.microsoft.com/mssql/server:2022-latest
    
    """
    def __init__(self, sqlConnection:str, databaseName = None) -> None:    
        userId = re.findall("User Id=([a-zA-Z0-9\-_\.]+);", sqlConnection)
        password = re.findall("Password=([a-zA-Z0-9\+\-_=!\.]+);", sqlConnection)
        server = re.findall("Server=([a-zA-Z0-9\-_\.]+);", sqlConnection)        
        logger.debug(f"password='{password}'")
        if(databaseName == None):
            databaseName = re.findall("Database=([a-zA-Z0-9\-_\.]+);", sqlConnection)
            if(len(databaseName) == 0):
                databaseName = None
            else:
                databaseName = databaseName[0]
                

        if(len(userId) == 0):
            raise Exception("User Id=X; not found in connection string")
        if(len(password) == 0):
            raise Exception("Password=X; not found in connection string")        
        if(len(server) == 0):
            raise Exception("Server=X; not found in connection string")
        if(databaseName == None):
            raise Exception("Database=X; not found in connection string")
        
        try:
            self.__connection = pytds.connect(server[0], databaseName, userId[0], password[0], autocommit=True)
        except Exception as ex:
            if(len(ex.args) > 1 and "Cannot open database" in ex.args[1]):
                logger.info(f"Creating database {databaseName}")

                #Switch to master to create the database.
                conn = pytds.connect(server[0], "master", userId[0], password[0])

                cursor = conn.cursor()

                dbScript = f"""        
                    IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = '{databaseName}')
                    BEGIN
                        CREATE DATABASE {databaseName};
                    END;
                """
                cursor.execute(dbScript)
                
                self.__connection = pytds.connect(server[0], databaseName, userId[0], password[0], autocommit=True)
            else:
                raise ex

        tableScript = """USE PoolAutomation;
            IF OBJECT_ID('StateLogs', 'U') IS NULL 
            BEGIN
                CREATE TABLE StateLogs(
                        temperature1 decimal(4,2) NULL,
                        temperature2 decimal(4,2) NULL,
                        temperature3 decimal(4,2) NULL,
                        temperature4 decimal(4,2) NULL,
                        temperature5 decimal(4,2) NULL,
                        pumpState1 VARCHAR(10) NULL,
                        pumpState2 VARCHAR(10) NULL,
                        pumpState3 VARCHAR(10) NULL,
                        pumpState4 VARCHAR(10) NULL,
                        pumpState5 VARCHAR(10) NULL,
                        valveState1 BIT NULL,
                        valveState2 BIT NULL,
                        valveState3 BIT NULL,
                        valveState4 BIT NULL,
                        valveState5 BIT NULL,
                        ScheduleActive1 BIT NULL,
                        ScheduleActive2 BIT NULL,
                        ScheduleActive3 BIT NULL,
                        ActionActive1 VARCHAR(20) NULL,
                        ActionActive2 VARCHAR(20) NULL,
                        ActionActive3 VARCHAR(20) NULL,
                        ActionActive4 VARCHAR(20) NULL,
                        ActionActive5 VARCHAR(20) NULL,
                        Orp1 decimal(4,2)  NULL,
                        Orp2 decimal(4,2) NULL,
                        PH1 decimal(4,2) NULL,
                        PH2 decimal(4,2) NULL,
                        Pressure1 decimal(4,2) NULL,
                        Pressure2 decimal(4,2) NULL,
                        Pressure3 decimal(4,2) NULL,
                        Pressure4 decimal(4,2) NULL,
                        CreatedDate datetime2 
                        )
                        CREATE CLUSTERED COLUMNSTORE INDEX [CCI-StateLogs] ON StateLogs
            END
        """

        cursor = self.__connection.cursor()
        cursor.execute(tableScript)
        
        db_cursor = cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'StateLogs'")
        self.__tblColumns = [x[0].lower() for x in list(db_cursor)]

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
        cursor = self.__connection.cursor()
        statement = f"INSERT INTO StateLogs VALUES({'%s,'*31}%s)"
        data = [temperature1,
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
            ]
        logger.debug(statement)
        result = cursor.execute(statement, data)

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

    def agg(self, where:str=None,columns:"list[str]" = None) -> list:
        conn = self.__connection.cursor()
        conn.execute(f"SELECT ROUND(AVG(temperature1),1), ROUND(AVG(temperature2),1), ROUND(AVG(temperature3),1), ROUND(AVG(temperature4),1), date_part('hour', CreatedDate) AS Hour FROM StateLogs GROUP BY date_part('hour', CreatedDate)")
        return conn.fetchall()
        