@echo off
echo ================================================================================
echo                    CHECKING YOUR STOCK TRACKER FILES
echo ================================================================================
echo.
echo Current Directory:
cd
echo.
echo ================================================================================
echo Main HTML Files:
echo ================================================================================
dir /b *.html 2>nul
if errorlevel 1 echo No HTML files found in root directory
echo.
echo ================================================================================
echo Module Files:
echo ================================================================================
if exist "modules" (
    cd modules
    dir /b *.html 2>nul
    cd ..
) else (
    echo modules folder not found!
)
echo.
echo ================================================================================
echo Critical Files Check:
echo ================================================================================
if exist "index.html" (echo [OK] index.html found) else (echo [MISSING] index.html)
if exist "backend.py" (echo [OK] backend.py found) else (echo [MISSING] backend.py)
if exist "modules\historical_data_manager.html" (echo [OK] Historical Data Manager found) else (echo [MISSING] Historical Data Manager)
if exist "modules\prediction_centre_phase4.html" (echo [OK] Prediction Centre found) else (echo [MISSING] Prediction Centre)
echo.
pause