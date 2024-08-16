@echo off
:: This script starts in the current directory, changes to 'export', clears the 'multi' folder, activates the virtual environment, and runs app.py

:: Ensure the script starts in the current directory (the directory where this batch file is located)
cd /d %~dp0

:: Change to the 'export' directory within the current directory
echo Changing directory to 'export'
cd export || (
    echo Failed to change directory to 'export'
    pause
    exit /b 1
)

:: Remove the contents of the 'multi' folder
echo Clearing the 'multi' folder
if exist multi (
    echo Deleting all files in 'multi' folder
    del /f /s /q multi\*.* >nul 2>&1

    echo Removing subdirectories in 'multi' folder
    for /d %%x in (multi\*) do rd /s /q "%%x" >nul 2>&1

    echo 'multi' folder contents cleared
) else (
    echo 'multi' folder does not exist, skipping deletion
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
