@echo off
title KTTC_FC - Legacy Video Cut Tool
cd /d "%~dp0"

set "PYTHON_EXE=python"
if exist "..\.venv\Scripts\python.exe" set "PYTHON_EXE=..\.venv\Scripts\python.exe"
if exist ".venv\Scripts\python.exe" set "PYTHON_EXE=.venv\Scripts\python.exe"

echo [*] Dang khoi chay Legacy Video Cut Tool (Tkinter)...
"%PYTHON_EXE%" catvideo.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [*] Da xay ra loi khi chay tool.
    pause
)
