@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

call :find_python
if not defined PYTHON_EXE (
    echo Python was not found on this PC. Attempting to install it automatically...
    call :install_python
    call :find_python
)

if not defined PYTHON_EXE (
    echo [ERROR] Automatic install failed.
    echo Please install Python 3.10+ manually from https://python.org/downloads and re-run this script.
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

REM ------------------------------------------------------------
:find_python
set "PYTHON_EXE="
py -3 --version >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_EXE=py"
    goto :eof
)
python --version >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_EXE=python"
)
goto :eof

REM ------------------------------------------------------------
:install_python
REM Try winget first (built into Windows 10 1709+ and Windows 11)
where winget >nul 2>&1
if not errorlevel 1 (
    winget install -e --id Python.Python.3.12 --scope user --accept-package-agreements --accept-source-agreements --silent
    if not errorlevel 1 goto :eof
)

REM Fall back to downloading the official installer directly
echo Downloading the official Python installer...
set "PY_INSTALLER=%TEMP%\python-installer.exe"
powershell -NoProfile -Command "try { Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.14/python-3.12.14-amd64.exe' -OutFile '%PY_INSTALLER%' } catch { exit 1 }"
if not exist "%PY_INSTALLER%" (
    echo [ERROR] Could not download the Python installer. Check your internet connection.
    goto :eof
)
"%PY_INSTALLER%" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0
del "%PY_INSTALLER%" >nul 2>&1
REM Refresh PATH for the current process so py/python can be found without restarting
for /f "usebackq tokens=2,*" %%A in (`reg query "HKCU\Environment" /v Path 2^>nul`) do set "PATH=%%B;%PATH%"
goto :eof