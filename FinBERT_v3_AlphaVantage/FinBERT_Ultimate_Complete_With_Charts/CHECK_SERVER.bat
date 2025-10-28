@echo off
echo Checking what's running on port 5000...
echo.

netstat -an | findstr :5000

echo.
echo Testing server endpoints...
echo.

curl http://localhost:5000 2>nul
if errorlevel 1 (
    echo.
    echo No server response. Server may not be running.
) else (
    echo.
    echo Server is responding.
)

echo.
pause