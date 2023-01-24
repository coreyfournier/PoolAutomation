from typing import Callable
from IO.VariableRepo import VariableRepo
from lib.Variable import *
import DependencyContainer
import time
import datetime

logger = DependencyContainer.get_logger(__name__)

class Variables:
    def __init__(self, variables:"list[Variable|VariableGroup]", repo:VariableRepo) -> None:
        
        self._repo:VariableRepo = repo
        self._groups:"dict[str,VariableGroup]" = {}

        if(variables != None):            
            hasAny = self._repo.hasAny()
            for var in variables:
                self.addVariable(var)
                
            #if there was none in the repo, but there were variables, then save them.
            if(not hasAny):
                self.save()

    def getVariablesThatExpire(self, allowExpired = False):
        ready = []
        for key, variable in self._repo.get().items():
            if(variable.expires != None and variable.expires and ((not variable.hasExpired and not allowExpired) or allowExpired)):
                ready.append(variable)
        return ready

    def checkForExpiredVariables(self):
        """Checks against now to see if the variables are not exprired and should be expired. 
        Fires a notification when it does.
        """
        now = datetime.datetime.now()
        for item in self.getVariablesThatExpire():
            if(item.value != None and now > item.value):
                item.hasExpired = True
                #Notify anyone that it expired
                if(DependencyContainer.actions != None):
                    DependencyContainer.actions.nofityListners(VariableChangeEvent(None,item))
    
    def addVariable(self, variable:"Variable|VariableGroup") -> None:        
        self._repo.add(variable)
    
    def updateValue(self, name:str, value:any) -> None:
        variable = self._repo.get()[name]
        oldValue = variable.value        
        variable.value = value
        self._repo.save()

        if(DependencyContainer.actions != None):
            DependencyContainer.actions.nofityListners(VariableChangeEvent(None, variable))
            
    def get(self, name:str) -> Variable:
        if(name in self._repo.get()):
            return self._repo.get()[name]
        else:
            return None   
    
    def save(self):
        self._repo.save()

    def getVariablesForUi(self) -> "list[VariableGroup]":
        return self._repo.getGroups()
