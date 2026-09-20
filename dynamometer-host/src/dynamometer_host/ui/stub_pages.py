"""占位页签：自动加载 / 数据打印 / 伺服设置 / 输入设置 / 使用说明。"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from dynamometer_host.devices.bus import ConnectionSettings, DeviceBus


class AutoLoadPage(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        lay = QVBoxLayout(self)
        box = QGroupBox("自动加载（Phase 2 占位）")
        form = QFormLayout(box)
        form.addRow("序列文件:", QLineEdit())
        form.addRow("保持时间 (s):", QDoubleSpinBox())
        form.addRow("循环次数:", QSpinBox())
        tip = QLabel("本阶段仅占位。真实自动加载台阶/曲线序列将在 Phase 2 实现。")
        tip.setWordWrap(True)
        form.addRow(tip)
        lay.addWidget(box)
        lay.addStretch()


class PrintPage(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        lay = QVBoxLayout(self)
        box = QGroupBox("数据打印（Phase 2 占位）")
        v = QVBoxLayout(box)
        v.addWidget(QLabel("已采样数据将在此浏览、筛选、导出 CSV/Excel 与打印预览。"))
        row = QHBoxLayout()
        row.addWidget(QPushButton("导出 CSV（占位）"))
        row.addWidget(QPushButton("打印预览（占位）"))
        row.addStretch()
        v.addLayout(row)
        lay.addWidget(box)
        lay.addStretch()


class ServoSettingsPage(QWidget):
    """伺服连接设置 → MockServo。"""

    status_message = Signal(str)
    connected_changed = Signal(bool)

    def __init__(self, bus: DeviceBus, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._bus = bus
        lay = QVBoxLayout(self)

        box = QGroupBox("纳川 SVD750-RS 连接（Mock）")
        form = QFormLayout(box)
        self.port = QComboBox()
        self.port.setEditable(True)
        self.port.addItems(["MOCK", "COM1", "COM2", "COM3", "COM4", "/dev/ttyUSB0"])
        self.port.setCurrentText(bus.settings.servo_port)
        self.baud = QComboBox()
        self.baud.addItems(["9600", "19200", "38400", "57600", "115200"])
        self.baud.setCurrentText(str(bus.settings.servo_baud))
        self.slave = QSpinBox()
        self.slave.setRange(1, 247)
        self.slave.setValue(bus.settings.servo_slave)
        self.rated = QDoubleSpinBox()
        self.rated.setDecimals(3)
        self.rated.setRange(0.001, 1000.0)
        self.rated.setValue(bus.settings.rated_torque_nm)
        self.mode = QComboBox()
        self.mode.addItems(["S-485 速度模式 (Pn023=3)", "t-485 扭矩模式 (Pn023=5)"])
        form.addRow("串口:", self.port)
        form.addRow("波特率:", self.baud)
        form.addRow("站址:", self.slave)
        form.addRow("额定扭矩 (N·m):", self.rated)
        form.addRow("控制模式:", self.mode)

        row = QHBoxLayout()
        self.btn_connect = QPushButton("连接 (Mock)")
        self.btn_disconnect = QPushButton("断开")
        self.lbl = QLabel("状态: 未连接")
        row.addWidget(self.btn_connect)
        row.addWidget(self.btn_disconnect)
        row.addWidget(self.lbl)
        row.addStretch()
        form.addRow(row)

        tip = QLabel(
            "Phase 0 使用 MockServo。现场波特率/校验/站址待确认后接入真实 Modbus。"
        )
        tip.setWordWrap(True)
        form.addRow(tip)
        lay.addWidget(box)
        lay.addStretch()

        self.btn_connect.clicked.connect(self._on_connect)
        self.btn_disconnect.clicked.connect(self._on_disconnect)

    def _sync_settings(self) -> None:
        s = self._bus.settings
        s.servo_port = self.port.currentText().strip() or "MOCK"
        s.servo_baud = int(self.baud.currentText())
        s.servo_slave = self.slave.value()
        s.rated_torque_nm = self.rated.value()

    def _on_connect(self) -> None:
        self._sync_settings()
        self._bus.servo.connect(
            self._bus.settings.servo_port,
            self._bus.settings.servo_baud,
            self._bus.settings.servo_slave,
        )
        self.lbl.setText(f"状态: 已连接 ({self._bus.settings.servo_port})")
        self.status_message.emit("伺服 Mock 已连接")
        self.connected_changed.emit(True)

    def _on_disconnect(self) -> None:
        self._bus.servo.disconnect()
        self.lbl.setText("状态: 未连接")
        self.status_message.emit("伺服已断开")
        self.connected_changed.emit(False)


class InputSettingsPage(QWidget):
    """输入设置 + 可选制动器励磁 %。"""

    brake_changed = Signal(float)
    status_message = Signal(str)

    def __init__(self, bus: DeviceBus, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._bus = bus
        lay = QVBoxLayout(self)

        torque_box = QGroupBox("XMT808-H 扭矩仪（Mock）")
        tf = QFormLayout(torque_box)
        self.t_port = QComboBox()
        self.t_port.setEditable(True)
        self.t_port.addItems(["MOCK", "COM4", "COM5", "/dev/ttyUSB1"])
        self.t_baud = QComboBox()
        self.t_baud.addItems(["9600", "19200"])
        self.t_slave = QSpinBox()
        self.t_slave.setRange(1, 247)
        self.t_slave.setValue(1)
        self.dp = QSpinBox()
        self.dp.setRange(0, 4)
        self.dp.setValue(3)
        tf.addRow("串口:", self.t_port)
        tf.addRow("波特率:", self.t_baud)
        tf.addRow("站址:", self.t_slave)
        tf.addRow("小数点位数:", self.dp)
        row = QHBoxLayout()
        btn_t = QPushButton("连接扭矩仪 (Mock)")
        btn_z = QPushButton("清零")
        row.addWidget(btn_t)
        row.addWidget(btn_z)
        row.addStretch()
        tf.addRow(row)
        lay.addWidget(torque_box)

        ao_box = QGroupBox("制动器励磁 / Modbus AO（Mock）— 不占用加载/卸载")
        af = QFormLayout(ao_box)
        self.ao_port = QComboBox()
        self.ao_port.setEditable(True)
        self.ao_port.addItems(["MOCK", "COM5", "COM6"])
        self.ao_baud = QComboBox()
        self.ao_baud.addItems(["9600", "19200"])
        self.ao_slave = QSpinBox()
        self.ao_slave.setRange(1, 247)
        self.ao_slave.setValue(1)
        self.brake_spin = QDoubleSpinBox()
        self.brake_spin.setRange(0.0, 100.0)
        self.brake_spin.setDecimals(1)
        self.brake_spin.setSuffix(" %")
        self.brake_spin.setValue(0.0)
        af.addRow("AO 串口:", self.ao_port)
        af.addRow("AO 波特率:", self.ao_baud)
        af.addRow("AO 站址:", self.ao_slave)
        af.addRow("励磁给定:", self.brake_spin)
        tip = QLabel(
            "0–100% → Mock AO 0–10 V →（日后）KTC-800A ADJ。加载/卸载键不控制本通道。"
        )
        tip.setWordWrap(True)
        af.addRow(tip)
        lay.addWidget(ao_box)

        power_box = QGroupBox("电参通道（待确认硬件）")
        pf = QFormLayout(power_box)
        pf.addRow(QLabel("Vin / Iin 测量路径尚未锁定；Phase 0 使用 MockPowerMeter。"))
        filt = QDoubleSpinBox()
        filt.setRange(0.0, 1.0)
        filt.setSingleStep(0.05)
        filt.setValue(0.3)
        pf.addRow("滤波系数:", filt)
        lay.addWidget(power_box)
        lay.addStretch()

        btn_t.clicked.connect(self._connect_torque)
        btn_z.clicked.connect(lambda: self._bus.torque.zero())
        self.brake_spin.valueChanged.connect(self._on_brake)

    def _connect_torque(self) -> None:
        s = self._bus.settings
        s.torque_port = self.t_port.currentText()
        s.torque_baud = int(self.t_baud.currentText())
        s.torque_slave = self.t_slave.value()
        self._bus.torque.connect(s.torque_port, s.torque_baud, s.torque_slave)
        self._bus.ao.connect(
            self.ao_port.currentText(),
            int(self.ao_baud.currentText()),
            self.ao_slave.value(),
        )
        self.status_message.emit("扭矩仪 / AO Mock 已连接")

    def _on_brake(self, value: float) -> None:
        self._bus.set_brake_percent(value)
        self.brake_changed.emit(value)

    def set_brake_percent(self, value: float) -> None:
        self.brake_spin.blockSignals(True)
        self.brake_spin.setValue(value)
        self.brake_spin.blockSignals(False)


class HelpPage(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        lay = QVBoxLayout(self)
        box = QGroupBox("使用说明")
        v = QVBoxLayout(box)
        text = QTextEdit()
        text.setReadOnly(True)
        text.setPlainText(
            "减速机测功机上位机 — Phase 0 Mock\n"
            "\n"
            "基本流程\n"
            "1. 在「伺服设置」连接设备（本阶段为 Mock）。\n"
            "2. 「实时数据」→ 初始化 → 设定目标转速/扭矩 → 加载。\n"
            "3. 观察八路曲线与数值栏；可手动/自动采样。\n"
            "4. 卸载停止伺服。制动器励磁 % 在「实时数据」或「输入设置」独立调节，\n"
            "   不占用「加载/卸载」键。\n"
            "\n"
            "安全须知（占位）\n"
            "- 现场急停以硬线为准；软件急停将把 AO 置 0 并卸载伺服。\n"
            "- 真实设备接入前确认串口参数、额定扭矩与控制模式。\n"
            "\n"
            "后续阶段\n"
            "- Phase 1：真实 XMT808-H + 纳川 SVD750-RS；AO 未到货前继续 Mock。\n"
            "- Phase 2：自动加载序列、数据打印导出。\n"
        )
        v.addWidget(text)
        lay.addWidget(box)
