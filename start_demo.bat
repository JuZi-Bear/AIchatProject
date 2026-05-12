@echo off
cd /d "%~dp0"

echo ========================================
echo AI Multi-Agent Pipeline Demo
echo ========================================
echo.
echo 1. Start CLI Demo: python graph_demo.py
echo 2. Start Web UI: streamlit run webui.py
echo 3. Exit
echo.

set /p choice=Please choose 1-3: 

if "%choice%"=="1" (
    echo.
    echo Starting CLI Demo...
    python graph_demo.py
    pause
    exit /b
)

if "%choice%"=="2" (
    echo.
    echo Starting Web UI...
    streamlit run webui.py
    pause
    exit /b
)

if "%choice%"=="3" (
    exit /b
)

echo Invalid choice. Please run start_demo.bat again.
pause
