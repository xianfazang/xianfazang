# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec — Windows one-file GUI build for Phase 0 Mock UI."""

from __future__ import annotations

from pathlib import Path

from PyInstaller.utils.hooks import collect_all, collect_submodules

block_cipher = None

ROOT = Path(SPECPATH).resolve()
SRC = ROOT / "src"

datas: list = []
binaries: list = []
hiddenimports: list = [
    "dynamometer_host",
    "dynamometer_host.ui",
    "dynamometer_host.ui.main_window",
    "dynamometer_host.ui.realtime_page",
    "dynamometer_host.ui.charts",
    "dynamometer_host.ui.styles",
    "dynamometer_host.ui.stub_pages",
    "dynamometer_host.devices",
    "dynamometer_host.core",
    "dynamometer_host.smoke",
]

for pkg in ("PySide6", "pyqtgraph", "numpy"):
    pkg_datas, pkg_binaries, pkg_hidden = collect_all(pkg)
    datas += pkg_datas
    binaries += pkg_binaries
    hiddenimports += pkg_hidden

hiddenimports += collect_submodules("dynamometer_host")

a = Analysis(
    [str(SRC / "dynamometer_host" / "__main__.py")],
    pathex=[str(SRC)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="测功机上位机",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI — no black console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
