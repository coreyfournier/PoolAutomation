import logging
import os

#defaults to DEBUG in the get_logger
#This must be set BEFORE any imports of custom code because it calls get_logger
log_level:int = None

#Set a file path here to redirect logging to a file.
#This must be set BEFORE any imports of custom code because it calls get_logger
log_to_file:str = None

#f= fahrenheit c=celsius 
tempFormat = "f"

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
from Pumps.Pump import Pump
from IO.ScheduleRepo import ScheduleRepo
from Temperature.Temperature import Temperature
from lib.Actions import *
from lib.Variables import Variables
from lib.Valves import Valves

light = None

#List of pumps description is the first item in the tuple, pump is the second.
pumps:"list[tuple(str,Pump)]" = None

scheduleRepo:ScheduleRepo = None

#List of devices available. key is the name of the device, second is the device
temperatureDevices:"dict[str,Temperature]" = {}

#Custom actions / code that can execute based on the environment.
actions:Actions = None

variables:Variables = None

valves:Valves = None