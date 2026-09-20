#!/usr/bin/env python3
"""启动 UI 并截图保存到项目 store media/。"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

STORE_MEDIA = Path("/cursor/stores/bc-74d2538e-3a5e-40bf-81fa-d7e47109ac84/media")
OUT = STORE_MEDIA / "phase0-mock-ui.png"
OUT_LOADED = STORE_MEDIA / "phase0-mock-ui-loaded.png"


def main() -> int:
    if not os.environ.get("DISPLAY") and sys.platform != "win32":
        print("No DISPLAY — skip screenshot")
        return 0

    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication

    from dynamometer_host.ui.main_window import MainWindow
    from dynamometer_host.ui.styles import APP_STYLESHEET

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(APP_STYLESHEET)

    win = MainWindow()
    win.show()
    win.raise_()

    STORE_MEDIA.mkdir(parents=True, exist_ok=True)

    def shot1():
        win.grab().save(str(OUT))
        print(f"saved {OUT}")
        # 连接 + 初始化 + 加载，再截一张有曲线的
        win.bus.connect_all()
        win.bus.initialize_servo()
        win.realtime.target_speed.setValue(900)
        win.realtime.target_torque.setValue(1.0)
        win.bus.load_servo(target_speed_rpm=900, target_torque_nm=1.0)
        win.bus.set_brake_percent(25.0)
        win.realtime.sync_brake_percent(25.0)
        win._set_status("演示：已加载 Mock 伺服，制动 25%")

    def shot2():
        # 让曲线跑一会儿
        win.grab().save(str(OUT_LOADED))
        print(f"saved {OUT_LOADED}")
        app.quit()

    QTimer.singleShot(800, shot1)
    QTimer.singleShot(3500, shot2)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
