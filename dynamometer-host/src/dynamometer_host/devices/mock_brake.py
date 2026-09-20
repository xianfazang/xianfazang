"""Mock KTC-800A：经 AO 0–10 V 映射励磁 %。"""

from __future__ import annotations

from dynamometer_host.devices.base import IAnalogOutput, IBrake


class MockBrake(IBrake):
    """percent 0–100 → AO 0–10 V（通道 0）。"""

    def __init__(self, ao: IAnalogOutput, channel: int = 0) -> None:
        self._ao = ao
        self._channel = channel
        self._percent = 0.0

    def set_brake_percent(self, percent: float) -> None:
        self._percent = max(0.0, min(100.0, float(percent)))
        self._ao.set_voltage(self._channel, self._percent / 10.0)

    def get_brake_percent(self) -> float:
        return self._percent

    def emergency_stop(self) -> None:
        self.set_brake_percent(0.0)
