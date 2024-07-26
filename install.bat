@echo off
:: This script sets up a Python virtual environment and installs dependencies

:: Change to the bin directory
echo Changing directory to bin
cd export

:: Create a virtual environment named 'venv'
echo Creating virtual environment
python -m venv venv

:: Activate the virtual environment
echo Activating virtual environment
call venv\Scripts\activate

:: Install requirements from requirements.txt
echo Installing requirements
pip install -r requirements.txt

:: Deactivate the virtual environment
echo Deactivating virtual environment
deactivate

echo Setup complete
pause
