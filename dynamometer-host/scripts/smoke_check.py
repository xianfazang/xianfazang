#!/usr/bin/env python3
"""无界面冒烟入口（亦可 ``python -m dynamometer_host --smoke``）。"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dynamometer_host.smoke import run_smoke  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(run_smoke())
