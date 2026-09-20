# 减速机测功机上位机（Phase 0 — Mock UI）

中文 Windows 桌面测功上位机骨架。本阶段使用 **Mock 设备** 驱动实时曲线与采样，无需真实 RS485 硬件。

技术栈：Python 3.11+ · PySide6 · pyqtgraph

## Windows 运行（开发）

```bat
cd dynamometer-host
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
python -m dynamometer_host
```

或：

```bat
dynamometer-host
```

## Windows 双击 exe（打包）

GitHub Actions 工作流 `.github/workflows/build-windows-exe.yml` 在 `windows-latest` 上用 PyInstaller 生成 `测功机上位机.exe`，并打成 `测功机上位机-Mock.zip`。

本地 Windows 打包：

```bat
cd dynamometer-host
pip install -r requirements.txt -r requirements-build.txt
pip install -e .
pyinstaller build_exe.spec --noconfirm --clean
powershell -File scripts\package_windows_zip.ps1
```
## Linux / 开发机

```bash
cd dynamometer-host
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
python -m dynamometer_host
```

无显示环境可做冒烟检查：

```bash
python scripts/smoke_check.py
pytest -q
```

截图（需可用 DISPLAY）：

```bash
python scripts/capture_screenshot.py
```

## 包结构

```
src/dynamometer_host/
  ui/          # 主窗口与六大页签
  devices/     # IServo / ITorque / IBrake / Mock*
  core/        # 功率效率计算、采样存储
```

## Phase 0 说明

- **加载 / 卸载** 只驱动 `MockServo`
- 制动器励磁 % 走独立 `MockBrake` ← `MockAnalogOutput`，与加载键无关
- 真实 Modbus / 自动加载序列 / 打印引擎属后续阶段
