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
    """Heater is enabled, pool is cold, and roof is warm enough to allow the heater to turn on.
    """
    GPIO = GpioStub()
    
    DependencyContainer.variables = Variables(None, VariableRepoStub())

    #Given: #1 the pump is off
    mainPump = Pump(1,"main","", Speed.OFF)
    solarHeaterValve = Valve("solar","",1, False, GpioController(GPIO, 1))
    roofTemp = TemperatureStub(1, "roof", "Roof","roof", 1)
    solarTemp = TemperatureStub(1, "solar-heat", "solar-heat","solar-heat", 2)
    poolTemp = TemperatureStub(1, "pool-temp", "pool-temp","pool-temp", 3)

    sh = SolarHeater()

    for var in sh.getVariables():
        DependencyContainer.variables.addVariable(var)

    #Given: #2 Make sure the header is enabled
    DependencyContainer.variables.get("solar-heat-enabled").value = True
    #Given: #3 Target temp of the pool is higher than the current temp
    DependencyContainer.variables.get("solar-heat-temperature").value = 30

    DependencyContainer.valves = Valves(ValveRepoStub(
        [solarHeaterValve]
    ))
    DependencyContainer.pumps = Pumps(PumpRepoStub(
        [mainPump]
    ))    
    
       
    #When the roof is hot enough and the pool temp is 
    roofTemp.set(49) #120F
    solarTemp.set(0)
    #Current pool temp
    poolTemp.set(26) #80F

    DependencyContainer.temperatureDevices = TemperatureSensors(TemperatureRepoStub(
        {"roof" : roofTemp,
        "solar-heat" : solarTemp,
        "pool-temp" : poolTemp}
    )) 
 

    heaterAction = sh.getAction()

    sh.evaluateSolarStatus(
        TemperatureChangeEvent("", False, heaterAction, TemperatureBase(1,"roof","","",1))
                               )
    
    #Then:
    #Solar heater value should now be on
    assert solarHeaterValve.isOn, "Heater was not on as expected."

    #Pump should now be on.
    assert mainPump.currentSpeed != Speed.OFF, "Pump was not on as expected"


def test_turnOff():
    """Pool is now hot enough and the heater needs to be turned off.
    """
    GPIO = GpioStub()
    
    DependencyContainer.variables = Variables(None, VariableRepoStub())

    #Given: #1 the pump is off
    mainPump = Pump(1,"main","", Speed.SPEED_1)
    solarHeaterValve = Valve("solar","",1, False, GpioController(GPIO, 1))
    roofTemp = TemperatureStub(1, "roof", "Roof","roof", 1)
    solarTemp = TemperatureStub(1, "solar-heat", "solar-heat","solar-heat", 2)
    poolTemp = TemperatureStub(1, "pool-temp", "pool-temp","pool-temp", 3)

    sh = SolarHeater()

    for var in sh.getVariables():
        DependencyContainer.variables.addVariable(var)

    #Given: #2 Make sure the header is enabled
    DependencyContainer.variables.get("solar-heat-enabled").value = True
    #Given: #3 Target temp of the pool is at or greater than the current temp
    targetTemp = 35
    DependencyContainer.variables.get("solar-heat-temperature").value = targetTemp
    #Given: #4 the heater is actively running
    DependencyContainer.variables.get("solar-heat-on").value = True

    DependencyContainer.valves = Valves(ValveRepoStub(
        [solarHeaterValve]
    ))
    DependencyContainer.pumps = Pumps(PumpRepoStub(
        [mainPump]
    ))    
    
       
    #When the roof is hot enough and the pool temp is 
    roofTemp.set(49) #120F
    solarTemp.set(0)
    #Current pool temp
    poolTemp.set(targetTemp)

    DependencyContainer.temperatureDevices = TemperatureSensors(TemperatureRepoStub(
        {"roof" : roofTemp,
        "solar-heat" : solarTemp,
        "pool-temp" : poolTemp}
    )) 
 

    heaterAction = sh.getAction()

    sh.evaluateSolarStatus(
        TemperatureChangeEvent("", False, heaterAction, TemperatureBase(1,"roof","","",1))
                               )
    
    #Then:
    #Solar heater value should now be off
    assert not solarHeaterValve.isOn, "Heater was not off as expected."

    #Pump should now be off.
    assert mainPump.currentSpeed == Speed.OFF, "Pump was not off as expected"    