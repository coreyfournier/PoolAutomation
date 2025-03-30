import tempfile
import os
import DependencyContainer
from Plugins.SolarHeater import *
from IO.VariableRepo import *
from lib.Variable import *
from IO.GpioStub import *
from Configuration import *
from Plugins.IPlugin import IPlugin
from Devices.Pumps import *
from Devices.TemperatureSensors import *
from Tests.IO.TemperatureRepoStub import TemperatureRepoStub
from Tests.IO.VariableRepoStub import VariableRepoStub
from Tests.IO.ValveRepoStub import ValveRepoStub
from Tests.IO.PumpRepoStub import PumpRepoStub

DependencyContainer.logServerName = "none"

def test_turnOn():
    GPIO = GpioStub()
    dataPath = os.path.join(tempfile.gettempdir(), "unit_test")
        
    DependencyContainer.valves = Valves(ValveRepoStub(
        [Valve("solar","",1, False, GpioController(GpioStub(), 1))]
    ))
    
    DependencyContainer.pumps = Pumps(PumpRepoStub(
        [Pump(1,"main","", Speed.OFF)]
    ))    
    
    DependencyContainer.variables = Variables(None, VariableRepoStub())

    DependencyContainer.temperatureDevices = TemperatureSensors(TemperatureRepoStub(
        {"roof" : Temperature(1, "roof", "Roof","roof", 1)}
    )) 

    sh = SolarHeater()

    for var in sh.getVariables():
        DependencyContainer.variables.addVariable(var)

    assert 4 == 4


