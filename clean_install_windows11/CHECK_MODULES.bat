@echo off
cls
echo ================================================================
echo     MODULE FILE CHECKER
echo ================================================================
echo.

echo Checking which module files actually exist...
echo.

echo PREDICTION CENTRE files:
echo ------------------------
dir /b modules\prediction*.html 2>nul
if errorlevel 1 echo NO PREDICTION FILES FOUND!

echo.
echo DOCUMENT ANALYSER files:
echo ------------------------
dir /b modules\document*.html 2>nul
if errorlevel 1 echo NO DOCUMENT FILES FOUND!

echo.
echo ML TRAINING files:
echo ------------------------
dir /b modules\ml_training*.html 2>nul
if errorlevel 1 echo NO ML TRAINING FILES FOUND!

echo.
echo TECHNICAL ANALYSIS files:
echo ------------------------
dir /b modules\technical*.html 2>nul
if errorlevel 1 echo NO TECHNICAL FILES FOUND!

echo.
echo ALL MODULE FILES:
echo ------------------------
dir /b modules\*.html

echo.
echo ================================================================
echo     CHECKING INDEX.HTML REFERENCES
echo ================================================================
echo.

echo Current module mappings in index.html:
findstr /C:"predictor':" index.html
findstr /C:"documents':" index.html
findstr /C:"mltraining':" index.html
findstr /C:"technical':" index.html

echo.
echo ================================================================
echo     RECOMMENDATIONS
echo ================================================================
echo.
echo If files are missing, we need to:
echo 1. Use the files that DO exist
echo 2. Update index.html to point to them
echo 3. Or create the missing files
echo.
pause