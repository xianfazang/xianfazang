"""pyqtgraph 实时曲线小部件（白底黑网格，~30 s 滚动）。"""

from __future__ import annotations

from collections import deque

import pyqtgraph as pg
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


# 参考图：白底黑网格
pg.setConfigOptions(antialias=True, foreground="k", background="w")


class RealtimeChart(QWidget):
    def __init__(
        self,
        title: str,
        unit: str,
        *,
        window_s: float = 30.0,
        y_min: float | None = None,
        y_max: float | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._unit = unit
        self._window_s = window_s
        self._xs: deque[float] = deque()
        self._ys: deque[float] = deque()
        self._t0: float | None = None
        self._fixed_yrange = y_min is not None and y_max is not None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)

        self._title = QLabel(title)
        self._title.setObjectName("chartTitle")
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._title)

        self._plot = pg.PlotWidget()
        self._plot.showGrid(x=True, y=True, alpha=0.35)
        self._plot.setLabel("bottom", "时间", units="s")
        self._plot.setLabel("left", unit)
        self._plot.setXRange(0, window_s, padding=0)
        if self._fixed_yrange:
            self._plot.setYRange(y_min, y_max, padding=0.05)
        self._plot.getAxis("bottom").enableAutoSIPrefix(False)
        self._plot.getAxis("left").enableAutoSIPrefix(False)
        self._curve = self._plot.plot(pen=pg.mkPen("#1a5fb4", width=1.5))

        # 当前值标注（图内文字）
        self._text = pg.TextItem(color="#c06000", anchor=(0, 0))
        self._plot.addItem(self._text)
        self._text.setPos(1.0, 0)

        layout.addWidget(self._plot, stretch=1)
        self._set_current(None)

    def _set_current(self, value: float | None) -> None:
        if value is None:
            self._text.setText(f"当前: -- {self._unit}")
        else:
            self._text.setText(f"当前: {value:.3f} {self._unit}")

    def clear(self) -> None:
        self._xs.clear()
        self._ys.clear()
        self._t0 = None
        self._curve.setData([], [])
        self._set_current(None)

    def append(self, t_abs: float, value: float) -> None:
        if self._t0 is None:
            self._t0 = t_abs
        t_rel = t_abs - self._t0
        self._xs.append(t_rel)
        self._ys.append(value)

        # 丢弃窗口外数据
        while self._xs and (t_rel - self._xs[0]) > self._window_s:
            self._xs.popleft()
            self._ys.popleft()

        xs = list(self._xs)
        ys = list(self._ys)
        self._curve.setData(xs, ys)

        x_right = max(self._window_s, t_rel)
        x_left = x_right - self._window_s
        self._plot.setXRange(x_left, x_right, padding=0)

        if ys and not self._fixed_yrange:
            ymin, ymax = min(ys), max(ys)
            if abs(ymax - ymin) < 1e-9:
                pad = max(0.1, abs(ymax) * 0.1 + 0.05)
                self._plot.setYRange(ymin - pad, ymax + pad, padding=0)
            else:
                self._plot.setYRange(ymin, ymax, padding=0.12)

        # 文本放在可视区左上
        y_view = self._plot.viewRange()[1]
        self._text.setPos(x_left + 0.8, y_view[1] - (y_view[1] - y_view[0]) * 0.02)
        self._set_current(value)
