@echo off
setlocal
cd /d "%~dp0"

title KTTC_FC - Tool Cat Video Desktop Tkinter (Legacy)

echo =======================================================
echo    KTTC_FC - Tool Cat Video Desktop Tkinter (Legacy)
echo =======================================================
echo.

set "PYTHON_EXE=python"
if exist ".venv\Scripts\python.exe" set "PYTHON_EXE=.venv\Scripts\python.exe"

echo [*] Dang khoi chay Tool Cat Video Desktop...
"%PYTHON_EXE%" legacy\catvideo.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [*] Da xay ra loi khi chay tool.
    pause
)
