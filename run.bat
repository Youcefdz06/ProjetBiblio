@echo off
setlocal
cd /d "%~dp0"

REM Try to find Python in PATH first
set "PYTHON_EXE="

for /f "delims=" %%I in ('where py 2^>nul') do if not defined PYTHON_EXE set "PYTHON_EXE=%%I"
for /f "delims=" %%I in ('where python 2^>nul') do if not defined PYTHON_EXE set "PYTHON_EXE=%%I"

REM If not found in PATH, show error
if not defined PYTHON_EXE (
    echo [ERROR] Python was not found in PATH.
    echo Install Python 3.10 or newer, then reopen this launcher.
    pause
    exit /b 1
)

"%PYTHON_EXE%" -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo Installing client dependency...
    "%PYTHON_EXE%" -m pip install -r requirements-client.txt
    if errorlevel 1 (
        echo [ERROR] Dependency installation failed.
        pause
        exit /b 1
    )
)

echo Starting ProjetBiblio...
"%PYTHON_EXE%" main.py
set "APP_EXIT_CODE=%errorlevel%"

if not "%APP_EXIT_CODE%"=="0" pause
exit /b %APP_EXIT_CODE%
