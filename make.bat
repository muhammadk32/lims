@echo off
REM ============================================
REM  LabMS ? Windows task runner
REM  Usage: make.bat <command>
REM ============================================
setlocal
cd /d "%~dp0"

if "%~1"=="" goto help
if /I "%~1"=="help" goto help
if /I "%~1"=="install" goto install
if /I "%~1"=="run" goto run
if /I "%~1"=="test" goto test
if /I "%~1"=="seed" goto seed
if /I "%~1"=="backup" goto backup
if /I "%~1"=="migrate" goto migrate
if /I "%~1"=="logs" goto logs
if /I "%~1"=="clean" goto clean
if /I "%~1"=="docker-build" goto docker-build
if /I "%~1"=="docker-up" goto docker-up
if /I "%~1"=="docker-down" goto docker-down
if /I "%~1"=="docker-logs" goto docker-logs
if /I "%~1"=="docker-shell" goto docker-shell

echo Unknown command: %~1
goto help

:help
echo LabMS - Available commands:
echo   make install         Install dev dependencies
echo   make run             Start the dev server (port 5000)
echo   make test            Run pytest
echo   make seed            Seed sample data
echo   make backup          Create a timestamped DB backup
echo   make migrate         Run database migrations (upgrade)
echo   make logs            Tail application log
echo   make clean           Remove caches and .pyc files
echo.
echo   make docker-build    Build the Docker image
echo   make docker-up       Start the container (port 8000)
echo   make docker-down     Stop the container
echo   make docker-logs     Tail container logs
echo   make docker-shell    Open a shell inside the container
goto :eof

:install
pip install -r requirements.txt
goto :eof

:run
python app.py
goto :eof

:test
pytest
goto :eof

:seed
python -m scripts.seed_data --patients 50 --orders 200
goto :eof

:backup
python -m scripts.backup
goto :eof

:migrate
flask --app app db upgrade
goto :eof

:logs
powershell -NoProfile -Command "Get-Content logs\app.log -Wait -Tail 40"
goto :eof

:clean
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc 2>nul
if exist .pytest_cache rd /s /q .pytest_cache
echo Cleaned.
goto :eof

:docker-build
docker compose build
goto :eof

:docker-up
docker compose up -d
goto :eof

:docker-down
docker compose down
goto :eof

:docker-logs
docker compose logs -f
goto :eof

:docker-shell
docker compose exec web /bin/bash
goto :eof
