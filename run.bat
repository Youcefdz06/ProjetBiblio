@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python was not found. Install Python 3.10 or newer.
    pause
    exit /b 1
)

if not exist ".env" (
    echo [ERROR] The .env file is missing.
    echo Copy .env.example to .env and add your Turso URL and auth token.
    pause
    exit /b 1
)

py -c "import dotenv; import turso_serverless" >nul 2>&1
if errorlevel 1 (
    echo Installing Python dependencies...
    py -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Dependency installation failed.
        pause
        exit /b 1
    )
)

echo Starting ProjetBiblio...
py main.py
set "APP_EXIT_CODE=%errorlevel%"

if not "%APP_EXIT_CODE%"=="0" (
    echo.
    echo [ERROR] ProjetBiblio stopped with code %APP_EXIT_CODE%.
    pause
)

exit /b %APP_EXIT_CODE%
