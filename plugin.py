#https://www.domoticz.com/wiki/Developing_a_Python_plugin
"""
<plugin key="RelayPump" name="Relay Pump" author="corey.fournier" version="1.0.0" wikilink="http://www.domoticz.com/" externallink="">
    <description>
        <h2>Relay Pump Plugin</h2><br/>
        <h3>Features</h3>
        <ul style="list-style-type:square">
            <li>Comes with three selectable icon sets: Default, Black and Round</li>
            <li>Display Domoticz notifications on Kodi screen if a Notifier name is specified and events configured for that notifier</li>
            <li>Multiple Shutdown action options</li>
            <li>When network connectivity is lost the Domoticz UI will optionally show the device(s) with a Red banner</li>
        </ul>
        <h3>Devices</h3>
        <ul style="list-style-type:square">
            <li>Status - Basic status indicator, On/Off. Also has icon for Kodi Remote popup</li>
            <li>Volume - Icon mutes/unmutes, slider shows/sets volume</li>
            <li>Source - Selector switch for content source: Video, Music, TV Shows, Live TV, Photos, Weather</li>
            <li>Playing - Icon Pauses/Resumes, slider shows/sets percentage through media</li>
        </ul>
    </description>
    <params>
        <param field="Mode1" label="Pump Pins" width="150px" required="true"/>
        <param field="Mode2" label="Shutdown Command" width="100px">
            <options>
                <option label="Hibernate" value="Hibernate"/>
                <option label="Suspend" value="Suspend"/>
                <option label="Shutdown" value="Shutdown"/>
                <option label="Ignore" value="Ignore" default="true" />
            </options>
        </param>
        <param field="Mode3" label="Notifications" width="75px">
            <options>
                <option label="True" value="True"/>
                <option label="False" value="False"  default="true" />
            </options>
        </param>
        <param field="Mode6" label="Debug" width="75px">
            <description><h2>Debugging</h2>Select the desired level of debug messaging</description>
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal"  default="true" />
            </options>
        </param>
    </params>
</plugin>
"""


import DomoticzEx as Domoticz
import json
from Pumps.Pump import Speed

class BasePlugin:
    enabled = False
    PumpIndex = 1

    def __init__(self):
        
        #self.var = 123
        self.speeds:"list[Speed]" = [Speed.OFF,Speed.SPEED_1,Speed.SPEED_2,Speed.SPEED_3,Speed.SPEED_4]
        #get the name in the list
        levelActions:str = "|".join([x.name for x in self.speeds])
        self.SourceOptions = {
            #add a pip for how many items are in the list
            'LevelActions': '|'*len(self.speeds),
            'LevelNames': levelActions,
            'LevelOffHidden': 'false',
            'SelectorStyle': '1'}

    def onStart(self):
        Domoticz.Log("*********onStart called - " + str(type(Devices)) + "***********************")

        Domoticz.Log(f"Total Devices {len(Devices)}")

        for k,v in Devices.items():
            Domoticz.Log(f"k={k} v={v}")

        Domoticz.Log(json.dumps(self.SourceOptions))
        
        if (len(Devices) == 0):            
            #Domoticz.Log("Adding Power")
            #Domoticz.Device(Name="Power", Unit=1, TypeName="Switch",  Image=5).Create()
            Domoticz.Log("Adding Pump")
            device = Domoticz.Device(
                Name="Pump Relay", 
                Unit=BasePlugin.PumpIndex, 
                TypeName="Selector Switch", 
                #18 = Selector
                Switchtype = 18, 
                Image = 5, 
                Options=self.SourceOptions
                )
            Domoticz.Log("Creating Pump")
            device.Create()
            #Domoticz.Device(Name="Main Volume", Unit=3, Type=244, Subtype=73, Switchtype=7, Image=8).Create()

    def onStop(self):
        Domoticz.Log("onStop called")

    def onConnect(self, Connection, Status, Description):
        Domoticz.Log("onConnect called")

    def onMessage(self, Connection, Data):
        Domoticz.Log(f"onMessage called Data={Data}")

    def onCommand(self, DeviceId, Unit, Command, Level, Color):
        Domoticz.Log("onCommand")
        Domoticz.Log(f"onCommand called for Device:{DeviceId} Unit:{Unit} Command:'{Command}' Level:{Level} Color:{Color}")
        #Domoticz.Log("onCommand called for '" + str(self.Name)+ "': Parameters '" + str(Command) + "', Level: " + str(Level))

        if(Unit == BasePlugin.PumpIndex):
            if(Level == 0):
                Domoticz.Log(f"Switching to: {self.speeds[0]}")
            else:#For some reason the numbers have a zero after it
                Domoticz.Log(f"Switching to: {self.speeds[int(Level/10)]}")

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Log("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Log("onDisconnect called")

    def onHeartbeat(self):
        Domoticz.Log("onHeartbeat called")

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(DeviceID, Unit, Command, Level, Color):
    global _plugin
    _plugin.onCommand(DeviceID, Unit, Command, Level, Color)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

# Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for DeviceName in Devices:
        Device = Devices[DeviceName]
        Domoticz.Debug("Device ID:       '" + str(Device.DeviceID) + "'")
        Domoticz.Debug("--->Unit Count:      '" + str(len(Device.Units)) + "'")
        for UnitNo in Device.Units:
            Unit = Device.Units[UnitNo]
            Domoticz.Debug("--->Unit:           " + str(UnitNo))
            Domoticz.Debug("--->Unit Name:     '" + Unit.Name + "'")
            Domoticz.Debug("--->Unit nValue:    " + str(Unit.nValue))
            Domoticz.Debug("--->Unit sValue:   '" + Unit.sValue + "'")
            Domoticz.Debug("--->Unit LastLevel: " + str(Unit.LastLevel))
    return