@echo off
chcp 65001 >nul
setlocal EnableExtensions
cd /d "%~dp0"

echo ========================================
echo   减速机测功机上位机（Phase 0 Mock）
echo ========================================
echo.

rem Prefer Windows Python launcher, then plain python
set "PY_CMD="
py -3 -c "import sys" >nul 2>&1
if not errorlevel 1 (
  set "PY_CMD=py -3"
) else (
  python -c "import sys" >nul 2>&1
  if not errorlevel 1 (
    set "PY_CMD=python"
  )
)

if not defined PY_CMD (
  echo [错误] 找不到 Python。
  echo 请先安装 Python 3.11 或更高版本，安装时勾选 “Add python.exe to PATH”。
  echo 下载：https://www.python.org/downloads/windows/
  echo.
  pause
  exit /b 1
)

echo 使用：%PY_CMD%
echo.

if not exist ".venv\Scripts\python.exe" (
  echo 正在创建虚拟环境 .venv ...
  %PY_CMD% -m venv .venv
  if errorlevel 1 (
    echo [错误] 创建虚拟环境失败。
    pause
    exit /b 1
  )
)

call ".venv\Scripts\activate.bat"
if errorlevel 1 (
  echo [错误] 无法激活虚拟环境。
  pause
  exit /b 1
)

echo 正在安装依赖（首次较慢，请稍候）...
python -m pip install -U pip
if errorlevel 1 (
  echo [错误] 升级 pip 失败。请检查网络后重试。
  pause
  exit /b 1
)

python -m pip install -r requirements.txt
if errorlevel 1 (
  echo [错误] 安装 requirements.txt 失败。请检查网络后重试。
  pause
  exit /b 1
)

python -m pip install -e .
if errorlevel 1 (
  echo [错误] 安装本程序失败。
  pause
  exit /b 1
)

echo.
echo 正在启动测功机上位机...
python -m dynamometer_host
set "EXITCODE=%ERRORLEVEL%"

if not "%EXITCODE%"=="0" (
  echo.
  echo [错误] 程序异常退出，代码 %EXITCODE%。
  pause
  exit /b %EXITCODE%
)

endlocal
