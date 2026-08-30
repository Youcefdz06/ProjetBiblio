@echo off
REM ============================================================================
REM ProjetBiblio Pre-flight Check
REM Validates system requirements before running main launcher
REM ============================================================================

setlocal enabledelayedexpansion

echo Checking system requirements...

REM Check Windows version (require Windows 7+)
for /f "tokens=2 delims=[]" %%A in ('ver') do set "VERSION=%%A"
echo Windows version detected: %VERSION%

REM Check for Administrator rights (optional but recommended)
net session >nul 2>&1
if errorlevel 1 (
    echo [!] Note: Running without Administrator privileges
    echo    This may affect some installations. Running normally...
) else (
    echo [✓] Administrator privileges available
)

REM Check internet connection
ping -n 1 python.org >nul 2>&1
if errorlevel 1 (
    ping -n 1 8.8.8.8 >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] No internet connection detected
        echo Please connect to the internet and try again
        pause
        exit /b 1
    )
)
echo [✓] Internet connection available

REM Check disk space (need at least 500MB)
for /f %%A in ('wmic logicaldisk where name^="%SystemDrive%" get freespace ^| find /v "^"') do set "FREESPACE=%%A"
if %FREESPACE% lss 524288000 (
    echo [WARNING] Low disk space detected
)

REM Check for .NET Framework (some dependencies may need it)
reg query "HKLM\Software\Microsoft\NET Framework Setup\NDP\v4\Full" >nul 2>&1
if not errorlevel 1 (
    echo [✓] .NET Framework detected
)

echo.
echo All checks passed. Ready to launch ProjetBiblio.
echo.
pause
exit /b 0
