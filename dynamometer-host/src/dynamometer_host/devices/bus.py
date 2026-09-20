"""DeviceBus：聚合 Mock/真实设备，供 UI 轮询。"""

from __future__ import annotations

import time
from dataclasses import dataclass

from dynamometer_host.devices.base import (
    IAnalogOutput,
    IBrake,
    IPowerMeter,
    IServo,
    ITorqueSensor,
    ServoState,
    TelemetrySample,
)
from dynamometer_host.devices.mock_ao import MockAnalogOutput
from dynamometer_host.devices.mock_brake import MockBrake
from dynamometer_host.devices.mock_power import MockPowerMeter
from dynamometer_host.devices.mock_servo import MockServo
from dynamometer_host.devices.mock_torque import MockTorqueSensor


@dataclass
class ConnectionSettings:
    servo_port: str = "COM3"
    servo_baud: int = 19200
    servo_slave: int = 1
    torque_port: str = "COM4"
    torque_baud: int = 9600
    torque_slave: int = 1
    ao_port: str = "COM5"
    ao_baud: int = 9600
    ao_slave: int = 1
    rated_torque_nm: float = 1.27


class DeviceBus:
    def __init__(
        self,
        servo: IServo,
        torque: ITorqueSensor,
        ao: IAnalogOutput,
        brake: IBrake,
        power: IPowerMeter,
    ) -> None:
        self.servo = servo
        self.torque = torque
        self.ao = ao
        self.brake = brake
        self.power = power
        self.settings = ConnectionSettings()
        self._last_t = time.monotonic()
        self._angle = 0.0
        self._temp = 28.0
        # 最近一次加载目标（供扭矩 Mock）
        self._target_torque_nm = 0.0
        self._target_speed_rpm = 0.0
        self._reverse = False

    @classmethod
    def create_mock(cls) -> DeviceBus:
        ao = MockAnalogOutput()
        return cls(
            servo=MockServo(),
            torque=MockTorqueSensor(),
            ao=ao,
            brake=MockBrake(ao),
            power=MockPowerMeter(),
        )

    def connect_all(self) -> None:
        s = self.settings
        self.servo.connect(s.servo_port, s.servo_baud, s.servo_slave)
        self.torque.connect(s.torque_port, s.torque_baud, s.torque_slave)
        self.ao.connect(s.ao_port, s.ao_baud, s.ao_slave)

    def disconnect_all(self) -> None:
        self.servo.disconnect()
        self.torque.disconnect()
        self.ao.disconnect()

    def initialize_servo(self) -> bool:
        return self.servo.initialize()

    def load_servo(
        self,
        *,
        target_speed_rpm: float,
        target_torque_nm: float,
        reverse: bool = False,
    ) -> bool:
        self._target_speed_rpm = target_speed_rpm
        self._target_torque_nm = target_torque_nm
        self._reverse = reverse
        return self.servo.load(
            target_speed_rpm=target_speed_rpm,
            target_torque_nm=target_torque_nm,
            reverse=reverse,
            rated_torque_nm=self.settings.rated_torque_nm,
        )

    def unload_servo(self) -> bool:
        return self.servo.unload()

    def set_brake_percent(self, percent: float) -> None:
        self.brake.set_brake_percent(percent)

    def poll(self) -> TelemetrySample:
        now = time.monotonic()
        dt = max(1e-3, now - self._last_t)
        self._last_t = now

        loaded = self.servo.state == ServoState.LOADED
        if loaded:
            self.servo.set_targets(
                target_speed_rpm=self._target_speed_rpm,
                target_torque_nm=self._target_torque_nm,
                reverse=self._reverse,
            )

        self.servo.tick(dt)
        speed = self.servo.read_speed_rpm()
        brake_pct = self.brake.get_brake_percent()

        if isinstance(self.torque, MockTorqueSensor):
            self.torque.set_load_context(
                loaded=loaded,
                target_torque_nm=self._target_torque_nm,
                brake_percent=brake_pct,
            )
        self.torque.tick(dt)

        if isinstance(self.power, MockPowerMeter):
            self.power.set_context(loaded=loaded, speed_rpm=speed, brake_percent=brake_pct)
        self.power.tick(dt)

        # 角度积分（示意）
        self._angle = (self._angle + abs(speed) * dt * 6.0) % 360.0
        # 温度随负载缓慢上升
        t_tgt = 45.0 if loaded else 28.0
        t_tgt += brake_pct * 0.08
        self._temp += (t_tgt - self._temp) * min(1.0, 0.15 * dt)

        return TelemetrySample(
            torque_nm=self.torque.read_torque_nm(),
            speed_rpm=speed,
            temperature_c=self._temp,
            angle_deg=self._angle,
            voltage_v=self.power.read_voltage_v(),
            current_a=self.power.read_current_a(),
            brake_percent=brake_pct,
            servo_state=self.servo.state,
            fault_code=0,
        )
