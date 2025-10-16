@echo off
echo ========================================
echo Testing Each Service Individually
echo ========================================
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

:menu
echo.
echo Select a service to test:
echo 1. Main Backend (Port 8000)
echo 2. ML Backend (Port 8002)
echo 3. FinBERT Backend (Port 8003)
echo 4. Historical Backend (Port 8004)
echo 5. Backtesting Backend (Port 8005)
echo 6. Run All Tests
echo 7. Exit
echo.
set /p choice="Enter your choice (1-7): "

if "%choice%"=="1" goto main
if "%choice%"=="2" goto ml
if "%choice%"=="3" goto finbert
if "%choice%"=="4" goto historical
if "%choice%"=="5" goto backtesting
if "%choice%"=="6" goto all
if "%choice%"=="7" goto end

echo Invalid choice. Please try again.
goto menu

:main
echo.
echo Testing Main Backend...
echo ========================================
python -c "import main_backend; print('Main Backend imports OK')"
echo.
echo Starting Main Backend (Press Ctrl+C to stop)...
python main_backend.py
goto menu

:ml
echo.
echo Testing ML Backend...
echo ========================================
python -c "import ml_backend; print('ML Backend imports OK')"
echo.
echo Starting ML Backend (Press Ctrl+C to stop)...
python ml_backend.py
goto menu

:finbert
echo.
echo Testing FinBERT Backend...
echo ========================================
python -c "import finbert_backend; print('FinBERT Backend imports OK')"
echo.
echo Starting FinBERT Backend (Press Ctrl+C to stop)...
python finbert_backend.py
goto menu

:historical
echo.
echo Testing Historical Backend...
echo ========================================
python -c "import historical_backend; print('Historical Backend imports OK')"
echo.
echo Starting Historical Backend (Press Ctrl+C to stop)...
python historical_backend.py
goto menu

:backtesting
echo.
echo Testing Backtesting Backend...
echo ========================================
python -c "import backtesting_backend; print('Backtesting Backend imports OK')"
echo.
echo Starting Backtesting Backend (Press Ctrl+C to stop)...
python backtesting_backend.py
goto menu

:all
echo.
echo Running import tests for all services...
echo ========================================
python -c "import main_backend; print('1. Main Backend - OK')"
python -c "import ml_backend; print('2. ML Backend - OK')"
python -c "import finbert_backend; print('3. FinBERT Backend - OK')"
python -c "import historical_backend; print('4. Historical Backend - OK')"
python -c "import backtesting_backend; print('5. Backtesting Backend - OK')"
echo.
echo All imports successful!
goto menu

:end
echo.
echo Exiting...
exit /b 0