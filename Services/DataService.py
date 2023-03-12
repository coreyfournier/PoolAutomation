from pickle import TRUE
import cherrypy
import os
import DependencyContainer
import odata_query
from odata_query.grammar import ODataParser, ODataLexer
from odata_query.sql import AstToSqlVisitor
from IO.StateLoggerDuckDbRepo import StateLoggerDuckDbRepo



class DataService():
    def __init__(self) -> None:
        self.__lexer = ODataLexer()
        self.__parser = ODataParser()
        

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
        ast = self.__parser.parse(self.__lexer.tokenize(query))

        visitor = AstToSqlVisitor()
        where_clause = visitor.visit(ast)

        return DependencyContainer.stateLogger.query(where_clause, columns.split(","))

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def tempStats(self):
        data = DependencyContainer.stateLogger.agg()
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