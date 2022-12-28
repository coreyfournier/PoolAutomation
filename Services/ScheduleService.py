import cherrypy
from Pumps.Pump import *
import dataclasses
import DependencyContainer
from Pumps.Schedule import *
logger = DependencyContainer.get_logger(__name__)

class ScheduleService:
    def __init__(self):	
        pass

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def schedules(self):
        """Gets all schedules active or inactive and their status

        Returns:
            Schedule: All schedule information
        """
        return [dataclasses.asdict(item) for item in DependencyContainer.scheduleRepo.schedules]