"""应用入口：``python -m dynamometer_host``."""

from __future__ import annotations

import os
import sys


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)

    if "--smoke" in argv:
        from dynamometer_host.smoke import run_smoke

        return run_smoke()

    # Headless: no DISPLAY → import + calc/mock smoke instead of GUI
    if not os.environ.get("DISPLAY") and sys.platform != "win32":
        from dynamometer_host.smoke import run_smoke

        print("DISPLAY 不可用，执行无界面冒烟检查…")
        return run_smoke()

    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QFont

    from dynamometer_host.ui.main_window import MainWindow
    from dynamometer_host.ui.styles import APP_STYLESHEET

    # High-DPI friendly
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    app.setApplicationName("减速机测功机上位机")
    app.setOrganizationName("DynamometerHost")
    app.setStyle("Fusion")
    app.setStyleSheet(APP_STYLESHEET)

    font = QFont()
    font.setFamilies(
        [
            "Microsoft YaHei UI",
            "Microsoft YaHei",
            "WenQuanYi Micro Hei",
            "Noto Sans CJK SC",
            "Droid Sans Fallback",
            "SimHei",
            "Sans Serif",
        ]
    )
    font.setPointSize(9)
    app.setFont(font)

    win = MainWindow()
    win.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
