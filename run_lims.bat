@echo off
cd /d "%~dp0"
call venv\Scripts\activate.bat
start "" http://localhost:5000
flask run --host=0.0.0.0 --port=5000
