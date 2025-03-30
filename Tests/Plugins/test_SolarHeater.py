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
from Tests.Devices.TemperatureStub import TemperatureStub

DependencyContainer.logServerName = "none"

def test_turnOn():
    GPIO = GpioStub()
    dataPath = os.path.join(tempfile.gettempdir(), "unit_test")
        
    mainPump = Pump(1,"main","", Speed.OFF)
    solarHeaterValve = Valve("solar","",1, False, GpioController(GpioStub(), 1))
    roofTemp = TemperatureStub(1, "roof", "Roof","roof", 1)
    solarTemp = TemperatureStub(1, "solar-heat", "solar-heat","solar-heat", 2)
    poolTemp = TemperatureStub(1, "pool-temp", "pool-temp","pool-temp", 3)

    DependencyContainer.valves = Valves(ValveRepoStub(
        [solarHeaterValve]
    ))
    
    DependencyContainer.pumps = Pumps(PumpRepoStub(
        [mainPump]
    ))    
    
    DependencyContainer.variables = Variables(None, VariableRepoStub())
    
    roofTemp.set(49) #120F
    solarTemp.set(0)
    poolTemp.set(26) #80F

    DependencyContainer.temperatureDevices = TemperatureSensors(TemperatureRepoStub(
        {"roof" : roofTemp,
        "solar-heat" : solarTemp,
        "pool-temp" : poolTemp}
    )) 

    sh = SolarHeater()

    for var in sh.getVariables():
        DependencyContainer.variables.addVariable(var)

    #Make sure the header is enabled
    DependencyContainer.variables.get("solar-heat-enabled").value = True

    heaterAction = sh.getAction()

    sh.evaluateSolarStatus(
        TemperatureChangeEvent("", False, heaterAction, TemperatureBase(1,"roof","","",1))
                               )
    
    #Solar heater value should now be on
    assert solarHeaterValve.isOn, "Heater was not on as expected."

    #Pump should now be on.
    assert mainPump.currentSpeed != Speed.OFF, "Pump was not on as expected"