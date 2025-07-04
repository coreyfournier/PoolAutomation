import tempfile
import os
import DependencyContainer
from Plugins.Slide import *
from IO.VariableRepo import *
from lib.Variable import *
from IO.GpioStub import *
from Configuration import *
from Devices.Pumps import *
from Devices.TemperatureSensors import *
from Tests.IO.TemperatureRepoStub import TemperatureRepoStub
from Tests.IO.VariableRepoStub import VariableRepoStub
from Tests.IO.ValveRepoStub import ValveRepoStub
from Tests.IO.PumpRepoStub import PumpRepoStub
from Tests.Devices.TemperatureStub import TemperatureStub

DependencyContainer.logServerName = "none"

def test_slideOn():
    """When the slide is turned on, the valve is on and the speed has changed
    """
    GPIO = GpioStub()
    
    DependencyContainer.variables = Variables(None, VariableRepoStub())

    #Given: #1 the pump is on
    mainPump = Pump(1,"main","", Speed.SPEED_4)
    slideValve = Valve("slide","",1, False, GpioController(GPIO, 1))
    #Given #2 the value is on
    slideValve.controller.on()
    roofTemp = TemperatureStub(1, "roof", "Roof","roof", 1)
    solarTemp = TemperatureStub(1, "solar-heat", "solar-heat","solar-heat", 2)
    poolTemp = TemperatureStub(1, "pool-temp", "pool-temp","pool-temp", 3)

    slidePlugin:IPlugin = Slide()

    variables = slidePlugin.getVariables()

    for var in variables:
        DependencyContainer.variables.addVariable(var)

    #Given: #4 Heater is current running
    DependencyContainer.variables.get("slide-on").value = True    
        
    DependencyContainer.temperatureUnit = 'f'

    DependencyContainer.valves = Valves(ValveRepoStub(
        [slideValve]
    ))
    DependencyContainer.pumps = Pumps(PumpRepoStub(
        [mainPump]
    ))    
    

    DependencyContainer.temperatureDevices = TemperatureSensors(TemperatureRepoStub(
        {"roof" : roofTemp,
        "solar-heat" : solarTemp,
        "pool-temp" : poolTemp}
    )) 
 

    slideAction = slidePlugin.getAction()
  
    
    #Then:
    #Solar heater value should now be on
    assert slideValve.isOn, "slide was not on as expected."

    #Pump should now be on.
    assert mainPump.currentSpeed != Speed.OFF, "Pump was not on as expected"