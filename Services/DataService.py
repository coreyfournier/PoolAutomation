from pickle import TRUE
import cherrypy
import os
import DependencyContainer


class DataService():
    def __init__(self) -> None:
        pass        

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get(self, query:str, table:str = "StateLogs", columns:str="*") ->"list[list[any]]":
        """_summary_
            Example: /data/get?query=CreatedDate%20ge%202023-02-10&columns=temperature2,temperature2,temperature1,pumpState1,ScheduleActive1,CreatedDate
        Args:
            query (str): odata where statement
            table (str, optional): Table name. To support others in the future. Defaults to "StateLogs".
            columns (str, optional): Columns to select comma seperated.. Defaults to "*".

        Returns:
            _type_: Array of arrays in json
        """
        where_clause = DependencyContainer.stateLogger.odataQueryToWhereStatement(query)
        return DependencyContainer.stateLogger.query(where_clause, columns.split(","))

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def tempStats(self, query:str):
        where_clause = DependencyContainer.stateLogger.odataQueryToWhereStatement(query)
        data = DependencyContainer.stateLogger.agg(where_clause)
        
        names = [x.displayName for x in DependencyContainer.temperatureDevices.getAll()]
        allItems = {}
        hours = set()
        for idx, name in enumerate(names):
            if(name not in allItems):
                allItems[name] = []
            for item in data:                
                allItems[name].append(item[idx]) 

                if(data[-1] not in hours):
                    hours.add(item[-1])

        return {
            "hours":list(hours),
            "data" : [{"name": key, "data" : item} for key, item in allItems.items()]
            }
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def heroes(self):
        return [
            {"id":1, "name":"test1"},
            {"id":2, "name":"test2"},
            ]