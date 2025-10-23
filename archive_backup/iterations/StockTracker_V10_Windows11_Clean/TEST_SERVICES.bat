@echo off
title Stock Tracker - Service Health Check
color 0E

echo ================================================
echo    STOCK TRACKER SERVICE HEALTH CHECK
echo ================================================
echo.

echo Testing all services...
echo.

:: Test Main Backend
echo [1/6] Testing Main Backend (Port 8000)...
curl -s -o nul -w "Status: %%{http_code}\n" http://localhost:8000/health
if %errorlevel% equ 0 (
    echo [OK] Main Backend is responding
) else (
    echo [FAIL] Main Backend is not responding
)
echo.

:: Test ML Backend
echo [2/6] Testing ML Backend (Port 8002)...
curl -s -o nul -w "Status: %%{http_code}\n" http://localhost:8002/health
if %errorlevel% equ 0 (
    echo [OK] ML Backend is responding
) else (
    echo [FAIL] ML Backend is not responding
)
echo.

:: Test Document Analyzer
echo [3/6] Testing Document Analyzer (Port 8003)...
curl -s -o nul -w "Status: %%{http_code}\n" http://localhost:8003/health
if %errorlevel% equ 0 (
    echo [OK] Document Analyzer is responding
) else (
    echo [FAIL] Document Analyzer is not responding
)
echo.

:: Test Historical Data
echo [4/6] Testing Historical Data (Port 8004)...
curl -s -o nul -w "Status: %%{http_code}\n" http://localhost:8004/health
if %errorlevel% equ 0 (
    echo [OK] Historical Data is responding
) else (
    echo [FAIL] Historical Data is not responding
)
echo.

:: Test Backtesting
echo [5/6] Testing Backtesting (Port 8005)...
curl -s -o nul -w "Status: %%{http_code}\n" http://localhost:8005/health
if %errorlevel% equ 0 (
    echo [OK] Backtesting is responding
) else (
    echo [FAIL] Backtesting is not responding
)
echo.

:: Test Web Scraper
echo [6/6] Testing Web Scraper (Port 8006)...
curl -s -o nul -w "Status: %%{http_code}\n" http://localhost:8006/health
if %errorlevel% equ 0 (
    echo [OK] Web Scraper is responding
) else (
    echo [FAIL] Web Scraper is not responding
)
echo.

echo ================================================
echo    HEALTH CHECK COMPLETE
echo ================================================
echo.
pause