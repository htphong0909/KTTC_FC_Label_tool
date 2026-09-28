@echo off
title KTTC_FC Capture Tool - Chon Anh Minh Hoa (Legacy)
cd /d "%~dp0"

set "PYTHON_EXE=python"
if exist "..\.venv\Scripts\python.exe" set "PYTHON_EXE=..\.venv\Scripts\python.exe"
if exist ".venv\Scripts\python.exe" set "PYTHON_EXE=.venv\Scripts\python.exe"

echo [*] Dang khoi chay Legacy Capture Tool...
"%PYTHON_EXE%" capture_tool.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [*] Da xay ra loi khi chay tool.
    pause
)
