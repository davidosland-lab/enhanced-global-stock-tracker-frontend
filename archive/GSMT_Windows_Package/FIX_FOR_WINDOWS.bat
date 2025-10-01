@echo off
REM ============================================
REM Fix for Windows - Updates dashboard to use localhost
REM ============================================

echo.
echo Applying Windows localhost fix...
echo.

REM Backup original dashboard
if exist simple_working_dashboard.html.bak (
    echo Backup already exists
) else (
    copy simple_working_dashboard.html simple_working_dashboard.html.bak
    echo Created backup of original dashboard
)

REM Use the Windows-fixed version
if exist simple_working_dashboard_windows.html (
    copy /Y simple_working_dashboard_windows.html simple_working_dashboard.html
    echo Dashboard updated to use localhost:8002
) else (
    echo ERROR: simple_working_dashboard_windows.html not found
    pause
    exit /b 1
)

echo.
echo Fix applied successfully!
echo Please refresh your browser (press F5)
echo.
pause