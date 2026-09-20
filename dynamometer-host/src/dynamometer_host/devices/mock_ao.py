"""Mock Modbus AO（0–10 V）。"""

from __future__ import annotations

from dynamometer_host.devices.base import IAnalogOutput


class MockAnalogOutput(IAnalogOutput):
    def __init__(self, channels: int = 8) -> None:
        self._connected = False
        self._volts = [0.0] * channels

    def connect(self, port: str, baudrate: int, slave_id: int) -> bool:
        self._connected = True
        return True

    def disconnect(self) -> None:
        self._connected = False
        self._volts = [0.0] * len(self._volts)

    def set_voltage(self, channel: int, volts: float) -> None:
        if channel < 0 or channel >= len(self._volts):
            raise IndexError(channel)
        self._volts[channel] = max(0.0, min(10.0, float(volts)))

    def get_voltage(self, channel: int = 0) -> float:
        return self._volts[channel]
