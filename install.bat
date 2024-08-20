@echo off
:: This script sets up a Python virtual environment and installs dependencies
:: Ensure the script starts in the current directory (the directory where this batch file is located)
cd /d %~dp0

:: Change to the 'export' directory within the current directory
echo Changing directory to 'export'
cd export || (
    echo Failed to change directory to 'export'
    pause
    exit /b 1
)

:: Create a virtual environment named 'venv'
echo Creating virtual environment
py -3.9 -m venv .venv

:: Activate the virtual environment
echo Activating virtual environment
call .venv\Scripts\activate

:: Install requirements from requirements.txt
echo Installing requirements
pip install -r requirements.txt

:: Deactivate the virtual environment
echo Deactivating virtual environment
deactivate

echo Setup complete
pause
