from typing import Callable
from IO.VariableRepo import VariableRepo
from lib.Variable import *
import DependencyContainer
import time
import datetime
from Events.VariableChangeEvent import VariableChangeEvent
from lib.Entity import Entity

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
            
            if(item.value != None):
                #datetime.datetime.strptime(item.value, "%Y-%m-%dT%H:%M:%S.%fZ")
                valueAsDateTime = datetime.datetime.strptime(item.value, "%Y-%m-%dT%H:%M:%S.%f")
                if(now > valueAsDateTime):
                    item.hasExpired = True
                    #Notify anyone that it expired
                    if(DependencyContainer.actions != None):
                        DependencyContainer.actions.nofityListners(VariableChangeEvent(None, False,None, item))
    
    def addVariable(self, variable:"Variable|VariableGroup") -> None:        
        self._repo.add(variable)
    
    def updateValue(self, name:str, value:any) -> None:
        variable = self._repo.get()[name]
        oldValue = variable.value        
        variable.value = value
        self._repo.save()

        if(DependencyContainer.actions != None):
            DependencyContainer.actions.nofityListners(VariableChangeEvent(None, False,None, variable))
            
    def get(self, name:str, default:any = None) -> Variable:
        if(name in self._repo.get()):            
            return self._repo.get()[name]
        elif(default != None):
            return Variable(name, "", None, default)
        else:
            return None   
    
    def save(self):
        self._repo.save()

    def getVariablesForUi(self) -> "list[VariableGroup]":
        return self._repo.getGroups()

    def getAll(self) -> "list[Variable]":
        """Gets every variable, including the ones hidden from the UI
        """
        return list(self._repo.get().values())

    def getGroups(self) -> "list[VariableGroup]":
        """Gets every group, including the ones hidden from the UI
        """
        return self._repo.getGroups(False)

    def getEntities(self) -> "list[Entity]":
        """Variables shown in the UI can be changed from outside the app. Hidden ones are state the plugins
        manage, so they are read only.
        """
        changeable:"set[str]" = set()
        for group in self.getVariablesForUi():
            changeable.update([x.name for x in group.variables])

        #Names like "Enabled" mean nothing without the group, so prefix them with the group title
        groupTitles:"dict[str,str]" = {}
        for group in self.getGroups():
            for variable in group.variables:
                groupTitles[variable.name] = group.title

        entities:"list[Entity]" = []
        for variable in self.getAll():
            displayName = variable.displayName
            if(variable.name in groupTitles):
                displayName = f"{groupTitles[variable.name]} {displayName}"

            setValue = None
            if(variable.name in changeable):
                setValue = lambda value, variable=variable: setattr(variable, "value", value)

            entities.append(Entity("variable", variable.name, displayName, variable.dataType,
                lambda variable=variable: variable.value,
                setValue))

        return entities
