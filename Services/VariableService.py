import cherrypy
from Devices.Pump import *
import dataclasses
import DependencyContainer
from lib.Variable import *
from lib.Variables import Variables

logger = DependencyContainer.get_logger(__name__)

class VariableService:
    def  __init__(self) -> None:
        pass

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def change(self):
        #make sure the variable exists
        
        data = cherrypy.request.json
        name = data["name"]
        value = data["value"]

        variable = DependencyContainer.variables.get(name)
        if(variable == None):
            raise Exception(f"Missing variable '{name}'")
        else:
            DependencyContainer.variables.get(name).value = value
            return variable.to_dict()
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get(self, name:str):
        variable = DependencyContainer.variables.get(name)
        
        if(variable == None):
            return None
        else:
            return variable.to_dict()
        
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def UiVariables(self):
        return [temp.to_dict() for temp in DependencyContainer.variables.getVariablesForUi()]
