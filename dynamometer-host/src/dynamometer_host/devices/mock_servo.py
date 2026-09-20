"""Mock 纳川 SVD750-RS：加载状态机。"""

from __future__ import annotations

import math
import random
import time

from dynamometer_host.devices.base import IServo, ServoState


class MockServo(IServo):
    def __init__(self) -> None:
        self._state = ServoState.DISCONNECTED
        self._connected = False
        self._port = ""
        self._baud = 19200
        self._slave = 1
        self._target_speed = 0.0
        self._target_torque_nm = 0.0
        self._rated_torque_nm = 1.27
        self._reverse = False
        self._speed = 0.0
        self._torque_pct = 0.0
        self._t0 = time.monotonic()
        self._fault = 0

    @property
    def state(self) -> ServoState:
        return self._state

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def connection_info(self) -> str:
        if not self._connected:
            return "未连接"
        return f"{self._port} @ {self._baud} 站址 {self._slave}"

    def connect(self, port: str, baudrate: int, slave_id: int) -> bool:
        self._port = port or "COM3"
        self._baud = baudrate
        self._slave = slave_id
        self._connected = True
        self._state = ServoState.IDLE
        self._fault = 0
        return True

    def disconnect(self) -> None:
        self.unload()
        self._connected = False
        self._state = ServoState.DISCONNECTED

    def initialize(self) -> bool:
        if not self._connected:
            # Mock 允许未显式连接时一键初始化并假定已连
            self.connect("MOCK", 19200, 1)
        self._state = ServoState.IDLE
        self._speed = 0.0
        self._torque_pct = 0.0
        self._fault = 0
        return True

    def load(
        self,
        *,
        target_speed_rpm: float,
        target_torque_nm: float,
        reverse: bool = False,
        rated_torque_nm: float = 1.27,
    ) -> bool:
        if self._state == ServoState.DISCONNECTED:
            return False
        self._rated_torque_nm = max(rated_torque_nm, 1e-6)
        self.set_targets(
            target_speed_rpm=target_speed_rpm,
            target_torque_nm=target_torque_nm,
            reverse=reverse,
        )
        self._state = ServoState.LOADED
        self._t0 = time.monotonic()
        return True

    def unload(self) -> bool:
        if self._state == ServoState.DISCONNECTED:
            return False
        self._state = ServoState.IDLE
        self._target_speed = 0.0
        # 缓慢滑降至 0 由 tick 完成
        return True

    def set_targets(
        self,
        *,
        target_speed_rpm: float,
        target_torque_nm: float,
        reverse: bool = False,
    ) -> None:
        self._target_speed = abs(target_speed_rpm)
        self._target_torque_nm = target_torque_nm
        self._reverse = reverse

    def read_speed_rpm(self) -> float:
        sign = -1.0 if self._reverse else 1.0
        return sign * self._speed

    def read_torque_feedback_pct(self) -> float:
        return self._torque_pct

    def tick(self, dt: float) -> None:
        if self._state == ServoState.LOADED:
            # 一阶逼近目标转速 + 轻微噪声
            alpha = min(1.0, 3.0 * dt)
            self._speed += (self._target_speed - self._speed) * alpha
            self._speed += random.uniform(-2.0, 2.0)
            self._speed = max(0.0, self._speed)
            pct = (self._target_torque_nm / self._rated_torque_nm) * 100.0
            self._torque_pct += (pct - self._torque_pct) * alpha
            # 轻微正弦扰动模拟波动
            t = time.monotonic() - self._t0
            self._speed += 5.0 * math.sin(t * 1.7)
            if self._speed < 0:
                self._speed = 0.0
        elif self._state == ServoState.IDLE:
            self._speed *= max(0.0, 1.0 - 4.0 * dt)
            self._torque_pct *= max(0.0, 1.0 - 4.0 * dt)
            if self._speed < 0.5:
                self._speed = 0.0
            if abs(self._torque_pct) < 0.1:
                self._torque_pct = 0.0
