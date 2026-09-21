@echo off
REM ============================================
REM  LabMS One-Click Launcher (Windows)
REM  Starts the server AND opens Chrome.
REM ============================================

title LabMS - Laboratory Management System
cd /d "%~dp0"

echo.
echo ============================================
echo   Starting LabMS...
echo ============================================
echo.

REM --- Activate virtual environment ---
if exist "venv\Scripts\activate.bat" (
    echo [1/4] Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo [!] No venv found. Using system Python.
)

REM --- Install dependencies (first run only) ---
if not exist "venv\.installed" (
    echo [2/4] Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo [X] Failed to install dependencies.
        pause
        exit /b 1
    )
    echo done > venv\.installed
) else (
    echo [2/4] Dependencies already installed. Skipping.
)

REM --- Wait for server to be ready, then open Chrome ---
echo [3/4] Launching server and opening browser...
start "" /min cmd /c "timeout /t 3 >nul & start chrome http://localhost:5000"

REM --- Start the app (this blocks until you close it) ---
echo [4/4] Server running. Press CTRL+C to stop.
echo.
python app.py

echo.
echo ============================================
echo   LabMS has stopped.
echo ============================================
pause