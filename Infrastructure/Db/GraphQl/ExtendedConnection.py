
import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from  Infrastructure.Db.Models.StateLog import StateLog as StateLogModel
from graphene import ObjectType, Connection, Node, Int

class ExtendedConnection(Connection):
    class Meta:
        abstract = True

    #total_count = Int()
    #edge_count = Int()