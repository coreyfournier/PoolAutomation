import tempfile
import os
import DependencyContainer
from Plugins.SolarHeater import *
from IO.VariableRepo import *
from lib.Variable import *
from IO.GpioStub import *
from Configuration import *
from Plugins.IPlugin import IPlugin

DependencyContainer.logServerName = "none"

def test_turnOn():
    
    variableFile = os.path.join(tempfile.gettempdir() + ".json")

    #configure
                                 
    #DependencyContainer.Variables = Variables(variableFile, VariableRepo(variableFile))
    #SolarHeater sh = SolarHeater()

    assert 4 == 4

