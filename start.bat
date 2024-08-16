@echo off
:: This script starts in the current directory, changes to 'export', activates the virtual environment, and runs app.py

:: Ensure the script starts in the current directory (the directory where this batch file is located)
cd /d %~dp0

:: Change to the 'export' directory within the current directory
echo Changing directory to 'export'
cd export || (
    echo Failed to change directory to 'export'
    pause
    exit /b 1
)

:: Activate the virtual environment
echo Activating virtual environment
call .venv\Scripts\activate || (
    echo Failed to activate virtual environment
    pause
    exit /b 1
)

:: Run the app.py script
echo Running app.py
python app.py
if %errorlevel% neq 0 (
    echo app.py script failed with error code %errorlevel%
    pause
    exit /b 1
)

:: Deactivate the virtual environment after app.py has finished
echo Deactivating virtual environment
deactivate
