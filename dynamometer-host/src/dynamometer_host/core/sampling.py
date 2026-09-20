"""采样会话存储（Phase 0：内存表 + CSV 导出桩）。"""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass, fields
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


@dataclass
class SampleRecord:
    index: int
    timestamp: str
    torque_nm: float
    speed_rpm: float
    p_out_w: float
    temperature_c: float
    angle_deg: float
    voltage_v: float
    current_a: float
    p_in_w: float
    efficiency_pct: float | None
    brake_percent: float


class SampleStore:
    """会话内采样表。"""

    def __init__(self) -> None:
        self._rows: list[SampleRecord] = []

    def __len__(self) -> int:
        return len(self._rows)

    @property
    def rows(self) -> list[SampleRecord]:
        return list(self._rows)

    def clear(self) -> None:
        self._rows.clear()

    def add(
        self,
        *,
        torque_nm: float,
        speed_rpm: float,
        p_out_w: float,
        temperature_c: float,
        angle_deg: float,
        voltage_v: float,
        current_a: float,
        p_in_w: float,
        efficiency_pct: float | None,
        brake_percent: float,
    ) -> SampleRecord:
        rec = SampleRecord(
            index=len(self._rows) + 1,
            timestamp=datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
            torque_nm=torque_nm,
            speed_rpm=speed_rpm,
            p_out_w=p_out_w,
            temperature_c=temperature_c,
            angle_deg=angle_deg,
            voltage_v=voltage_v,
            current_a=current_a,
            p_in_w=p_in_w,
            efficiency_pct=efficiency_pct,
            brake_percent=brake_percent,
        )
        self._rows.append(rec)
        return rec

    def export_csv(self, path: str | Path, rows: Iterable[SampleRecord] | None = None) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = list(rows) if rows is not None else self._rows
        fieldnames = [f.name for f in fields(SampleRecord)]
        with path.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                writer.writerow(asdict(row))
        return path
