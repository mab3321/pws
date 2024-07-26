@echo off
:: This script downloads the latest ChromeDriver, extracts it, and sets it up for use.

:: Retrieve the latest ChromeDriver version
for /f "delims=" %%i in ('powershell -NoLogo -NoProfile -Command "(Invoke-WebRequest -Uri 'https://chromedriver.storage.googleapis.com/LATEST_RELEASE').Content"') do set CHROME_DRIVER_VERSION=%%i

:: Download the corresponding ChromeDriver zip file
echo Downloading ChromeDriver version %CHROME_DRIVER_VERSION%
powershell -NoLogo -NoProfile -Command "Invoke-WebRequest -Uri 'https://chromedriver.storage.googleapis.com/%CHROME_DRIVER_VERSION%/chromedriver_win32.zip' -OutFile 'chromedriver_win32.zip'"

:: Extract the ChromeDriver executable
echo Extracting ChromeDriver
powershell -NoLogo -NoProfile -Command "Expand-Archive -Path 'chromedriver_win32.zip' -DestinationPath '.'"

:: Clean up the downloaded zip file
echo Cleaning up
del chromedriver_win32.zip

:: Move ChromeDriver to a directory in the PATH
echo Moving ChromeDriver to C:\Windows\System32
move /y chromedriver.exe C:\Windows\System32\chromedriver.exe

:: Set permissions
echo Setting permissions
icacls C:\Windows\System32\chromedriver.exe /grant Users:F /T

echo ChromeDriver setup complete
pause
