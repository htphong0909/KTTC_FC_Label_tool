@echo off
setlocal
cd /d "%~dp0"

title KTTC_FC - Tool Chup Anh 3 Moc S-Key-E (Legacy)

echo =======================================================
echo    KTTC_FC - Tool Chup Anh 3 Moc S-Key-E (Legacy)
echo =======================================================
echo.

set "PYTHON_EXE=python"
if exist ".venv\Scripts\python.exe" set "PYTHON_EXE=.venv\Scripts\python.exe"

echo [*] Dang khoi chay Tool Chup Anh...
"%PYTHON_EXE%" legacy\capture_tool.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [*] Da xay ra loi khi chay tool.
    pause
)
