import cherrypy
from Devices.PoolChemistry import PoolChemistry
from Devices.Pump import *
import dataclasses
import DependencyContainer
from Devices.TemperatureBase import TemperatureBase, TemperatureDevice
from lib.Trends import TrendCalculator


logger = DependencyContainer.get_logger(__name__)

class PoolChemistryService:
    def  __init__(self) -> None:
        pass       

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def sensor(self):        

        if(DependencyContainer.enviromentalSensor == None):
            return None
        else:
            sensors = DependencyContainer.enviromentalSensor.get()
            if(sensors == None):
                return None
            else:
                return dataclasses.asdict(sensors)

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def trends(self):
        """Gets how much each chemistry reading has moved over the configured windows.

        Like the temperature trends, this is the only place that reaches for the database. An install
        without one gets available=false and the panel shows the readings on their own.

        Returns:
            dict: available, and the trends keyed by the reading name (ph, orp).
        """
        calculator = TrendCalculator(maxDigits = 2)

        if(not calculator.isAvailable):
            logger.debug("No state logger is configured, so there are no trends to report.")
            return {"available": False, "trends": {}}

        trends = calculator.getAll(DependencyContainer.trendChemistryColumns)

        return {
            "available": True,
            "trends": {key: [trend.to_dict() for trend in items] for key, items in trends.items()}
        }
