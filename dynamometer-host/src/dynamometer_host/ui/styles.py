"""工业浅灰 Win 风格样式（对照参考截图）。"""

APP_STYLESHEET = """
QMainWindow, QWidget {
    background-color: #f0f0f0;
    color: #202020;
}
QTabWidget::pane {
    border: 1px solid #a0a0a0;
    background: #f0f0f0;
    top: -1px;
}
QTabBar::tab {
    background: #e4e4e4;
    border: 1px solid #a0a0a0;
    border-bottom: none;
    padding: 6px 16px;
    margin-right: 2px;
    min-width: 72px;
}
QTabBar::tab:selected {
    background: #f0f0f0;
    font-weight: bold;
}
QTabBar::tab:!selected {
    margin-top: 2px;
}
QGroupBox {
    border: 1px solid #a8a8a8;
    margin-top: 10px;
    padding: 8px 8px 6px 8px;
    background: #f5f5f5;
    font-weight: bold;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
}
QPushButton {
    padding: 4px 12px;
    min-height: 24px;
    border: 1px solid #888;
    background: #e8e8e8;
}
QPushButton:hover {
    background: #f2f2f2;
}
QPushButton:pressed {
    background: #d0d0d0;
}
QPushButton:disabled {
    color: #888;
    background: #ddd;
}
QPushButton#btnInit {
    background-color: #f0a040;
    border-color: #c07020;
    font-weight: bold;
    color: #202020;
    min-width: 72px;
}
QPushButton#btnLoad {
    background-color: #40b060;
    border-color: #208040;
    font-weight: bold;
    color: #fff;
    min-width: 72px;
}
QPushButton#btnUnload {
    background-color: #e05050;
    border-color: #a03030;
    font-weight: bold;
    color: #fff;
    min-width: 72px;
}
QPushButton#btnSample {
    background-color: #3080d0;
    border-color: #2060a0;
    font-weight: bold;
    color: #fff;
    min-width: 110px;
}
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background: #ffffff;
    border: 1px solid #9a9a9a;
    padding: 2px 4px;
    min-height: 22px;
}
QStatusBar {
    background: #e8e8e8;
    border-top: 1px solid #b0b0b0;
}
QLabel#readoutLabel {
    background: #e6e6e6;
    border: 1px solid #b0b0b0;
    padding: 6px 10px;
    font-size: 13px;
}
QLabel#chartTitle {
    font-weight: bold;
    font-size: 11px;
}
QSlider::groove:horizontal {
    height: 6px;
    background: #ccc;
    border-radius: 3px;
}
QSlider::handle:horizontal {
    width: 14px;
    margin: -5px 0;
    background: #6080a0;
    border: 1px solid #406080;
    border-radius: 7px;
}
"""
