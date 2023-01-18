from pickle import TRUE
import cherrypy
import os
import DependencyContainer


class LightService:
    def __init__(self):	
        self.lights = DependencyContainer.lights

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get(self):
        temp = [x.to_dict() for x in self.lights.getAll()]
        return temp

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def change(self, name:str, sceneIndex:int):
        cherrypy.response.headers['Content-Type'] = 'application/json'
        light = self.lights.get(name)
        light.change(int(sceneIndex))

        return "OK"

    @cherrypy.expose
    def off(self, name:str):
        self.lights.get(name).off()
        return "OK"


