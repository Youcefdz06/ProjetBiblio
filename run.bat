@echo off
setlocal enabledelayedexpansion
color 0A
title ProjetBiblio - Loading...

REM ============================================================================
REM ProjetBiblio - Cross-Platform Launcher (Silent Auto-Setup)
REM Handles: Python installation, dependency setup, server/client startup
REM ============================================================================

cd /d "%~dp0"

REM Setup logging
set "LOG_FILE=%TEMP%\projetbiblio_setup.log"
(
    echo [%date% %time%] Starting ProjetBiblio launcher
) > "%LOG_FILE%"

REM Configuration
set "PYTHON_VERSION=3.12.14"
set "PYTHON_URL=https://www.python.org/ftp/python/3.12.14/python-3.12.14-amd64.exe"
set "MIN_PYTHON_VERSION=3.10"
set "RETRY_COUNT=3"
set "CURRENT_RETRY=0"

echo.
echo ============================================================================
echo  ProjetBiblio - Library Management System
echo ============================================================================
echo  Initializing environment...
echo.

REM Step 1: Find or install Python
:find_python_loop
call :find_python
if not defined PYTHON_EXE (
    call :install_python_auto
    if errorlevel 1 (
        echo [ERROR] Failed to setup Python after %RETRY_COUNT% attempts
        call :log_error "Python installation failed"
        call :show_error_details
        pause
        exit /b 1
    )
    call :find_python
)

if not defined PYTHON_EXE (
    echo [ERROR] Python still not found after installation
    call :log_error "Python not found in PATH after installation"
    pause
    exit /b 1
)

echo [✓] Python: !PYTHON_EXE!
call :log_info "Python found: !PYTHON_EXE!"

REM Step 2: Install dependencies (silent)
echo  Installing dependencies...
call :install_dependencies
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    call :log_error "Dependency installation failed"
    pause
    exit /b 1
)
echo [✓] Dependencies ready
call :log_info "Dependencies installed successfully"

REM Step 3: Start API server
echo  Starting API server...
call :start_server
if errorlevel 1 (
    echo [ERROR] Failed to start server
    call :log_error "Server startup failed"
    pause
    exit /b 1
)
echo [✓] API server running
call :log_info "Server started successfully"

REM Step 4: Launch client
echo  Launching terminal client...
echo.
title ProjetBiblio - Running
"%PYTHON_EXE%" main.py
set "APP_EXIT_CODE=!errorlevel!"

call :cleanup_server
call :log_info "Application closed with code !APP_EXIT_CODE!"

if not "!APP_EXIT_CODE!"=="0" (
    echo.
    echo [!] Application exited with code !APP_EXIT_CODE!
)

exit /b !APP_EXIT_CODE!

REM ============================================================================
REM ============================================================================
REM FUNCTIONS
REM ============================================================================
REM ============================================================================

:find_python
setlocal enabledelayedexpansion
set "PYTHON_EXE="

REM Try 'py' launcher (preferred on Windows)
py -3 --version >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_EXE=py"
    endlocal & set "PYTHON_EXE=!PYTHON_EXE!"
    exit /b 0
)

REM Try 'python' directly
python --version >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_EXE=python"
    endlocal & set "PYTHON_EXE=!PYTHON_EXE!"
    exit /b 0
)

REM Try common installation paths
for %%P in (
    "C:\Python312\python.exe"
    "C:\Python311\python.exe"
    "C:\Python310\python.exe"
    "%APPDATA%\Python\Python312\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
) do (
    if exist "%%P" (
        set "PYTHON_EXE=%%P"
        endlocal & set "PYTHON_EXE=!PYTHON_EXE!"
        exit /b 0
    )
)

endlocal
exit /b 1

:install_python_auto
setlocal enabledelayedexpansion

:retry_install
set /a CURRENT_RETRY+=1
if %CURRENT_RETRY% gtr %RETRY_COUNT% exit /b 1

echo.
echo  [Attempt %CURRENT_RETRY%/%RETRY_COUNT%] Installing Python %PYTHON_VERSION%...

REM Try winget (Windows 11 / Windows 10 22H2)
where winget >nul 2>&1
if not errorlevel 1 (
    call :log_info "Attempting installation via winget"
    winget install -e --id Python.Python.3.12 ^
        --scope user ^
        --accept-package-agreements ^
        --accept-source-agreements ^
        --silent >nul 2>&1
    
    if not errorlevel 1 (
        call :refresh_path
        exit /b 0
    )
    call :log_warn "winget installation failed, trying direct download"
)

REM Direct download from python.org
set "PY_INSTALLER=%TEMP%\python-setup-%RANDOM%.exe"
echo  Downloading Python from python.org (may take a moment)...

call :download_file "%PYTHON_URL%" "%PY_INSTALLER%"
if errorlevel 1 (
    call :log_error "Download failed on attempt %CURRENT_RETRY%"
    del "%PY_INSTALLER%" >nul 2>&1
    goto retry_install
)

if not exist "%PY_INSTALLER%" (
    call :log_error "Installer file not found after download"
    goto retry_install
)

echo  Installing...
"%PY_INSTALLER%" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0 >nul 2>&1

if errorlevel 1 (
    call :log_error "Installation failed on attempt %CURRENT_RETRY%"
    del "%PY_INSTALLER%" >nul 2>&1
    goto retry_install
)

del "%PY_INSTALLER%" >nul 2>&1
call :refresh_path
call :log_info "Python installed successfully via direct download"
exit /b 0

:download_file
setlocal enabledelayedexpansion
set "URL=%~1"
set "OUTPUT=%~2"

REM Use PowerShell for robust downloads with timeout
powershell -NoProfile -Command ^
    "try { ^
        $ProgressPreference = 'SilentlyContinue'; ^
        Invoke-WebRequest -Uri '%URL%' -OutFile '%OUTPUT%' ^
            -TimeoutSec 120 -ErrorAction Stop; ^
        exit 0 ^
    } catch { ^
        exit 1 ^
    }" >nul 2>&1

endlocal & exit /b %errorlevel%

:refresh_path
setlocal enabledelayedexpansion
for /f "usebackq tokens=2,*" %%A in (`reg query "HKCU\Environment" /v Path 2^>nul`) do (
    set "NEWPATH=%%B"
    set "PATH=!NEWPATH!;%PATH%"
)

REM Also check system PATH
for /f "usebackq tokens=2,*" %%A in (`reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path 2^>nul`) do (
    set "SYSPATH=%%B"
    set "PATH=!PATH!;!SYSPATH!"
)

endlocal & set "PATH=%PATH%"
exit /b 0

:install_dependencies
setlocal enabledelayedexpansion

REM Check for local package cache first
set "CACHE_DIR=%~dp0.projetbiblio-cache"
if exist "%CACHE_DIR%\packages" (
    echo  (using cached packages)
    "%PYTHON_EXE%" -m pip install --quiet --disable-pip-version-check ^
        --no-index --find-links "%CACHE_DIR%\packages" -r requirements.txt 2>nul
    if not errorlevel 1 (
        exit /b 0
    )
    echo  (cache incomplete, downloading from internet)
)

REM Fallback to online installation
"%PYTHON_EXE%" -m pip install --quiet --disable-pip-version-check -r requirements.txt
if errorlevel 1 (
    REM Try again with upgrade
    "%PYTHON_EXE%" -m pip install --quiet --upgrade pip setuptools wheel >nul 2>&1
    "%PYTHON_EXE%" -m pip install --quiet --disable-pip-version-check -r requirements.txt
    if errorlevel 1 exit /b 1
)
exit /b 0

:start_server
set "SERVER_LOG=%TEMP%\projetbiblio_server.log"

REM Start in background
start /b "ProjetBiblio API Server" "%PYTHON_EXE%" api.py > "%SERVER_LOG%" 2>&1

REM Wait for startup
timeout /t 2 /nobreak >nul

REM Verify server started
tasklist /FI "WINDOWTITLE eq ProjetBiblio API Server" 2>nul | find /I "cmd" >nul
if errorlevel 1 (
    REM Check log for errors
    if exist "%SERVER_LOG%" (
        for /f %%A in ("%SERVER_LOG%") do set "LOG_SIZE=%%~zA"
        if !LOG_SIZE! gtr 0 (
            call :log_error "Server startup failed. Log:"
            type "%SERVER_LOG%" >> "%LOG_FILE%"
        )
    )
    exit /b 1
)

exit /b 0

:cleanup_server
taskkill /FI "WINDOWTITLE eq ProjetBiblio API Server" /T /F >nul 2>&1
timeout /t 1 /nobreak >nul
exit /b 0

:log_info
echo [INFO] %~1 >> "%LOG_FILE%"
exit /b 0

:log_warn
echo [WARN] %~1 >> "%LOG_FILE%"
exit /b 0

:log_error
echo [ERROR] %~1 >> "%LOG_FILE%"
exit /b 0

:show_error_details
echo.
echo ============================================================================
echo  TROUBLESHOOTING
echo ============================================================================
echo  • Check internet connection
echo  • Ensure Windows is updated
echo  • Disable antivirus temporarily
echo  • Run as Administrator if needed
echo  • Check log file: %LOG_FILE%
echo.
exit /b 0

    if not db_url:
        print('  - TURSO_DATABASE_URL')
    if not auth_token:
        print('  - TURSO_AUTH_TOKEN')
    print('[ACTION] Please edit .env and add these credentials')
    exit(1)

print('[SUCCESS] Environment variables validated')
exit(0)
" >nul 2>&1

if errorlevel 1 (
    echo [ERROR] Environment validation failed. Please check your .env file.
    exit /b 1
)
goto :eof