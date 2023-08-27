from pickle import TRUE
import cherrypy
import os
import DependencyContainer
import json
from lib.Event import Event

logger = DependencyContainer.get_logger(__name__)

class DataService():
    def __init__(self) -> None:
        pass
   
    @cherrypy.expose
    def getUpdate(self, _=None):
        cherrypy.response.headers["Content-Type"] = "text/event-stream;charset=utf-8"
        cherrypy.response.headers['Cache-Control'] = 'no-cache'

        def content(event:Event):
            logger.debug(f"New event '{event.dataType}'")
            eventDict = event.to_dict()            
            data = 'retry: 200\ndata: ' + json.dumps(eventDict) +  '\n\n'
            logger.debug(data)
            return data
       
        return DependencyContainer.serverSentEvents.getEvents(content)

    getUpdate._cp_config = {'response.stream': True, 'tools.encode.encoding':'utf-8'}

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
        #No state logger, so don't try to query it.
        if(DependencyContainer.stateLogger == None):
            return { "hours":[], "data" : [] }        

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
            "hours":[x.strftime(DependencyContainer.hour_format) for x in sorted(list(hours))],
            "data" : [{"name": key, "data" : item} for key, item in allItems.items()]
            }
    
    