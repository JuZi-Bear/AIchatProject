@echo off
cd /d "%~dp0"

if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
)

where python >nul 2>nul
if errorlevel 1 (
    echo Python was not found. Please install Python or create .venv first.
    pause
    exit /b 1
)

python --version >nul 2>nul
if errorlevel 1 (
    echo Python exists but cannot run. The virtual environment may be broken.
    echo Please recreate .venv, then install dependencies again.
    pause
    exit /b 1
)

python -c "import streamlit, rich, langgraph, openai, dotenv, yaml" >nul 2>nul
if errorlevel 1 (
    echo Project dependencies are missing or incomplete.
    echo Please run install.bat first, then start this script again.
    pause
    exit /b 1
)

echo ========================================
echo AI Multi-Agent Pipeline Demo
echo ========================================
echo.
echo 1. Start CLI Demo: python graph_demo.py
echo 2. Start Web UI: python -m streamlit run webui.py
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
    python -m streamlit run webui.py
    pause
    exit /b
)

if "%choice%"=="3" (
    exit /b
)

echo Invalid choice. Please run start_demo.bat again.
pause
