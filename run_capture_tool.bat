@echo off
title KTTC_FC Capture Tool - Chon Anh Minh Hoa
cd /d "%~dp0"
call .venv\Scripts\activate.bat
python capture_tool.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Da xay ra loi khi chay tool.
    pause
)
