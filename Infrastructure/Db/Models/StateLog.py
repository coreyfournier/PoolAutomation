from sqlalchemy import Column, Integer, String, Float, DateTime
import DependencyContainer
#from Infrastructure.Db.SqlDb import Base
from sqlalchemy.ext.declarative import declarative_base

#Base = declarative_base()
#Base.query = DependencyContainer.sqlDb.getDbSession().query_property()

class StateLog(DependencyContainer.Base):
    __tablename__ = 'StateLogs'
    
    temperature1 = Column(Float)
    temperature2 = Column(Float)
    temperature3 = Column(Float)
    temperature4 = Column(Float)
    temperature5 = Column(Float)
    pumpState1 = Column(String)
    pumpState2 = Column(String)
    pumpState3 = Column(String)
    pumpState4 = Column(String)
    pumpState5 = Column(String)
    valveState1 = Column(String)
    valveState2 = Column(String)
    valveState3 = Column(String)
    valveState4 = Column(String)
    valveState5 = Column(String)
    ScheduleActive1 = Column(Integer)
    ScheduleActive2 = Column(Integer)
    ScheduleActive3 = Column(Integer)
    ActionActive1 = Column(String)
    ActionActive2 = Column(String)
    ActionActive3 = Column(String)
    ActionActive4 = Column(String)
    ActionActive5 = Column(String)
    Orp1 = Column(Float)
    Orp2 = Column(Float)
    PH1 = Column(Float)
    PH2 = Column(Float)
    Pressure1 = Column(Float)
    Pressure2 = Column(Float)
    Pressure3 = Column(Float)
    Pressure4 = Column(Float)
    CreatedDate = Column(DateTime, primary_key=True)
