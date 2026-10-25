from Plugins.IPlugin import IPlugin
import DependencyContainer
from Events.Event import Event
import json
import os
import re
import threading
import cherrypy
import paho.mqtt.client as mqtt

from lib.Actions import *
from lib.Variables import *
from lib.Entity import Entity

logger = DependencyContainer.get_logger(__name__)

ACTION_NAME = "home-assistant"
#Home Assistant device classes for the measurements it knows. Anything else is shown without one.
DEVICE_CLASSES:"dict[str,str]" = {
    "temperature": "temperature",
    "ph": "ph"
}

class HomeAssistant(IPlugin):
    """Pushes every change to an MQTT broker so Home Assistant does not have to poll.
    Uses Home Assistant MQTT discovery, so everything shows up on its own. Publishes whatever the devices,
    variables and plugins expose as entities (DependencyContainer.getEntities), so it doesn't need to know
    about any of them. Entities that can be changed can also be controlled from Home Assistant.

    Only runs when MQTT_HOST is set. Other settings (all optional):
        MQTT_PORT - defaults to 1883
        MQTT_USERNAME / MQTT_PASSWORD
        MQTT_TOPIC_PREFIX - defaults to pool-automation
        MQTT_DISCOVERY_PREFIX - defaults to homeassistant, which is what Home Assistant uses out of the box
    """
    def __init__(self) -> None:
        #An empty value (MQTT_HOST= in the .env file) means it's turned off
        self._host:str = os.environ.get("MQTT_HOST") or None
        self._port:int = int(os.environ.get("MQTT_PORT", "1883"))
        self._prefix:str = os.environ.get("MQTT_TOPIC_PREFIX", "pool-automation")
        self._discoveryPrefix:str = os.environ.get("MQTT_DISCOVERY_PREFIX", "homeassistant")
        self._client:mqtt.Client = None
        #Everything being published, found when discovery was last sent
        self._entities:"list[Entity]" = []
        #Maps a command topic to the entity it changes
        self._commands:"dict[str,Entity]" = {}
        #Last payload published to each state topic. Used to only publish what changed.
        self._published:"dict[str,str]" = {}
        #Events and (re)connects come in on different threads
        self._lock = threading.Lock()

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
            entity = self._commands[topic]
            entity.setValue(self._parse(entity, payload))
        except Exception as err:
            logger.exception(f"Failed running command {topic}={payload}. Error:{err}")

    def onChange(self, event:Event):
        if(self._client is None or not self._client.is_connected()):
            #Everything gets published when it connects
            return

        #No need to know what the event was about. Anything whose value changed gets published, which also
        #catches changes that don't raise an event. The timer event fires every few seconds as a backstop.
        self._publishChanges()

    #-------------------------------------------------------------------------
    # State
    #-------------------------------------------------------------------------

    def _publishAll(self):
        try:
            with self._lock:
                self._entities = [x for x in DependencyContainer.getEntities()
                    #Overriding the schedule isn't something this plugin does
                    if not (x.group == "override" and x.name == ACTION_NAME)]
                self._commands = {}
                self._published = {}

                for entity in self._entities:
                    self._discover(entity)

                self._client.publish(self._availabilityTopic(), "online", retain=True)
                self._publishChangesLocked()
        except Exception as err:
            logger.exception(f"Failed publishing to MQTT. Error:{err}")

    def _publishChanges(self):
        with self._lock:
            self._publishChangesLocked()

    def _publishChangesLocked(self):
        for entity in self._entities:
            try:
                value = entity.getValue()
            except Exception as err:
                logger.debug(f"Failed reading {entity.group}/{entity.name}. Error:{err}")
                continue

            #Unknown values are left alone. Home Assistant shows them as unknown until there is a value.
            if(value is None):
                continue

            topic = self._stateTopic(entity)
            payload = self._format(entity, value)
            if(self._published.get(topic) != payload):
                self._client.publish(topic, payload, retain=True)
                self._published[topic] = payload

    #-------------------------------------------------------------------------
    # Discovery
    #-------------------------------------------------------------------------

    def _component(self, entity:Entity) -> str:
        """Which Home Assistant entity type to show it as
        """
        if(entity.dataType is bool):
            return "binary_sensor" if entity.readOnly else "switch"
        if(entity.readOnly):
            return "sensor"
        if(entity.options != None):
            return "select"
        if(entity.dataType in (int, float)):
            return "number"
        #Free text that can be changed is shown read only. Nothing needs to change one from Home Assistant yet.
        return "sensor"

    def _discover(self, entity:Entity):
        """Publishes the Home Assistant discovery config for one entity
        """
        component = self._component(entity)
        uniqueId = f"{self._safe(self._prefix)}_{entity.group}_{self._safe(entity.name)}"
        payload = {
            "name": entity.displayName,
            "unique_id": uniqueId,
            "state_topic": self._stateTopic(entity),
            "availability_topic": self._availabilityTopic(),
            "device": {
                "identifiers": [self._safe(self._prefix)],
                "name": "Pool Automation",
                "manufacturer": "Pool Automation",
                #Shown as the firmware version on the device page
                "sw_version": DependencyContainer.appVersion
            }
        }

        if(component in ("switch", "select", "number")):
            commandTopic = self._commandTopic(entity)
            payload["command_topic"] = commandTopic
            self._commands[commandTopic] = entity

        if(component == "select"):
            payload["options"] = entity.options
        if(component == "number"):
            payload["min"] = entity.minValue if entity.minValue != None else -100000
            payload["max"] = entity.maxValue if entity.maxValue != None else 100000
            payload["step"] = entity.step if entity.step != None else (1 if entity.dataType is int else 0.1)
            payload["mode"] = "box"
        if(entity.unit != None):
            payload["unit_of_measurement"] = entity.unit
        if(entity.measurement != None and component == "sensor"):
            payload["state_class"] = "measurement"
            if(entity.measurement in DEVICE_CLASSES):
                payload["device_class"] = DEVICE_CLASSES[entity.measurement]
        if(entity.icon != None):
            payload["icon"] = entity.icon

        self._client.publish(f"{self._discoveryPrefix}/{component}/{uniqueId}/config", json.dumps(payload), retain=True)

    #-------------------------------------------------------------------------
    # Payloads
    #-------------------------------------------------------------------------

    @staticmethod
    def _format(entity:Entity, value:any) -> str:
        if(entity.dataType is bool):
            return "ON" if value else "OFF"
        return str(value)

    @staticmethod
    def _parse(entity:Entity, payload:str) -> any:
        if(entity.dataType is bool):
            return payload == "ON"
        if(entity.dataType is int):
            return int(float(payload))
        if(entity.dataType is float):
            return float(payload)
        return payload

    #-------------------------------------------------------------------------
    # Topics
    #-------------------------------------------------------------------------

    def _availabilityTopic(self) -> str:
        return f"{self._prefix}/status"

    def _stateTopic(self, entity:Entity) -> str:
        return f"{self._prefix}/{entity.group}/{self._safe(entity.name)}/state"

    def _commandTopic(self, entity:Entity) -> str:
        return f"{self._prefix}/{entity.group}/{self._safe(entity.name)}/set"

    @staticmethod
    def _safe(name:str) -> str:
        """MQTT wildcards and Home Assistant ids don't allow everything, so stick to the basics
        """
        return re.sub(r"[^a-zA-Z0-9_-]", "_", name)
