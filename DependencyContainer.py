import logging
import os
import logging.handlers
import socket
import logging, platform
import importlib.util

#defaults to DEBUG in the get_logger
#This must be set BEFORE any imports of custom code because it calls get_logger
log_level:int = None

#Set a file path here to redirect logging to a file.
#This must be set BEFORE any imports of custom code because it calls get_logger
log_to_file:str = None

#f= fahrenheit c=celsius
temperatureUnit = "f"

#Build number set by the GitHub workflow (ex: 2026.10.25.42). dev when running locally.
appVersion:str = os.environ.get("APP_VERSION") or "dev"

#format to show when it hours and minutes
short_time_format = "%I:%M%p"
#format to show for just an hour
hour_format = "%I %p"
dateFormat = "%m/%d/%Y"
timeFormat = "%H:%M"

MAX_YEAR:int = 2100
MIN_YEAR:int = 1970

#-----------------------------------------------------------------------------
# Trend configuration
# Trends are optional. They are only calculated when a state logger (database)
# has been configured. Every value used to calculate a trend lives here so an
# install only has to change it in one place.
#-----------------------------------------------------------------------------

#How many hours the short term trend looks back.
trendHours:int = 3
#How many days the long term trend looks back. The same block of hours (trendHours)
#is compared on both days, because the temperature swings from night to day.
trendDays:int = 3
#Size in hours of the window averaged at each end of the short term trend.
trendBucketHours:int = 1
#Id used by the environmental sensor. It is not a physical one wire device, so it gets its own id.
environmentalSensorId:int = 99
#Column in the state log that holds the pump state. Trends ignore any reading taken while this pump was off,
#because the water has to move for the readings to mean anything.
trendPumpStateColumn:str = "pumpState1"
#Value stored in trendPumpStateColumn when the pump is not running.
trendPumpOffValue:str = "OFF"
#Maps a temperature sensor id to the column it is logged to. This has to agree with Plugins/StateLogging.py.
#A sensor that is missing from here simply has no trend.
trendTemperatureColumns:"dict[int,str]" = {
    1: "temperature1",
    2: "temperature2",
    3: "temperature3",
    4: "temperature4",
    environmentalSensorId: "temperature5"
}
#Maps a chemistry reading to the column it is logged to. Keys are the property names of Devices.PoolChemistry.
trendChemistryColumns:"dict[str,str]" = {
    "ph": "PH1",
    "orp": "Orp1"
}

logServerName = 'ENV_LOG_SERVER_NAME'
logServerPort = 'ENV_LOG_SERVER_PORT'

_nameToLevel = {
    'CRITICAL': logging.CRITICAL,
    'FATAL': logging.FATAL,
    'ERROR': logging.ERROR,
    'WARN': logging.WARNING,
    'WARNING': logging.WARNING,
    'INFO': logging.INFO,
    'DEBUG': logging.DEBUG,
    'NOTSET': logging.NOTSET,
}
_log_format = '%(asctime)s %(levelname)s: [%(name)s.%(funcName)s] %(message)s'
_date_format = '%Y-%m-%d %H:%M:%S'
_loggersToWarn = ['pytds.tds.', 'cherrypy.','pytds.tds.submit_rpc','pytds.tds.parse_prelogin','pytds._connect','pytds.tds.process_env_chg']


if log_to_file == None:
    logging.basicConfig(
        level = log_level, 
        format = _log_format,
        datefmt = _date_format,
        force=True)
else:
    logging.basicConfig(
        filename = log_to_file,
        #new file for each logger created
        filemode='w',
        level = log_level, 
        format = _log_format,
        datefmt = _date_format,
        force=True)

for logger_name in _loggersToWarn:
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.WARN)


def get_logger(logger_name:str) -> logging.Logger:
    """Gets a universal logger specific to the caller
        Defaults the log level to DEBUG, if not environment variable is found for LOG_LEVEL
    Args:
        logger_name (str): Expecting __name__

    Returns:
        logging.Logger: logger
    """
    global log_level
    global log_to_file

    if log_level == None:
        log_level = logging.DEBUG
    elif 'LOG_LEVEL' in os.environ:
        log_level = _nameToLevel[os.environ['LOG_LEVEL']]
   
    logger = logging.getLogger(f'PoolAutomation.{logger_name}')    
    logger.setLevel(log_level)

    #Log to a syslog if it is specified in the environment    
    if (importlib.util.find_spec("syslog_rfc5424_formatter") is not None and logServerName in os.environ and logServerPort in os.environ):   
        from syslog_rfc5424_formatter import RFC5424Formatter     
        syslogHandler = logging.handlers.SysLogHandler(address=(os.environ[logServerName], int(os.environ[logServerPort])))        
        syslogHandler.setFormatter(RFC5424Formatter())
        logger.addHandler(syslogHandler)
    
    return logger

#from Lights.GloBrite import GloBrite 
from Devices.Pump import Pump
from Devices.Schedules import Schedules
from Devices.TemperatureBase import TemperatureBase
from lib.Actions import *
from lib.Variables import Variables
from Devices.Valves import Valves
from Devices.Pumps import Pumps
from Devices.Lights import Lights
from Devices.TemperatureSensors import TemperatureSensors
from IO.StateLoggerDuckDbRepo import StateLoggerDuckDbRepo
from IO.SeverSentEvents import *
from Devices.AtlasScientific import *
from IO.GeneratorRepo import *
from lib.Entity import Entity



#Global event handler to broker events for SSE
serverSentEvents:ServerSentEvents = ServerSentEvents()

lights:Lights = None

#List of pumps description is the first item in the tuple, pump is the second.
pumps:Pumps = None

schedules:Schedules = None

#List of devices available. key is the name of the device, second is the device
temperatureDevices:TemperatureSensors = None

#Custom actions / code that can execute based on events fired in the system.
actions:Actions = None

variables:Variables = None

valves:Valves = None

stateLogger:StateLoggerDuckDbRepo = None

enviromentalSensor:AtlasScientific = None

generator:GeneratorRepo = None

#Plugins that were loaded. Set by Configuration.
plugins:"list" = []

def getEntities() -> "list[Entity]":
    """Gets everything the devices, variables, actions, schedules and plugins expose outside the app.
    Consumers (Home Assistant ...) use this instead of knowing about each kind of device.
    """
    entities:"list[Entity]" = []
    sources = []

    for collection in [pumps, valves, lights, temperatureDevices]:
        if(collection != None):
            sources.extend(collection.getAll())

    if(enviromentalSensor != None):
        sources.append(enviromentalSensor)
    if(variables != None):
        sources.append(variables)
    if(actions != None):
        sources.extend(actions.get())
    if(schedules != None):
        sources.append(schedules)
    sources.extend(plugins)

    for source in sources:
        entities.extend(source.getEntities() or [])

    return entities