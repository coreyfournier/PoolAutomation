import json
import pytest
import DependencyContainer
from Plugins.HomeAssistant import *
from IO.GpioStub import *
from IO.GpioController import GpioController
from Devices.Pumps import *
from Devices.RelayPump import RelayPump
from Devices.Valves import *
from Devices.Lights import Lights
from Devices.GloBrite import GloBrite
from Devices.TemperatureSensors import *
from Tests.IO.VariableRepoStub import VariableRepoStub
from Tests.IO.ValveRepoStub import ValveRepoStub
from Tests.IO.PumpRepoStub import PumpRepoStub
from Tests.IO.TemperatureRepoStub import TemperatureRepoStub
from Tests.Devices.TemperatureStub import TemperatureStub

DependencyContainer.logServerName = "none"

class MqttClientStub:
    """Records what would have been sent to the broker
    """
    def __init__(self) -> None:
        self.published:"dict[str,str]" = {}

    def publish(self, topic:str, payload:str, retain:bool = False):
        self.published[topic] = payload

    def is_connected(self) -> bool:
        return True

@pytest.fixture
def plugin(monkeypatch):
    monkeypatch.setenv("MQTT_HOST", "localhost")
    GPIO = GpioStub()

    homeAssistant = HomeAssistant()
    homeAssistant._client = MqttClientStub()

    DependencyContainer.temperatureUnit = 'f'
    DependencyContainer.variables = Variables(None, VariableRepoStub())
    DependencyContainer.variables.addVariable(
        VariableGroup("Freeze Prevention", [
                Variable("freeze-prevention-enabled", "Enabled", bool, value=False),
                Variable("freeze-prevention-temperature", "Min Temp", float, value=35.0)
            ],
            True,
            "freeze-prevention-on"))
    DependencyContainer.actions = Actions([homeAssistant.getAction()])
    DependencyContainer.pumps = Pumps(PumpRepoStub([
        RelayPump(1, "main", "Main", {
            Speed.SPEED_1: GpioController(GPIO, 17),
            Speed.SPEED_2: GpioController(GPIO, 27)
        })
    ]))
    DependencyContainer.valves = Valves(ValveRepoStub([Valve("solar", "Solar", 1, False, GpioController(GPIO, 19))]))
    DependencyContainer.lights = Lights([GloBrite("main", "Light", GpioController(GPIO, 6), 0)])
    poolTemp = TemperatureStub(4, "pool-temp", "Pool", "Pool", 4)
    poolTemp.set(25)
    DependencyContainer.temperatureDevices = TemperatureSensors(TemperatureRepoStub({"pool-temp": poolTemp}))
    DependencyContainer.schedules = None
    DependencyContainer.enviromentalSensor = None

    yield homeAssistant

    DependencyContainer.actions = None

def test_disabledWithoutHost(monkeypatch):
    """Nothing is registered when no broker is configured
    """
    monkeypatch.delenv("MQTT_HOST", raising=False)
    assert HomeAssistant().getAction() is None

def test_publishAllSendsDiscoveryAndState(plugin:HomeAssistant):
    plugin._publishAll()
    published = plugin._client.published

    pumpConfig = json.loads(published["homeassistant/select/pool-automation_pump_main/config"])
    assert pumpConfig["options"] == ["OFF", "SPEED_1", "SPEED_2"]
    assert pumpConfig["command_topic"] == "pool-automation/pump/main/set"
    assert published["pool-automation/pump/main/state"] == "OFF"

    assert "homeassistant/switch/pool-automation_valve_solar/config" in published
    assert published["pool-automation/valve/solar/state"] == "OFF"

    lightConfig = json.loads(published["homeassistant/select/pool-automation_light_main/config"])
    assert lightConfig["options"][0] == LIGHT_OFF
    assert published["pool-automation/light/main/state"] == LIGHT_OFF

    assert published["pool-automation/temperature/pool-temp/state"] == "77.0"

    #UI variables can be controlled, hidden ones are read only
    enabledConfig = json.loads(published["homeassistant/switch/pool-automation_variable_freeze-prevention-enabled/config"])
    assert enabledConfig["name"] == "Freeze Prevention Enabled"
    assert "homeassistant/number/pool-automation_variable_freeze-prevention-temperature/config" in published
    assert "homeassistant/binary_sensor/pool-automation_variable_freeze-prevention-on/config" in published
    assert published["pool-automation/variable/freeze-prevention-temperature/state"] == "35.0"

    assert published["pool-automation/status"] == "online"

def test_commandsChangeDevices(plugin:HomeAssistant):
    plugin._publishAll()

    plugin._runCommand("pool-automation/pump/main/set", "SPEED_2")
    assert DependencyContainer.pumps.get("main").currentSpeed == Speed.SPEED_2

    plugin._runCommand("pool-automation/valve/solar/set", "ON")
    assert DependencyContainer.valves.get("solar").isOn

    plugin._runCommand("pool-automation/light/main/set", "Blue")
    assert DependencyContainer.lights.get("main").currentScene == "Blue"

    plugin._runCommand("pool-automation/variable/freeze-prevention-temperature/set", "33.5")
    assert DependencyContainer.variables.get("freeze-prevention-temperature").value == 33.5

def test_changesArePublished(plugin:HomeAssistant):
    """Changes made anywhere in the app are pushed out, not just the ones from Home Assistant
    """
    DependencyContainer.pumps.get("main").on(Speed.SPEED_1)
    DependencyContainer.valves.on("solar")
    DependencyContainer.lights.get("main").change(7)
    DependencyContainer.variables.get("freeze-prevention-enabled").value = True

    published = plugin._client.published
    assert published["pool-automation/pump/main/state"] == "SPEED_1"
    assert published["pool-automation/valve/solar/state"] == "ON"
    assert published["pool-automation/light/main/state"] == "Blue"
    assert published["pool-automation/variable/freeze-prevention-enabled/state"] == "ON"

    DependencyContainer.lights.get("main").off()
    assert published["pool-automation/light/main/state"] == LIGHT_OFF
