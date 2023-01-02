import cherrypy
from Pumps.Pump import *
import dataclasses
import DependencyContainer
from lib.Variables import Variable

logger = DependencyContainer.get_logger(__name__)

class VariableService:
    def  __init__(self) -> None:
        pass

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def change(self, name:str, value:any):
        #make sure the variable exists

        variable = DependencyContainer.variables.get(str)
        if(variable == None):
            logger.warn(f"Adding new variable '{name}'")
            DependencyContainer.variables.addVariable(Variable(name, value, type(value)))
        else:
            DependencyContainer.variables.updateValue(name, value)
            return variable
        