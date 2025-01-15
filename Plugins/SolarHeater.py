from IPlugin import IPlugin
import DependencyContainer
from lib.Event import Event

from Devices.Temperature import *
from lib.Actions import *
from lib.Variables import *
from Devices.Pump import *
from Devices.DeviceController import DeviceController

logger = DependencyContainer.get_logger(__name__)

class SolarHeater(IPlugin):
    """Controls the solar heater

    Args:
        IPlugin (_type_): _description_
    """
    def __init__(self) -> None:
        pass

    def getAction(self)-> Action:
        return Action("solar-heat", "Solar Heater",
            self.evaluateSolarStatus,
            DependencyContainer.variables.get("solar-heat-on", False).value
        )
    
    def startup(self, GPIO:any, i2cBus:any) -> None:
        pass
    
    def getVariables(self) -> "list[Variable|VariableGroup]":
        return [
            Variable("solar-heat-on",None, bool, value=False),
            VariableGroup("Solar Heater", [                
                    Variable("solar-heat-temperature","Heater temp", float,value=90.0),                                    
                    #The roof must be this temp + current pool temp before the heater turns on.
                    Variable("solar-min-roof-diff","Minimum roof diff", float, value=5),
                    Variable("solar-heat-enabled","Enabled", bool, value=False)
                ], 
                True, 
                "solar-heat-on", 
                1)]


    def evaluateSolarStatus(self, event: Event):
        action = event.action
        shouldCheck = \
            (isinstance(event, TemperatureChangeEvent) and event.data.name in ["roof","solar-heat", "pool-temp"]) or  \
            (isinstance(event, VariableChangeEvent) and event.data.name in ["solar-min-roof-diff", "solar-heat-temperature", "solar-heat-enabled"])
        
        if(shouldCheck):
            solarSetTemp = DependencyContainer.variables.get("solar-heat-temperature").value
            minRoofDifference = DependencyContainer.variables.get("solar-min-roof-diff").value
            isSolarEnabled = DependencyContainer.variables.get("solar-heat-enabled").value
            solarHeatTemp = DependencyContainer.temperatureDevices.get("solar-heat").get(True)
            roofTemp = DependencyContainer.temperatureDevices.get("roof").get(True)
            poolTemp = DependencyContainer.temperatureDevices.get("pool-temp").get(True)
            isSolarHeatOn = DependencyContainer.variables.get("solar-heat-on", False).value

            solarShouldBeOn = False
            pumpForSolar:Pump = DependencyContainer.pumps.get("main")
            solarVsPoolDifference = solarHeatTemp - poolTemp

            #if not enabled, then do nothing
            if(isSolarEnabled):            
                #Roof must greater than this
                needRoofTemp = poolTemp + minRoofDifference

                logger.debug(f"solarVsPoolDifference={solarVsPoolDifference} needRoofTemp={needRoofTemp} solarSetTemp={solarSetTemp} roofTemp={roofTemp} poolTemp={poolTemp} isSolarHeatOn={isSolarHeatOn}")

                if(isSolarHeatOn):
                    #need to check if it should stay on
                    if(poolTemp >= solarSetTemp):
                        solarShouldBeOn = False                   
                        logger.debug(f"Pool {poolTemp} > {solarSetTemp} turning off")                

                    elif(solarVsPoolDifference > 0):
                        #change the speed based on the temp of the output
                        if(solarVsPoolDifference > 4 and pumpForSolar.currentSpeed == Speed.SPEED_3):
                            logger.debug(f"It's hot enough, increasing the speed 2. Diff={solarVsPoolDifference}")
                            pumpForSolar.on(Speed.SPEED_2)
                        elif(solarVsPoolDifference > 2 and pumpForSolar.currentSpeed == Speed.SPEED_4):
                            logger.debug(f"It's hot enough, increasing the speed to 3. Diff={solarVsPoolDifference}")
                            pumpForSolar.on(Speed.SPEED_3)                        
                        solarShouldBeOn = True

                    #If not producing heat, but the roof is still hot see if we can change the pump speed
                    elif(solarVsPoolDifference <= 0 and roofTemp >= needRoofTemp and pumpForSolar.currentSpeed != Speed.SPEED_4):
                        logger.debug(f"It's NOT hot enough, decreasing the speed to 4. Diff={solarVsPoolDifference}")
                        pumpForSolar.on(Speed.SPEED_4)
                        solarShouldBeOn = True                                  
                    else:
                        logger.debug(f"It's NOT hot enough, going to turn off Diff={solarVsPoolDifference}")
                        solarShouldBeOn = False
                #See if it should be turned on
                elif(roofTemp > needRoofTemp and poolTemp <= solarSetTemp):
                        logger.debug(f"Heater staying on. Pool still not warm enough {poolTemp} < {solarSetTemp}. Roof:{roofTemp} Roof temp until off:{poolTemp-needRoofTemp}")
                        solarShouldBeOn = True                        
                else: 
                    if(isSolarHeatOn):
                        solarShouldBeOn = False                   
                        logger.debug(f"Pool {poolTemp} > {solarSetTemp} turning off")                    

            #If not enabled, but on, turn it off
            elif(isSolarHeatOn):
                solarShouldBeOn = False            
                logger.debug("Solar is disabled")

            if(isSolarHeatOn and not solarShouldBeOn):
                logger.info("Turning solar OFF")
                #Turn it off, it should not be on
                action.overrideSchedule = False
                DependencyContainer.variables.get("solar-heat-on").value = False
                DependencyContainer.valves.off("solar")
                SolarHeater.turnOffPumpIfNoActiveSchedule(pumpForSolar)
            elif(not isSolarHeatOn and solarShouldBeOn):
                logger.info("Turning solar ON")
                #It's not on and it should be
                action.overrideSchedule = True
                DependencyContainer.variables.get("solar-heat-on").value = True
                pumpForSolar.on(Speed.SPEED_2)
                DependencyContainer.valves.on("solar")

    @staticmethod
    def turnOffPumpIfNoActiveSchedule(pump:DeviceController):
        """This expects overrideSchedule to be set to False for the action.
        This would fire an event for the Schedule to resume. If none resumed, then none will be running.
        When no schedules are running, then the pump will turn off
        Args:
            pump (DeviceController): _description_
        """
        if(DependencyContainer.schedules != None):
            activeSchedules = DependencyContainer.schedules.getRunning()
            #If no schedules are running, then turn the pump off
            if(len(activeSchedules) == 0):                
                hasOverride = DependencyContainer.actions.hasOverrides()      
                if(not hasOverride):
                    logger.info(f"Turning pump off as there are no running schedules or schedule overrides")                      
                    pump.off()