@echo off
setlocal
cd /d "%~dp0"

title KTTC_FC - Video Labeler and Slicer

echo =======================================================
echo    KTTC_FC - Video Labeler and Slicer Tool
echo =======================================================
echo.

set "PYTHON_EXE=python"
if exist ".venv\Scripts\python.exe" set "PYTHON_EXE=.venv\Scripts\python.exe"

echo [*] Starting Desktop Application...
"%PYTHON_EXE%" -m tools.video_labeler.launcher

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [*] Application exited with code %ERRORLEVEL%.
)

echo.
echo [*] Application closed.
pause
