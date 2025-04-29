from sqlalchemy.orm import (scoped_session, sessionmaker, relationship,
                            backref)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (create_engine)
from IO.StateLoggerMsSqlRepo import parseConnectionString


class SqlDb():

    def __init__(self, sqlConnection):

        parsedConnection = parseConnectionString(sqlConnection)
        
        self._server = parsedConnection['server']
        self._databaseName = parsedConnection['databaseName']
        self._userName = parsedConnection['userName']
        self._userPassword = parsedConnection['userPassword']
        
        self.__engine = create_engine(
            f"mssql+pyodbc://{self._userName}:{self._userPassword}@{self._server}/{self._databaseName}?driver=SQL+Server+Native+Client+11.0"
            )

        self.Base = declarative_base()
        self.Base.query = self.getDbSession().query_property()

    
    def getDbSession(self):
        return scoped_session(sessionmaker(autocommit=False,
                                            autoflush=False,
                                            bind=self.__engine))

    