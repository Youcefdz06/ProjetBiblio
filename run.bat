@echo off
setlocal
cd /d "%~dp0"

REM Try to find Python in PATH first
for /f "tokens=*" %%i in ('where python 2^>nul') do set "PYTHON_EXE=%%i"

REM If not found in PATH, show error
if not defined PYTHON_EXE (
    echo [ERROR] Python was not found. Please install Python and add it to PATH.
    echo Visit: https://www.python.org/downloads/
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
