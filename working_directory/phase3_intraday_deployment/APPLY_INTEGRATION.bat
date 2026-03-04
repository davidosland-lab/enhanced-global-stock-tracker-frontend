@echo off
REM Auto-Installer for Phase 3 Intraday Integration
REM Windows Compatible

echo ==========================================
echo Phase 3 Intraday Integration - Installer
echo ==========================================
echo.

REM Check Python version
echo 1. Checking Python version...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo X Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set python_version=%%i
echo √ Python %python_version% found
echo.

REM Create virtual environment (optional)
set /p create_venv="Create virtual environment? (recommended) [y/N]: "
if /i "%create_venv%"=="y" (
    echo 2. Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo √ Virtual environment created and activated
) else (
    echo 2. Skipping virtual environment creation
)
echo.

REM Install dependencies
echo 3. Installing dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo X Failed to install dependencies
    pause
    exit /b 1
)
echo √ Dependencies installed successfully
echo.

REM Create necessary directories
echo 4. Creating directories...
if not exist logs mkdir logs
if not exist state mkdir state
if not exist reports mkdir reports
if not exist data mkdir data
echo √ Directories created
echo.

REM Configure settings
echo 5. Configuration...
echo Please edit config\live_trading_config.json to set:
echo   - Your initial capital
echo   - Broker API credentials (if using live trading)
echo   - Alert channels (Telegram, Email, etc.)
echo.
pause

REM Test installation
echo.
echo 6. Testing installation...
python test_integration.py --quick-test

if %errorlevel% neq 0 (
    echo ! Installation test had issues. Check logs above.
) else (
    echo √ Installation test passed
)
echo.

REM Final instructions
echo ==========================================
echo Installation Complete!
echo ==========================================
echo.
echo Next Steps:
echo.
echo 1. Configure your settings:
echo    notepad config\live_trading_config.json
echo.
echo 2. Run full test:
echo    python test_integration.py
echo.
echo 3. Start paper trading:
echo    python live_trading_coordinator.py --paper-trading
echo.
echo 4. View dashboard (if installed):
echo    http://localhost:8050
echo.
echo Documentation:
echo   - README.md - Quick start guide
echo   - INTEGRATION_GUIDE.md - Complete documentation
echo   - INSTALLATION_GUIDE.md - Detailed setup
echo.
echo Happy Trading! 🚀
echo.
pause
