import cherrypy
from Devices.Pump import *
import dataclasses
import DependencyContainer
from Devices.TemperatureBase import TemperatureBase, TemperatureDevice
from lib.Trends import TrendCalculator


logger = DependencyContainer.get_logger(__name__)

class TemperatureService:
    def  __init__(self) -> None:
        pass
       

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def sensors(self):
        tempSensors = DependencyContainer.temperatureDevices.getAll()
        if(tempSensors == None):
            items = []
        else :
            items = [
                {
                    "id": item.id,
                    "name": item.displayName, 
                    "temp": item.getAsLocal(True),
                    "unit": DependencyContainer.temperatureUnit.upper()
                } 
                #Loop through all the items creating the dictionary output
                for item in tempSensors
            ]

        if(DependencyContainer.enviromentalSensor != None):
            sensor = DependencyContainer.enviromentalSensor.get()
            if(sensor != None):
                items.append(
                    {
                    "id": DependencyContainer.environmentalSensorId,
                    "name": "Environmental", 
                    "temp": DependencyContainer.enviromentalSensor.get().temperature,
                    "unit": DependencyContainer.temperatureUnit.upper()
                })            

        return items

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def trends(self):
        """Gets how much each sensor has moved over the configured windows.

        The sensors themselves have no idea a database exists. This is the only place that asks for one,
        and it answers with available=false when the install does not have one, so the UI just leaves
        the trends off the panels.

        Returns:
            dict: available, and the trends keyed by sensor id.
        """
        calculator = TrendCalculator()

        if(not calculator.isAvailable):
            logger.debug("No state logger is configured, so there are no trends to report.")
            return {"available": False, "trends": {}}

        sensors = DependencyContainer.temperatureDevices.getAll()
        ids = [] if sensors == None else [item.id for item in sensors]

        if(DependencyContainer.enviromentalSensor != None):
            ids.append(DependencyContainer.environmentalSensorId)

        #A sensor that isn't logged to a column simply has no trend.
        columns = {
            id: DependencyContainer.trendTemperatureColumns[id]
            for id in ids
            if id in DependencyContainer.trendTemperatureColumns
        }

        trends = calculator.getAll(columns)

        return {
            "available": True,
            "trends": {
                #Json object keys are strings, so the ids go over the wire as strings.
                str(id): [trend.to_dict() for trend in items] for id, items in trends.items()
            }
        }
