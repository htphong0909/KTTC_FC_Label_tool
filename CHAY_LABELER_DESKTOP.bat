@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

title KTTC_FC - Video Labeler and Slicer

echo =======================================================
echo    KTTC_FC - Video Labeler and Slicer Tool
echo =======================================================
echo.

if exist ".venv\Scripts\python.exe" (
    set "PYTHON_EXE=.venv\Scripts\python.exe"
) else (
    set "PYTHON_EXE=python"
)

:: Kiểm tra thư viện flask, nếu thiếu sẽ tự động cài đặt
"%PYTHON_EXE%" -c "import flask" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [*] Phát hiện thiếu thư viện cần thiết (Flask). Đang tự động cài đặt từ requirements.txt...
    "%PYTHON_EXE%" -m pip install -r requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        echo [!] Cài đặt thư viện thất bại. Vui lòng kiểm tra kết nối mạng hoặc thử chạy:
        echo     "%PYTHON_EXE%" -m pip install -r requirements.txt
        echo.
        pause
        exit /b 1
    )
    echo [*] Cài đặt hoàn tất!
    echo.
)

echo [*] Clearing port 5055 and starting Desktop Application...
"%PYTHON_EXE%" -m tools.video_labeler.launcher

echo.
echo [*] Application closed.
pause
