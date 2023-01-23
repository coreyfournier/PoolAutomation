import logging
import os

#defaults to DEBUG in the get_logger
#This must be set BEFORE any imports of custom code because it calls get_logger
log_level:int = None

#Set a file path here to redirect logging to a file.
#This must be set BEFORE any imports of custom code because it calls get_logger
log_to_file:str = None

#f= fahrenheit c=celsius 
temperatureUnit = "f"

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

    log_format = '%(asctime)s %(levelname)s: [%(name)s.%(funcName)s] %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    logger = logging.getLogger(f'PoolAutomation.{logger_name}')    
    logger.setLevel(log_level)
    #limiting what is sent out for cherrypy
    cherrypyLogger = logging.getLogger('cherrypy.')
    cherrypyLogger.setLevel(logging.WARN)

    if log_to_file == None:
        logging.basicConfig(
            level = log_level, 
            format = log_format,
            datefmt = date_format,
            force=True)
    else:
        logging.basicConfig(
            filename = log_to_file,
            #new file for each logger created
            filemode='w',
            level = log_level, 
            format = log_format,
            datefmt = date_format,
            force=True)
    return logger

#from Lights.GloBrite import GloBrite 
from Devices.Pump import Pump
from Devices.Schedules import Schedules
from Devices.Temperature import Temperature
from lib.Actions import *
from lib.Variables import Variables
from Devices.Valves import Valves
from Devices.Pumps import Pumps
from Devices.Lights import Lights
from Devices.TemperatureSensors import TemperatureSensors

lights:Lights = None

#List of pumps description is the first item in the tuple, pump is the second.
pumps:Pumps = None

schedules:Schedules = None

#List of devices available. key is the name of the device, second is the device
temperatureDevices:TemperatureSensors = None

#Custom actions / code that can execute based on the environment.
actions:Actions = None

variables:Variables = None

valves:Valves = None