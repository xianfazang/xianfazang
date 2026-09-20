"""Mock XMT808-H 扭矩仪。"""

from __future__ import annotations

import math
import random
import time


from dynamometer_host.devices.base import ITorqueSensor


class MockTorqueSensor(ITorqueSensor):
    def __init__(self) -> None:
        self._connected = False
        self._offset = 0.0
        self._commanded_nm = 0.0
        self._loaded = False
        self._brake_pct = 0.0
        self._value = 0.0
        self._t0 = time.monotonic()

    def connect(self, port: str, baudrate: int, slave_id: int) -> bool:
        self._connected = True
        return True

    def disconnect(self) -> None:
        self._connected = False

    def set_load_context(self, *, loaded: bool, target_torque_nm: float, brake_percent: float) -> None:
        """由 DeviceBus 注入伺服/制动上下文，生成合理扭矩波形。"""
        self._loaded = loaded
        self._commanded_nm = target_torque_nm
        self._brake_pct = brake_percent

    def read_torque_nm(self) -> float:
        return self._value - self._offset

    def zero(self) -> None:
        self._offset = self._value

    def tick(self, dt: float) -> None:
        t = time.monotonic() - self._t0
        # 制动器 % 贡献一部分负载扭矩；伺服目标扭矩另一部分
        brake_nm = (self._brake_pct / 100.0) * 2.5
        base = 0.0
        if self._loaded:
            base = max(self._commanded_nm, 0.05) + brake_nm * 0.4
            base += 0.08 * math.sin(t * 2.3) + random.uniform(-0.02, 0.02)
        else:
            base = brake_nm * 0.6 + random.uniform(-0.005, 0.005)
            if abs(base) < 0.01 and self._brake_pct < 1:
                base = 0.0
        alpha = min(1.0, 5.0 * dt)
        self._value += (base - self._value) * alpha
