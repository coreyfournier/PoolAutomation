import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from Infrastructure.Db.Models.StateLog import StateLog as StateLogModel
#from Infrastructure.Db.Models.TempTrend import TempTrend as TempTrendModel
from graphene import ObjectType, Connection, Node, Int
from sqlalchemy.sql import and_, or_
from datetime import datetime
from Infrastructure.Db.GraphQl.StateLog import StateLog
import DependencyContainer
from Infrastructure.Db.GraphQl.ExtendedConnection import ExtendedConnection

class Query(graphene.ObjectType):
    statelogs = graphene.List(StateLogModel)
    
    #tempTrends = graphene.List(TempTrendModel)
    
    #connection_class = ExtendedConnection

    def resolve_statelogs(root, info, today:datetime = None, **kwargs):
        print(kwargs)
        query = StateLog.get_query(info)  # SQLAlchemy query
        result = query
        
        if(today == None):
            today = datetime.now()
        
        startDate = today.strftime("%Y-%m-%d 00:00:00")
        endDate = today.strftime("%Y-%m-%d 23:59:59")
        
        result = result.filter(
            and_(StateLogModel.CreatedDate >= startDate, StateLogModel.CreatedDate <= endDate))
        
        if('limit' in kwargs):
            result = result.limit(kwargs['limit'])

        return result    

    #def resolve_tempTrends(self, info, days:int = 10):
    #    query = DependencyContainer.stateLogger.tempTrendQuery(days)
#
#        with DependencyContainer.sqlDb.getDbSession() as connection:
#            result = connection.execute(query)
#            return result        
    
    
    #def resolve_total_count(root, info, **kwargs):
    #    return 1
    #def resolve_edge_count(root, info, **kwargs):
    #    return 3