from lib.Variable import *


class IVariableRepo:
    def __init__(self):
        self._container:VariableContainer = VariableContainer(groups=[], variables=[])
        self._variables:"dict[str,Variable]" = {}
        self._uniqueGroups:"dict[str,VariableContainer]" = {}


    def add(self, variable:"Variable|VariableGroup") -> None:
        refresh = False        
        if(isinstance(variable, VariableGroup)):
            if(variable.title not in self._uniqueGroups):
                self._uniqueGroups[variable.title] = variable
                self._container.groups.append(variable)
                refresh = True        
        else:
            #the name already exists, don't add a duplicate
            if(variable.name in self._variables):    
                self._variables[variable.name] = variable
                existing = [i for i, x in enumerate(self._container.variables) if x.name == variable.name]
                if(len(existing) > 0):
                    self._container.variables[existing[0]] = variable

                refresh = True
            else:
                self._container.variables.append(variable)
                refresh = True

        
        if(refresh):
            self._variables = self._container.getAll()

    def hasAny(self) -> bool:
        return len(self._container.groups) > 0 or len(self._container.variables) > 0

    def get(self) -> "VariableContainer":
        return self._variables

    def getGroups(self, forUI:bool = True) -> "list[VariableGroup]":
        if(forUI):
            return [IVariableRepo.filterNonUiVariables(x) for x in list(filter(lambda x: x.showInUi, self._container.groups))]
        else:
            return [x for x in self._container.groups]
        
    @staticmethod
    def filterNonUiVariables(group: VariableGroup)-> VariableGroup:
        group.variables = [x for x in list(filter(lambda x: x.showInUi, group.variables))]
        return group
    
    
    def save(self):
        #Implemented in child class
        pass

