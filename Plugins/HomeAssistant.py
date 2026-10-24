from Plugins.IPlugin import IPlugin
import DependencyContainer
from Events.Event import Event
import json
import os
import re
import threading
from typing import Callable
import cherrypy
import paho.mqtt.client as mqtt

from lib.Actions import *
from lib.Variables import *
from Devices.Pump import *
from Devices.Light import Light
from Devices.Valve import Valve
from Devices.TemperatureBase import *
from Devices.PoolChemistry import PoolChemistry
from Events.PumpChangeEvent import PumpChangeEvent
from Events.ValveChangeEvent import ValveChangeEvent
from Events.LightChangeEvent import LightChangeEvent
from Events.VariableChangeEvent import VariableChangeEvent
from Events.OverrideChangeEvent import OverrideChangeEvent
from Events.ScheduleChangeEvent import ScheduleChangeEvent
from Events.OrpChangeEvent import OrpChangeEvent
from Events.PhChangeEvent import PhChangeEvent

logger = DependencyContainer.get_logger(__name__)

#Value published for the light when no scene is on.
LIGHT_OFF = "OFF"
ACTION_NAME = "home-assistant"

class HomeAssistant(IPlugin):
    """Pushes every change to an MQTT broker so Home Assistant does not have to poll.
    Uses Home Assistant MQTT discovery, so the devices show up on their own. Pumps, valves, lights and the
    variables shown in the UI can also be controlled from Home Assistant.

    Only runs when MQTT_HOST is set. Other settings (all optional):
        MQTT_PORT - defaults to 1883
        MQTT_USERNAME / MQTT_PASSWORD
        MQTT_TOPIC_PREFIX - defaults to pool-automation
        MQTT_DISCOVERY_PREFIX - defaults to homeassistant, which is what Home Assistant uses out of the box
    """
    def __init__(self) -> None:
        self._host:str = os.environ.get("MQTT_HOST")
        self._port:int = int(os.environ.get("MQTT_PORT", "1883"))
        self._prefix:str = os.environ.get("MQTT_TOPIC_PREFIX", "pool-automation")
        self._discoveryPrefix:str = os.environ.get("MQTT_DISCOVERY_PREFIX", "homeassistant")
        self._client:mqtt.Client = None
        #Maps a command topic to the function that handles the payload
        self._commands:"dict[str,Callable]" = {}

    def getAction(self)-> Action:
        if(self._host is None):
            return None
        return Action(ACTION_NAME, "Home Assistant", self.onChange)

    def getVariables(self) -> "list[Variable|VariableGroup]":
        pass

    def startup(self, GPIO:any, i2cBus:any) -> None:
        if(self._host is None):
            logger.info("MQTT_HOST not set. Home Assistant MQTT is disabled.")
            return

        self._client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=self._prefix)
        if("MQTT_USERNAME" in os.environ):
            self._client.username_pw_set(os.environ["MQTT_USERNAME"], os.environ.get("MQTT_PASSWORD"))
        #Home Assistant marks everything unavailable when the connection drops
        self._client.will_set(self._availabilityTopic(), "offline", retain=True)
        self._client.on_connect = self._onConnect
        self._client.on_message = self._onMessage

        #Wait for the engine to start, so every plugin has registered its variables before discovery is published
        cherrypy.engine.subscribe("start", self._connect)
        cherrypy.engine.subscribe("stop", self._disconnect)

    def _connect(self):
        logger.info(f"Connecting to MQTT broker {self._host}:{self._port}")
        #connect_async keeps retrying in the background, so a missing broker never stops the pool from running
        self._client.connect_async(self._host, self._port)
        self._client.loop_start()

    def _disconnect(self):
        if(self._client.is_connected()):
            self._client.publish(self._availabilityTopic(), "offline", retain=True).wait_for_publish(3)
        self._client.disconnect()
        self._client.loop_stop()

    def _onConnect(self, client, userdata, flags, reasonCode, properties):
        if(reasonCode.is_failure):
            logger.error(f"MQTT connection refused: {reasonCode}")
            return

        logger.info("Connected to MQTT broker")
        client.subscribe(f"{self._prefix}/+/+/set")
        #Home Assistant announces itself when it restarts. Discovery needs to be sent again when that happens.
        client.subscribe(f"{self._discoveryPrefix}/status")
        #Reading the devices can be slow (the chemistry sensor is a web call), so don't hold up the network thread
        threading.Thread(target=self._publishAll, daemon=True).start()

    def _onMessage(self, client, userdata, message:mqtt.MQTTMessage):
        payload = message.payload.decode()

        if(message.topic == f"{self._discoveryPrefix}/status"):
            if(payload == "online"):
                threading.Thread(target=self._publishAll, daemon=True).start()
        elif(message.topic in self._commands):
            logger.debug(f"Command {message.topic}={payload}")
            #Light scenes take several seconds to cycle, so run commands off the network thread
            threading.Thread(target=self._runCommand, args=(message.topic, payload), daemon=True).start()
        else:
            logger.warning(f"No command registered for {message.topic}")

    def _runCommand(self, topic:str, payload:str):
        try:
            self._commands[topic](payload)
        except Exception as err:
            logger.exception(f"Failed running command {topic}={payload}. Error:{err}")

    def onChange(self, event:Event):
        if(self._client is None or not self._client.is_connected()):
            #Everything gets published when it connects
            return

        if(isinstance(event, PumpChangeEvent)):
            self._publishPump(event.data)
        elif(isinstance(event, ValveChangeEvent)):
            self._publishValve(event.data)
        elif(isinstance(event, LightChangeEvent)):
            self._publishLight(event.data)
        elif(isinstance(event, TemperatureChangeEvent)):
            self._publishTemperature(event.data)
        elif(isinstance(event, (OrpChangeEvent, PhChangeEvent))):
            self._publishChemistry(event.data)
        elif(isinstance(event, VariableChangeEvent)):
            self._publishVariable(event.data)
        elif(isinstance(event, OverrideChangeEvent)):
            self._publishOverride(event.data)
        elif(isinstance(event, ScheduleChangeEvent)):
            self._publishSchedule()

    def _publishAll(self):
        try:
            self._publishDiscovery()
            self._client.publish(self._availabilityTopic(), "online", retain=True)

            for pump in DependencyContainer.pumps.getAll():
                self._publishPump(pump)
            for valve in DependencyContainer.valves.getAll():
                self._publishValve(valve)
            for light in DependencyContainer.lights.getAll():
                self._publishLight(light)
            for device in DependencyContainer.temperatureDevices.getAll():
                self._publishTemperature(device)
            for variable in DependencyContainer.variables.getAll():
                self._publishVariable(variable)
            for action in DependencyContainer.actions.get():
                if(action.name != ACTION_NAME):
                    self._publishOverride(action)
            self._publishSchedule()

            if(DependencyContainer.enviromentalSensor != None):
                self._publishChemistry(DependencyContainer.enviromentalSensor.get())
        except Exception as err:
            logger.exception(f"Failed publishing to MQTT. Error:{err}")

    #-------------------------------------------------------------------------
    # State
    #-------------------------------------------------------------------------

    def _publishPump(self, pump:Pump):
        self._publishState("pump", pump.name, pump.currentSpeed.name)

    def _publishValve(self, valve:Valve):
        self._publishState("valve", valve.name, "ON" if valve.isOn else "OFF")

    def _publishLight(self, light:Light):
        self._publishState("light", light.name, light.currentScene or LIGHT_OFF)

    def _publishTemperature(self, device:TemperatureBase):
        temp = device.getLastAsLocal()
        if(temp != None):
            self._publishState("temperature", device.name, temp)

    def _publishChemistry(self, chemistry:PoolChemistry):
        if(chemistry != None):
            self._publishState("chemistry", "sensor", json.dumps(chemistry.to_dict()))

    def _publishVariable(self, variable:Variable):
        value = variable.value
        if(variable.dataType is bool):
            value = "ON" if value else "OFF"
        elif(value is None):
            value = ""
        self._publishState("variable", variable.name, value)

    def _publishOverride(self, action:Action):
        self._publishState("override", action.name, "ON" if action.overrideSchedule else "OFF")

    def _publishSchedule(self):
        if(DependencyContainer.schedules == None):
            return
        running = DependencyContainer.schedules.getRunning()
        self._publishState("schedule", "running", ", ".join([x.name for x in running]) if len(running) > 0 else "None")

    def _publishState(self, kind:str, name:str, value:any):
        self._client.publish(self._stateTopic(kind, name), str(value), retain=True)

    #-------------------------------------------------------------------------
    # Discovery
    #-------------------------------------------------------------------------

    def _publishDiscovery(self):
        self._commands = {}

        for pump in DependencyContainer.pumps.getAll():
            speeds = pump.speeds()
            options = [x.name for x in speeds] if speeds != None else [x.name for x in Speed]
            self._discover("select", "pump", pump.name, pump.displayName, {
                "options": options,
                "icon": "mdi:pump"
            }, lambda payload, pump=pump: self._setPumpSpeed(pump, payload))

        for valve in DependencyContainer.valves.getAll():
            self._discover("switch", "valve", valve.name, valve.displayName, {
                "icon": "mdi:valve"
            }, lambda payload, valve=valve: self._setValve(valve, payload))

        for light in DependencyContainer.lights.getAll():
            self._discover("select", "light", light.name, light.displayName, {
                "options": [LIGHT_OFF] + [x.name for x in light.lightScenes()],
                "icon": "mdi:lightbulb"
            }, lambda payload, light=light: self._setLight(light, payload))

        for device in DependencyContainer.temperatureDevices.getAll():
            self._discover("sensor", "temperature", device.name, device.displayName, {
                "device_class": "temperature",
                "state_class": "measurement",
                "unit_of_measurement": f"°{DependencyContainer.temperatureUnit.upper()}"
            })

        if(DependencyContainer.enviromentalSensor != None):
            self._discover("sensor", "chemistry", "ph", "pH", {
                "state_topic": self._stateTopic("chemistry", "sensor"),
                "value_template": "{{ value_json.ph }}",
                "device_class": "ph",
                "state_class": "measurement"
            })
            self._discover("sensor", "chemistry", "orp", "ORP", {
                "state_topic": self._stateTopic("chemistry", "sensor"),
                "value_template": "{{ value_json.orp }}",
                "unit_of_measurement": "mV",
                "state_class": "measurement",
                "icon": "mdi:flask"
            })
            self._discover("sensor", "chemistry", "temperature", "Chemistry Temperature", {
                "state_topic": self._stateTopic("chemistry", "sensor"),
                "value_template": "{{ value_json.temperature }}",
                "device_class": "temperature",
                "state_class": "measurement",
                "unit_of_measurement": f"°{DependencyContainer.temperatureUnit.upper()}"
            })

        for action in DependencyContainer.actions.get():
            if(action.name == ACTION_NAME):
                continue
            self._discover("binary_sensor", "override", action.name, f"{action.displayName} Override", {
                "icon": "mdi:calendar-remove"
            })

        self._discover("sensor", "schedule", "running", "Running Schedule", {
            "icon": "mdi:calendar-clock"
        })

        self._discoverVariables()

    def _discoverVariables(self):
        #Variables shown in the UI can be changed from Home Assistant. Hidden ones are internal state the plugins
        #manage, so they are read only.
        controllable:"set[str]" = set()
        for group in DependencyContainer.variables.getVariablesForUi():
            controllable.update([x.name for x in group.variables])

        #Names like "Enabled" mean nothing without the group, so prefix them with the group title
        groupTitles:"dict[str,str]" = {}
        for group in DependencyContainer.variables.getGroups():
            for variable in group.variables:
                groupTitles[variable.name] = group.title

        for variable in DependencyContainer.variables.getAll():
            displayName = variable.displayName
            if(variable.name in groupTitles):
                displayName = f"{groupTitles[variable.name]} {displayName}"

            isControllable = variable.name in controllable

            if(variable.dataType is bool):
                component = "switch" if isControllable else "binary_sensor"
                config = {}
            elif(variable.dataType in (int, float) and isControllable):
                component = "number"
                config = {
                    "min": -100000,
                    "max": 100000,
                    "step": 1 if variable.dataType is int else 0.1,
                    "mode": "box"
                }
            else:
                component = "sensor"
                config = {}

            command = (lambda payload, variable=variable: self._setVariable(variable, payload)) if isControllable else None
            self._discover(component, "variable", variable.name, displayName, config, command)

    def _discover(self, component:str, kind:str, name:str, displayName:str, config:dict, command:Callable = None):
        """Publishes the Home Assistant discovery config for one entity

        Args:
            component (str): Home Assistant entity type (sensor, switch, select ...)
            kind (str): Type of device in this app. Used to build the topics.
            name (str): api name of the device
            displayName (str): What Home Assistant shows
            config (dict): Extra config for the entity. Overrides the defaults.
            command (Callable, optional): Called with the payload when Home Assistant sends a command.
        """
        uniqueId = f"{self._safe(self._prefix)}_{kind}_{self._safe(name)}"
        payload = {
            "name": displayName,
            "unique_id": uniqueId,
            "state_topic": self._stateTopic(kind, name),
            "availability_topic": self._availabilityTopic(),
            "device": {
                "identifiers": [self._safe(self._prefix)],
                "name": "Pool Automation",
                "manufacturer": "Pool Automation"
            }
        }

        if(command != None):
            commandTopic = self._commandTopic(kind, name)
            payload["command_topic"] = commandTopic
            self._commands[commandTopic] = command

        payload.update(config)

        self._client.publish(f"{self._discoveryPrefix}/{component}/{uniqueId}/config", json.dumps(payload), retain=True)

    #-------------------------------------------------------------------------
    # Commands
    #-------------------------------------------------------------------------

    def _setPumpSpeed(self, pump:Pump, payload:str):
        if(Speed[payload] == Speed.OFF):
            pump.off()
        else:
            pump.on(Speed[payload])

    def _setValve(self, valve:Valve, payload:str):
        if(payload == "ON"):
            DependencyContainer.valves.on(valve.name)
        else:
            DependencyContainer.valves.off(valve.name)

    def _setLight(self, light:Light, payload:str):
        if(payload == LIGHT_OFF):
            light.off()
        else:
            sceneIndex = [x.name for x in light.lightScenes()].index(payload)
            light.change(sceneIndex)

    def _setVariable(self, variable:Variable, payload:str):
        if(variable.dataType is bool):
            variable.value = payload == "ON"
        elif(variable.dataType is int):
            variable.value = int(float(payload))
        elif(variable.dataType is float):
            variable.value = float(payload)
        else:
            variable.value = payload

    #-------------------------------------------------------------------------
    # Topics
    #-------------------------------------------------------------------------

    def _availabilityTopic(self) -> str:
        return f"{self._prefix}/status"

    def _stateTopic(self, kind:str, name:str) -> str:
        return f"{self._prefix}/{kind}/{self._safe(name)}/state"

    def _commandTopic(self, kind:str, name:str) -> str:
        return f"{self._prefix}/{kind}/{self._safe(name)}/set"

    @staticmethod
    def _safe(name:str) -> str:
        """MQTT wildcards and Home Assistant ids don't allow everything, so stick to the basics
        """
        return re.sub(r"[^a-zA-Z0-9_-]", "_", name)
