"""实时数据页 — 对照参考截图布局。"""

from __future__ import annotations

import time

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QDoubleSpinBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QSizePolicy,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from dynamometer_host.core.calc import efficiency, input_power, output_power
from dynamometer_host.core.sampling import SampleStore
from dynamometer_host.devices.base import ServoState
from dynamometer_host.devices.bus import DeviceBus
from dynamometer_host.ui.charts import RealtimeChart


class RealtimePage(QWidget):
    status_message = Signal(str)
    sample_count_changed = Signal(int)
    brake_changed = Signal(float)

    def __init__(self, bus: DeviceBus, store: SampleStore, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._bus = bus
        self._store = store
        self._auto_sample_left = 0.0

        root = QVBoxLayout(self)
        root.setContentsMargins(6, 6, 6, 4)
        root.setSpacing(4)

        root.addWidget(self._build_servo_panel())
        root.addWidget(self._build_temp_alarm_panel())
        root.addWidget(self._build_charts(), stretch=1)
        root.addWidget(self._build_sample_row())
        root.addWidget(self._build_brake_row())
        root.addWidget(self._build_readouts())

        self._timer = QTimer(self)
        self._timer.setInterval(50)  # 20 Hz UI
        self._timer.timeout.connect(self._on_tick)
        self._timer.start()

        self._last = {
            "torque": 0.0,
            "speed": 0.0,
            "p_out": 0.0,
            "temp": 0.0,
            "angle": 0.0,
            "volt": 0.0,
            "curr": 0.0,
            "p_in": 0.0,
            "eta": None,
            "brake": 0.0,
        }

    # ----- panels -----

    def _build_servo_panel(self) -> QGroupBox:
        box = QGroupBox("伺服控制面板")
        row = QHBoxLayout(box)
        row.setSpacing(8)

        self.btn_init = QPushButton("初始化")
        self.btn_init.setObjectName("btnInit")
        self.btn_load = QPushButton("加载")
        self.btn_load.setObjectName("btnLoad")
        self.btn_unload = QPushButton("卸载")
        self.btn_unload.setObjectName("btnUnload")
        for b in (self.btn_init, self.btn_load, self.btn_unload):
            b.setMinimumWidth(78)
            b.setMinimumHeight(30)
            row.addWidget(b)

        self.radio_manual = QRadioButton("手动")
        self.radio_auto = QRadioButton("自动")
        self.radio_manual.setChecked(True)
        row.addWidget(self.radio_manual)
        row.addWidget(self.radio_auto)

        self.btn_cycle = QPushButton("循环加载")
        self.btn_cycle.setEnabled(False)
        row.addWidget(self.btn_cycle)

        row.addWidget(QLabel("循环次数:"))
        self.cycle_count = QSpinBox()
        self.cycle_count.setRange(0, 9999)
        self.cycle_count.setSpecialValueText("无限")
        self.cycle_count.setValue(0)
        self.cycle_count.setFixedWidth(70)
        row.addWidget(self.cycle_count)

        row.addWidget(QLabel("力矩参考 (Nm):"))
        self.torque_ref = QDoubleSpinBox()
        self.torque_ref.setDecimals(3)
        self.torque_ref.setRange(0.001, 1000.0)
        self.torque_ref.setValue(1.27)
        self.torque_ref.setFixedWidth(80)
        row.addWidget(self.torque_ref)

        row.addWidget(QLabel("目标扭矩 (Nm):"))
        self.target_torque = QDoubleSpinBox()
        self.target_torque.setDecimals(3)
        self.target_torque.setRange(0.0, 1000.0)
        self.target_torque.setValue(0.0)
        self.target_torque.setSingleStep(0.1)
        self.target_torque.setFixedWidth(90)
        row.addWidget(self.target_torque)

        self.chk_reverse = QCheckBox("反向")
        row.addWidget(self.chk_reverse)

        row.addWidget(QLabel("目标转速 (RPM):"))
        self.target_speed = QSpinBox()
        self.target_speed.setRange(0, 6000)
        self.target_speed.setValue(0)
        self.target_speed.setFixedWidth(80)
        row.addWidget(self.target_speed)

        row.addStretch()

        self.btn_init.clicked.connect(self._on_init)
        self.btn_load.clicked.connect(self._on_load)
        self.btn_unload.clicked.connect(self._on_unload)
        self.radio_auto.toggled.connect(self._on_mode)
        self.torque_ref.valueChanged.connect(self._on_rated_changed)
        return box

    def _build_temp_alarm_panel(self) -> QGroupBox:
        box = QGroupBox("温度报警设置")
        row = QHBoxLayout(box)
        self.chk_temp_alarm = QCheckBox("启用温度报警")
        row.addWidget(self.chk_temp_alarm)
        row.addWidget(QLabel("报警温度 (℃):"))
        self.alarm_temp = QSpinBox()
        self.alarm_temp.setRange(0, 200)
        self.alarm_temp.setValue(80)
        self.alarm_temp.setFixedWidth(70)
        row.addWidget(self.alarm_temp)
        self.chk_auto_restart = QCheckBox("自动重启")
        row.addWidget(self.chk_auto_restart)
        self.lbl_temp_status = QLabel("状态: 未启用")
        row.addWidget(self.lbl_temp_status)
        row.addStretch()
        self.chk_temp_alarm.toggled.connect(self._update_temp_status)
        return box

    def _build_charts(self) -> QWidget:
        wrap = QWidget()
        grid = QGridLayout(wrap)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(4)

        specs = [
            ("扭矩", "N·m"),
            ("转速", "RPM"),
            ("输出功率", "W"),
            ("芯片温度", "℃"),
            ("输入电压", "V"),
            ("输入电流", "A"),
            ("输入功率", "W"),
            ("效率", "%"),
        ]
        self._charts: list[RealtimeChart] = []
        for i, (title, unit) in enumerate(specs):
            chart = RealtimeChart(title, unit, window_s=30.0)
            chart.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            self._charts.append(chart)
            grid.addWidget(chart, i // 4, i % 4)
        return wrap

    def _build_sample_row(self) -> QWidget:
        w = QWidget()
        row = QHBoxLayout(w)
        row.setContentsMargins(0, 2, 0, 2)
        self.btn_sample = QPushButton("采样当前数据")
        self.btn_sample.setObjectName("btnSample")
        row.addWidget(self.btn_sample)
        self.chk_auto_sample = QCheckBox("自动采样")
        row.addWidget(self.chk_auto_sample)
        row.addWidget(QLabel("间隔(秒):"))
        self.sample_interval = QSpinBox()
        self.sample_interval.setRange(1, 3600)
        self.sample_interval.setValue(10)
        self.sample_interval.setFixedWidth(70)
        row.addWidget(self.sample_interval)
        row.addStretch()
        self.lbl_sample_count = QLabel("已采样: 0 组数据")
        row.addWidget(self.lbl_sample_count)
        self.btn_sample.clicked.connect(self._sample_now)
        return w

    def _build_brake_row(self) -> QWidget:
        """独立制动器励磁 — 不占用加载/卸载。"""
        w = QGroupBox("制动器励磁 %（Mock AO → KTC，独立于加载/卸载）")
        row = QHBoxLayout(w)
        self.brake_slider = QSlider(Qt.Orientation.Horizontal)
        self.brake_slider.setRange(0, 1000)  # 0.1%
        self.brake_slider.setValue(0)
        self.brake_spin = QDoubleSpinBox()
        self.brake_spin.setRange(0.0, 100.0)
        self.brake_spin.setDecimals(1)
        self.brake_spin.setSuffix(" %")
        self.brake_spin.setFixedWidth(90)
        row.addWidget(QLabel("励磁:"))
        row.addWidget(self.brake_slider, stretch=1)
        row.addWidget(self.brake_spin)
        self.brake_slider.valueChanged.connect(self._on_brake_slider)
        self.brake_spin.valueChanged.connect(self._on_brake_spin)
        return w

    def _build_readouts(self) -> QWidget:
        wrap = QWidget()
        v = QVBoxLayout(wrap)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(3)

        row1 = QHBoxLayout()
        row2 = QHBoxLayout()
        self._readouts: dict[str, QLabel] = {}
        keys1 = [
            ("torque", "扭矩", "N·m"),
            ("speed", "转速", "RPM"),
            ("p_out", "输出功率", "W"),
            ("temp", "温度", "℃"),
            ("angle", "角度", "°"),
        ]
        keys2 = [
            ("volt", "输入电压", "V"),
            ("curr", "输入电流", "A"),
            ("p_in", "输入功率", "W"),
            ("eta", "效率", "%"),
        ]
        for key, name, unit in keys1:
            lbl = QLabel(f"{name}: -- {unit}")
            lbl.setObjectName("readoutLabel")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._readouts[key] = lbl
            row1.addWidget(lbl)
        for key, name, unit in keys2:
            lbl = QLabel(f"{name}: -- {unit}")
            lbl.setObjectName("readoutLabel")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._readouts[key] = lbl
            row2.addWidget(lbl)
        v.addLayout(row1)
        v.addLayout(row2)
        return wrap

    # ----- actions -----

    def _on_rated_changed(self, value: float) -> None:
        self._bus.settings.rated_torque_nm = value

    def _on_mode(self, auto: bool) -> None:
        self.btn_cycle.setEnabled(auto)
        if auto:
            self.status_message.emit("自动模式（序列占位）— 请使用手动加载演示 Mock")
        else:
            self.status_message.emit("手动模式")

    def _on_init(self) -> None:
        ok = self._bus.initialize_servo()
        if ok:
            self.status_message.emit("伺服已初始化（Mock）— 就绪")
        else:
            self.status_message.emit("初始化失败")

    def _on_load(self) -> None:
        speed = float(self.target_speed.value())
        torque = float(self.target_torque.value())
        if speed <= 0 and torque <= 0:
            # 给一组演示默认值，便于开箱看曲线
            speed = 800.0
            torque = 0.8
            self.target_speed.setValue(int(speed))
            self.target_torque.setValue(torque)
        ok = self._bus.load_servo(
            target_speed_rpm=speed,
            target_torque_nm=torque,
            reverse=self.chk_reverse.isChecked(),
        )
        if ok:
            self.status_message.emit(f"加载中 — 目标 {speed:.0f} RPM / {torque:.3f} N·m")
        else:
            self.status_message.emit("加载失败 — 请先初始化或在伺服设置连接")

    def _on_unload(self) -> None:
        self._bus.unload_servo()
        self.status_message.emit("已卸载 — 伺服停止")

    def _update_temp_status(self) -> None:
        if not self.chk_temp_alarm.isChecked():
            self.lbl_temp_status.setText("状态: 未启用")
            return
        temp = self._last["temp"]
        limit = self.alarm_temp.value()
        if temp >= limit:
            self.lbl_temp_status.setText(f"状态: 报警! {temp:.1f}≥{limit}")
            self.lbl_temp_status.setStyleSheet("color: #c00000; font-weight: bold;")
        else:
            self.lbl_temp_status.setText(f"状态: 正常 ({temp:.1f}℃)")
            self.lbl_temp_status.setStyleSheet("color: #206020;")

    def _on_brake_slider(self, raw: int) -> None:
        pct = raw / 10.0
        self.brake_spin.blockSignals(True)
        self.brake_spin.setValue(pct)
        self.brake_spin.blockSignals(False)
        self._bus.set_brake_percent(pct)
        self.brake_changed.emit(pct)

    def _on_brake_spin(self, pct: float) -> None:
        self.brake_slider.blockSignals(True)
        self.brake_slider.setValue(int(round(pct * 10)))
        self.brake_slider.blockSignals(False)
        self._bus.set_brake_percent(pct)
        self.brake_changed.emit(pct)

    def sync_brake_percent(self, pct: float) -> None:
        self.brake_slider.blockSignals(True)
        self.brake_spin.blockSignals(True)
        self.brake_slider.setValue(int(round(pct * 10)))
        self.brake_spin.setValue(pct)
        self.brake_slider.blockSignals(False)
        self.brake_spin.blockSignals(False)

    def _sample_now(self) -> None:
        d = self._last
        self._store.add(
            torque_nm=d["torque"],
            speed_rpm=d["speed"],
            p_out_w=d["p_out"],
            temperature_c=d["temp"],
            angle_deg=d["angle"],
            voltage_v=d["volt"],
            current_a=d["curr"],
            p_in_w=d["p_in"],
            efficiency_pct=d["eta"],
            brake_percent=d["brake"],
        )
        n = len(self._store)
        self.lbl_sample_count.setText(f"已采样: {n} 组数据")
        self.sample_count_changed.emit(n)
        self.status_message.emit(f"已采样第 {n} 组")

    def _fmt(self, key: str, name: str, unit: str, value: float | None, digits: int = 3) -> None:
        lbl = self._readouts[key]
        if value is None:
            lbl.setText(f"{name}: -- {unit}")
        else:
            lbl.setText(f"{name}: {value:.{digits}f} {unit}")

    def _on_tick(self) -> None:
        sample = self._bus.poll()
        t = time.monotonic()
        p_out = output_power(sample.torque_nm, abs(sample.speed_rpm))
        p_in = input_power(sample.voltage_v, sample.current_a)
        eta = efficiency(p_out, p_in)

        self._last = {
            "torque": sample.torque_nm,
            "speed": sample.speed_rpm,
            "p_out": p_out,
            "temp": sample.temperature_c,
            "angle": sample.angle_deg,
            "volt": sample.voltage_v,
            "curr": sample.current_a,
            "p_in": p_in,
            "eta": eta,
            "brake": sample.brake_percent,
        }

        values = [
            sample.torque_nm,
            sample.speed_rpm,
            p_out,
            sample.temperature_c,
            sample.voltage_v,
            sample.current_a,
            p_in,
            eta if eta is not None else 0.0,
        ]
        for chart, val in zip(self._charts, values):
            chart.append(t, val)

        self._fmt("torque", "扭矩", "N·m", sample.torque_nm)
        self._fmt("speed", "转速", "RPM", sample.speed_rpm, 1)
        self._fmt("p_out", "输出功率", "W", p_out)
        self._fmt("temp", "温度", "℃", sample.temperature_c, 1)
        self._fmt("angle", "角度", "°", sample.angle_deg, 1)
        self._fmt("volt", "输入电压", "V", sample.voltage_v, 2)
        self._fmt("curr", "输入电流", "A", sample.current_a, 3)
        self._fmt("p_in", "输入功率", "W", p_in, 2)
        self._fmt("eta", "效率", "%", eta, 2)

        self._update_temp_status()

        # 温报警：可选卸载
        if (
            self.chk_temp_alarm.isChecked()
            and sample.temperature_c >= self.alarm_temp.value()
            and sample.servo_state == ServoState.LOADED
        ):
            self._bus.unload_servo()
            self.status_message.emit("温度报警 — 已自动卸载伺服")

        if self.chk_auto_sample.isChecked():
            interval = float(self.sample_interval.value())
            self._auto_sample_left -= 0.05
            if self._auto_sample_left <= 0:
                self._sample_now()
                self._auto_sample_left = interval
        else:
            self._auto_sample_left = 0.0
