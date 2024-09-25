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

:: Activate the virtual environment
echo Activating virtual environment
call .venv\Scripts\activate
:: Change to the desired directory
cd /d "export"

:: Uninstall the existing chromedriver_py package
echo Uninstalling chromedriver_py...
pip uninstall -y chromedriver_py

:: Reinstall the chromedriver_py package
echo Installing chromedriver_py...
pip install chromedriver_py

echo ChromeDriver setup complete
pause
