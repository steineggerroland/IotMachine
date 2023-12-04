from iot.machine.IotMachine import IotMachine
from iot.machine.PowerStateDecorator import PowerState, SimplePowerStateDecorator


class WashingMachine(IotMachine):
    def __init__(self, name, watt=None):
        super().__init__(name, watt)
        self.power_state = PowerState.UNKNOWN
        self._power_state_decoration = SimplePowerStateDecorator(self)

    def update_power_consumption(self, watt):
        self._power_state_decoration.update_power_consumption(watt)

    def to_dict(self):
        return {"name": self.name, "watt": self.watt, "power_state": self.power_state}


def from_dict(dictionary: dict):
    return WashingMachine(dictionary['name'], dictionary['watt'] if 'watt' in dictionary else None)
