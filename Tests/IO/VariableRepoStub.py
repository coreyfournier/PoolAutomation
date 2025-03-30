import json
from typing import Callable
import os
from lib.Variable import *
from marshmallow import Schema, fields, EXCLUDE
from IO.IVariableRepo import IVariableRepo

class VariableRepoStub(IVariableRepo):
    def __init__(self) -> None:
        super().__init__()

    def save(self):
        #Don't save
        pass