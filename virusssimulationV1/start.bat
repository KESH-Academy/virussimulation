@echo off
echo Checking for Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed. Please install Python 3.x from https://www.python.org/downloads/
    pause
    exit
)

echo Checking for required packages...
python -m pip install -r requirements.txt

echo Starting Virus Spread Simulation...
python virus_simulator.py

pause 