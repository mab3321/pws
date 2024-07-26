@echo off
:: This script changes the directory, activates the virtual environment, and runs automate.py

:: Change to the specified directory
echo Changing directory to the specified path
cd export || (
    echo Failed to change directory to export
    pause
    exit /b 1
)

:: Activate the virtual environment
echo Activating virtual environment
call venv\Scripts\activate || (
    echo Failed to activate virtual environment
    pause
    exit /b 1
)

:: Run the automate.py script and capture any error output
echo Running automate.py
python automate.py 2>error.log
if %errorlevel% neq 0 (
    echo automate.py script failed with error code %errorlevel%
    echo Error details:
    type error.log
    pause
    exit /b 1
)

:: Deactivate the virtual environment
echo Deactivating virtual environment
deactivate || (
    echo Failed to deactivate virtual environment
    pause
    exit /b 1
)


:: This script downloads the latest ChromeDriver, extracts it, and sets it up for use in the export directory.

:: Ensure the script is running with administrative privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Requesting administrative privileges...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

:: Define the export directory
set current_dir=%~dp0
set dest_dir=%current_dir%export

:: Create export directory if it doesn't exist
if not exist "%dest_dir%" (
    echo Creating export directory
    mkdir "%dest_dir%"
)

:: Retrieve the latest ChromeDriver version
for /f "delims=" %%i in ('powershell -NoLogo -NoProfile -Command "(Invoke-WebRequest -Uri 'https://chromedriver.storage.googleapis.com/LATEST_RELEASE').Content"') do set CHROME_DRIVER_VERSION=%%i

:: Download the corresponding ChromeDriver zip file
echo Downloading ChromeDriver version %CHROME_DRIVER_VERSION%
powershell -NoLogo -NoProfile -Command "Invoke-WebRequest -Uri 'https://chromedriver.storage.googleapis.com/%CHROME_DRIVER_VERSION%/chromedriver_win32.zip' -OutFile 'chromedriver_win32.zip'"

:: Extract the ChromeDriver executable
echo Extracting ChromeDriver
powershell -NoLogo -NoProfile -Command "Expand-Archive -Path 'chromedriver_win32.zip' -DestinationPath '%dest_dir%'"

:: Clean up the downloaded zip file
echo Cleaning up
del chromedriver_win32.zip

:: Set permissions
echo Setting permissions
icacls "%dest_dir%\chromedriver.exe" /grant Users:F /T

echo ChromeDriver setup complete in %dest_dir%
echo Script execution complete
pause
