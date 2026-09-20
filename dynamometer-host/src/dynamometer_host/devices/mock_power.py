"""Mock 电参（Vin/Iin）— 硬件待确认。"""

from __future__ import annotations

import math
import random
import time


from dynamometer_host.devices.base import IPowerMeter


class MockPowerMeter(IPowerMeter):
    def __init__(self) -> None:
        self._loaded = False
        self._speed = 0.0
        self._brake = 0.0
        self._v = 0.0
        self._i = 0.0
        self._t0 = time.monotonic()

    def set_context(self, *, loaded: bool, speed_rpm: float, brake_percent: float) -> None:
        self._loaded = loaded
        self._speed = abs(speed_rpm)
        self._brake = brake_percent

    def read_voltage_v(self) -> float:
        return self._v

    def read_current_a(self) -> float:
        return self._i

    def tick(self, dt: float) -> None:
        t = time.monotonic() - self._t0
        if self._loaded or self._brake > 1:
            v_tgt = 48.0 + 2.0 * math.sin(t * 0.7)
            # 电流随转速与制动略增
            load = (self._speed / 1500.0) * 3.5 + (self._brake / 100.0) * 2.0
            i_tgt = max(0.2, load) + 0.15 * math.sin(t * 1.9) + random.uniform(-0.05, 0.05)
        else:
            v_tgt = 0.0
            i_tgt = 0.0
        alpha = min(1.0, 4.0 * dt)
        self._v += (v_tgt - self._v) * alpha
        self._i += (i_tgt - self._i) * alpha
        if self._v < 0.05:
            self._v = 0.0
        if self._i < 0.02:
            self._i = 0.0
