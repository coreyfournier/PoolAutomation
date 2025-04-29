import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from  Infrastructure.Db.Models.StateLog import StateLog as StateLogModel
from graphene import ObjectType, Connection, Node, Int
from sqlalchemy.sql import and_, or_
from datetime import datetime

class StateLog(SQLAlchemyObjectType):
    class Meta:
        model = StateLogModel
        # use `only_fields` to only expose specific fields ie "name"
        # only_fields = ("name",)   
        # use `exclude_fields` to exclude specific fields ie "last_name"
        # exclude_fields = ("last_name",)

        #count = Int()

