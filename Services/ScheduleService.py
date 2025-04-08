import cherrypy
from Devices.Pump import *
import dataclasses
import DependencyContainer
from Devices.Schedule import *
import json
logger = DependencyContainer.get_logger(__name__)

class ScheduleService:
    def __init__(self):	
        pass

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.accept(media="application/json")
    def schedules(self):        
        """Gets all schedules active or inactive and their status

        Returns:
            Schedule: All schedule information
        """
        
        if(cherrypy.request.method == 'GET'):
            return  self.get_schedules()
        elif(cherrypy.request.method == 'POST'):
            return self.post_schedules(cherrypy.request)
        
    def post_schedules(self, request):
        cl = request.headers['Content-Length']
        rawbody = request.body.read(int(cl)).decode('ascii')
        data = PumpSchedule.schema().loads(rawbody, many=True) 

        try:    
            DependencyContainer.schedules.save(data)

            return {
                "success":True
            }
        except Exception as e :
            return {
                "success":False,
                "error": str(e)
            }
        
    def get_schedules(self):
        schedules = [item.to_dict() for item in DependencyContainer.schedules.get()]

        if(DependencyContainer.pumps != None):
            for schedule in schedules:
                for pump in schedule["pumps"]:                
                    pumpInfo = DependencyContainer.pumps.get(pump["name"])
                    if(pumpInfo == None):
                        pump["displayName"] = "Missing"
                    else:
                        pump["displayName"] = pumpInfo.displayName
                        
        return {
            "overrides": [{"name": item.name, "displayName": item.displayName } for item in DependencyContainer.actions.getScheduleOverrides()],
            "schedules": schedules,
            "MAX_YEAR" : DependencyContainer.MAX_YEAR,
            "MIN_YEAR" : DependencyContainer.MIN_YEAR
        }
                
            