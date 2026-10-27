@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo ==========================================
echo  LIMS Install
echo  Folder: %CD%
echo ==========================================

echo [1/6] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Install 3.11 or 3.12 from python.org
    echo Check "Add Python to PATH" during install.
    pause & exit /b 1
)
python --version

echo [2/6] Checking database...
if not exist "instance\database.db" (
    echo [ERROR] instance\database.db missing. Re-export from old PC.
    pause & exit /b 1
)
for %%A in ("instance\database.db") do echo  DB size: %%~zA bytes

echo [3/6] Creating virtual environment...
if exist venv rmdir /S /Q venv
python -m venv venv
if errorlevel 1 ( echo [ERROR] venv failed & pause & exit /b 1 )

echo [4/6] Installing packages (2-5 min)...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt
if errorlevel 1 ( echo [ERROR] pip install failed & pause & exit /b 1 )

echo [5/6] Verifying DB...
python -c "import sqlite3; c=sqlite3.connect('instance/database.db'); print('Patients:', c.execute('SELECT COUNT(*) FROM patients').fetchone()[0])"

echo [6/6] Creating run_lims.bat...
(
    echo @echo off
    echo cd /d "%%~dp0"
    echo call venv\Scripts\activate.bat
    echo start "" http://localhost:5000
    echo flask run --host=0.0.0.0 --port=5000
) > run_lims.bat

echo.
echo DONE. Run run_lims.bat to start the app.
pause
