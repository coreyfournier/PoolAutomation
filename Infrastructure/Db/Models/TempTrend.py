from sqlalchemy import Column, Integer, String, Float, DateTime,Date
import DependencyContainer
from sqlalchemy.ext.declarative import declarative_base
#from Infrastructure.Db.SqlDb import Base

#Base = declarative_base()
#Base.query = DependencyContainer.sqlDb.getDbSession().query_property()

class TempTrend(Base):
    #__tablename__ = 'StateLogs'
    #Needed because this table is used elsewhere
    #__table_args__ = {'extend_existing': True}
    
    temperature1 = Column(Float)
    temperature2 = Column(Float)
    temperature3 = Column(Float)
    temperature4 = Column(Float)
    temperature5 = Column(Float)    
    CreatedDate = Column(Date, primary_key=True)
