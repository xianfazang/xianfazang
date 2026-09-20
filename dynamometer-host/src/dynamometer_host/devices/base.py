"""设备抽象接口。"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto


class ServoState(Enum):
    DISCONNECTED = auto()
    IDLE = auto()  # 已初始化，未加载
    LOADED = auto()
    FAULT = auto()


@dataclass
class TelemetrySample:
    """一次轮询的合成遥测（供 UI / 采样使用）。"""

    torque_nm: float = 0.0
    speed_rpm: float = 0.0
    temperature_c: float = 25.0
    angle_deg: float = 0.0
    voltage_v: float = 0.0
    current_a: float = 0.0
    brake_percent: float = 0.0
    servo_state: ServoState = ServoState.DISCONNECTED
    fault_code: int = 0


class IServo(ABC):
    """纳川 SVD750-RS 抽象（加载/卸载只走此接口）。"""

    @abstractmethod
    def connect(self, port: str, baudrate: int, slave_id: int) -> bool: ...

    @abstractmethod
    def disconnect(self) -> None: ...

    @abstractmethod
    def initialize(self) -> bool: ...

    @abstractmethod
    def load(
        self,
        *,
        target_speed_rpm: float,
        target_torque_nm: float,
        reverse: bool = False,
        rated_torque_nm: float = 1.27,
    ) -> bool: ...

    @abstractmethod
    def unload(self) -> bool: ...

    @abstractmethod
    def set_targets(
        self,
        *,
        target_speed_rpm: float,
        target_torque_nm: float,
        reverse: bool = False,
    ) -> None: ...

    @property
    @abstractmethod
    def state(self) -> ServoState: ...

    @abstractmethod
    def read_speed_rpm(self) -> float: ...

    @abstractmethod
    def read_torque_feedback_pct(self) -> float: ...

    @abstractmethod
    def tick(self, dt: float) -> None:
        """推进 Mock / 后台仿真。"""


class ITorqueSensor(ABC):
    """XMT808-H 扭矩通道抽象。"""

    @abstractmethod
    def connect(self, port: str, baudrate: int, slave_id: int) -> bool: ...

    @abstractmethod
    def disconnect(self) -> None: ...

    @abstractmethod
    def read_torque_nm(self) -> float: ...

    @abstractmethod
    def zero(self) -> None: ...

    @abstractmethod
    def tick(self, dt: float) -> None: ...


class IAnalogOutput(ABC):
    """RS485 Modbus AO 模块（0–10 V）抽象。"""

    @abstractmethod
    def connect(self, port: str, baudrate: int, slave_id: int) -> bool: ...

    @abstractmethod
    def disconnect(self) -> None: ...

    @abstractmethod
    def set_voltage(self, channel: int, volts: float) -> None: ...

    @abstractmethod
    def get_voltage(self, channel: int = 0) -> float: ...


class IBrake(ABC):
    """KTC-800A 经 AO 的励磁控制（与加载/卸载无关）。"""

    @abstractmethod
    def set_brake_percent(self, percent: float) -> None: ...

    @abstractmethod
    def get_brake_percent(self) -> float: ...

    @abstractmethod
    def emergency_stop(self) -> None: ...


class IPowerMeter(ABC):
    """电参（Vin/Iin）— 硬件待确认，Phase 0 Mock。"""

    @abstractmethod
    def read_voltage_v(self) -> float: ...

    @abstractmethod
    def read_current_a(self) -> float: ...

    @abstractmethod
    def tick(self, dt: float) -> None: ...
