@echo off
cd /d "%~dp0"

echo ========================================
echo AI Multi-Agent Pipeline Installer
echo ========================================
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo Python was not found. Please install Python 3.10 or later first.
    pause
    exit /b 1
)

if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

call ".venv\Scripts\activate.bat"

echo.
echo Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Installing project dependencies...
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo Dependency installation failed. Please check your network and try again.
    pause
    exit /b 1
)

echo.
echo Installation completed.
echo You can run start_demo.bat to start the demo.
pause
