"""主窗口：六大页签。"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMainWindow, QTabWidget, QStatusBar

from dynamometer_host.core.sampling import SampleStore
from dynamometer_host.devices.bus import DeviceBus
from dynamometer_host.ui.realtime_page import RealtimePage
from dynamometer_host.ui.stub_pages import (
    AutoLoadPage,
    HelpPage,
    InputSettingsPage,
    PrintPage,
    ServoSettingsPage,
)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("减速机测功机上位机")
        self.resize(1280, 860)
        self.setMinimumSize(1024, 720)

        self.bus = DeviceBus.create_mock()
        self.store = SampleStore()

        self.tabs = QTabWidget()
        self.realtime = RealtimePage(self.bus, self.store)
        self.auto_load = AutoLoadPage()
        self.print_page = PrintPage()
        self.servo_settings = ServoSettingsPage(self.bus)
        self.input_settings = InputSettingsPage(self.bus)
        self.help_page = HelpPage()

        self.tabs.addTab(self.realtime, "实时数据")
        self.tabs.addTab(self.auto_load, "自动加载")
        self.tabs.addTab(self.print_page, "数据打印")
        self.tabs.addTab(self.servo_settings, "伺服设置")
        self.tabs.addTab(self.input_settings, "输入设置")
        self.tabs.addTab(self.help_page, "使用说明")
        self.setCentralWidget(self.tabs)

        sb = QStatusBar()
        self.setStatusBar(sb)
        self._set_status("就绪 - 请在伺服设置页面连接设备")

        self.realtime.status_message.connect(self._set_status)
        self.servo_settings.status_message.connect(self._set_status)
        self.input_settings.status_message.connect(self._set_status)
        self.servo_settings.connected_changed.connect(self._on_servo_connected)

        # 制动器双向同步
        self.realtime.brake_changed.connect(self.input_settings.set_brake_percent)
        self.input_settings.brake_changed.connect(self.realtime.sync_brake_percent)

        # 菜单：急停
        act_estop = QAction("软件急停", self)
        act_estop.triggered.connect(self._estop)
        self.menuBar().addAction(act_estop)

    def _set_status(self, text: str) -> None:
        self.statusBar().showMessage(text)

    def _on_servo_connected(self, ok: bool) -> None:
        if ok:
            self._set_status("伺服已连接 (Mock) — 可在实时数据页初始化/加载")
        else:
            self._set_status("就绪 - 请在伺服设置页面连接设备")

    def _estop(self) -> None:
        self.bus.unload_servo()
        self.bus.brake.emergency_stop()
        self.realtime.sync_brake_percent(0.0)
        self.input_settings.set_brake_percent(0.0)
        self._set_status("软件急停 — 伺服已卸载，AO 励磁已置 0")
