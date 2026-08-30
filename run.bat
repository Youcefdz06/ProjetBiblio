@echo off
setlocal
cd /d "%~dp0"

set PYTHON_EXE=C:\Users\HP\AppData\Local\Python\pythoncore-3.14-64\python.exe

if not exist "%PYTHON_EXE%" (
    echo [ERROR] Python was not found at %PYTHON_EXE%
    pause
    exit /b 1
)

if not exist ".env" (
    echo [ERROR] The .env file is missing.
    echo Copy .env.example to .env and add your Turso URL and auth token.
    pause
    exit /b 1
)

"%PYTHON_EXE%" -c "import dotenv; import turso_serverless" >nul 2>&1
if errorlevel 1 (
    echo Installing Python dependencies...
    "%PYTHON_EXE%" -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Dependency installation failed.
        pause
        exit /b 1
    )
)

echo Starting ProjetBiblio...
"%PYTHON_EXE%" main.py
set "APP_EXIT_CODE=%errorlevel%"

if not "%APP_EXIT_CODE%"=="0" (
    echo.
    echo [ERROR] ProjetBiblio stopped with code %APP_EXIT_CODE%.
    pause
)

exit /b %APP_EXIT_CODE%
