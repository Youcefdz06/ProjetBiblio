@echo off
REM ============================================================================
REM ProjetBiblio - Portable Bundle Installer
REM Creates a self-contained package that works offline
REM Run this ONCE to prepare the system, then use run.bat normally
REM ============================================================================

setlocal enabledelayedexpansion
color 0E
title ProjetBiblio - Bundle Setup

cd /d "%~dp0"

echo.
echo ============================================================================
echo  ProjetBiblio Portable Bundle Setup
echo ============================================================================
echo.
echo This script will:
echo  1. Create a local dependencies cache
echo  2. Download Python and all packages
echo  3. Prepare for offline installation
echo.
echo This process may take 5-10 minutes. Running only ONCE is needed.
echo.

REM Create cache directory
set "CACHE_DIR=%~dp0.projetbiblio-cache"
if not exist "%CACHE_DIR%" (
    mkdir "%CACHE_DIR%"
    echo [✓] Created cache directory: %CACHE_DIR%
) else (
    echo [✓] Cache directory already exists
)

REM Download Python
set "PYTHON_INSTALLER=%CACHE_DIR%\python-3.12.14-amd64.exe"
if not exist "%PYTHON_INSTALLER%" (
    echo.
    echo Downloading Python 3.12.14 (ISO file, may take 1-2 minutes)...
    powershell -NoProfile -Command ^
        "$ProgressPreference = 'SilentlyContinue'; ^
        try { ^
            Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.14/python-3.12.14-amd64.exe' ^
                -OutFile '%PYTHON_INSTALLER%' -TimeoutSec 300 -ErrorAction Stop; ^
            Write-Host '[OK] Python downloaded'; ^
            exit 0 ^
        } catch { ^
            Write-Host '[ERROR] Download failed'; ^
            exit 1 ^
        }" >nul 2>&1
    
    if errorlevel 1 (
        echo [ERROR] Failed to download Python
        echo Check internet connection and try again
        pause
        exit /b 1
    )
) else (
    echo [✓] Python already cached
)

REM Download Python packages
echo.
echo Downloading dependencies (checking what's needed)...
py -3 --version >nul 2>&1
if not errorlevel 1 (
    echo [✓] Python found locally, downloading packages...
    py -m pip download -r requirements.txt -d "%CACHE_DIR%\packages" --quiet --disable-pip-version-check 2>nul
    if errorlevel 1 (
        echo [!] Could not pre-cache packages (this is optional)
        echo     Packages will be downloaded when needed
    ) else (
        echo [✓] Packages cached successfully
    )
) else (
    echo [!] Python not yet installed locally
    echo     Packages will be downloaded after Python installation
)

REM Create info file
(
    echo Bundle created: %date% %time%
    echo Python installer: %PYTHON_INSTALLER%
    echo Packages cache: %CACHE_DIR%\packages
    echo.
    echo To use offline:
    echo  1. Copy the entire project folder to offline PC
    echo  2. Run run.bat on the offline PC
    echo  3. The cached installer and packages will be used
) > "%CACHE_DIR%\INFO.txt"

echo.
echo ============================================================================
echo [✓] Bundle prepared successfully!
echo.
echo Cache directory: %CACHE_DIR%
echo Total size: ~500-800 MB
echo.
echo You can now:
echo  - Copy this entire folder to other PCs (portable)
echo  - Use on offline machines
echo  - Share with friends
echo.
echo Next: Run run.bat to start ProjetBiblio
echo ============================================================================
echo.
pause
exit /b 0
