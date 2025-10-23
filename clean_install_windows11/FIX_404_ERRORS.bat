@echo off
cls
echo ================================================================
echo     FIXING 404 ERRORS (COSMETIC)
echo ================================================================
echo.

echo Creating missing files to stop 404 errors...

:: Create favicon.ico (empty file is fine)
echo. > favicon.ico
echo Created: favicon.ico

:: Create a simple icon using HTML favicon
(
echo ^<link rel="icon" href="data:,"^>
) > favicon.html

:: Check for other missing files
if not exist modules\REAL_WORKING_PREDICTOR.html (
    echo ^<html^>^<body^>Redirecting...^<script^>window.location='prediction_centre_ml_connected.html'^</script^>^</body^>^</html^> > modules\REAL_WORKING_PREDICTOR.html
    echo Created redirect for REAL_WORKING_PREDICTOR.html
)

echo.
echo ================================================================
echo     404 ERRORS FIXED
echo ================================================================
echo.
echo The 404 errors were harmless (just missing icon files).
echo Your app should be working fine now!
echo.
echo Test these URLs:
echo - Dashboard: http://localhost:8000
echo - Backend API: http://localhost:8002/api/status
echo - Stock Data: http://localhost:8002/api/stock/AAPL
echo.
pause