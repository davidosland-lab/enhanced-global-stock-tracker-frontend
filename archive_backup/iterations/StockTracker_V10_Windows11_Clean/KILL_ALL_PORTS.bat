@echo off
echo ========================================
echo Killing all processes on ports 8000-8005
echo ========================================
echo.

REM Kill all Python processes first
echo Killing all Python processes...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM pythonw.exe 2>nul
timeout /t 2 >nul

REM Kill specific ports
echo Freeing port 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000"') do taskkill /PID %%a /F 2>nul

echo Freeing port 8002...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8002"') do taskkill /PID %%a /F 2>nul

echo Freeing port 8003...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8003"') do taskkill /PID %%a /F 2>nul

echo Freeing port 8004...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8004"') do taskkill /PID %%a /F 2>nul

echo Freeing port 8005...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8005"') do taskkill /PID %%a /F 2>nul

echo.
echo All ports cleared!
echo.
pause