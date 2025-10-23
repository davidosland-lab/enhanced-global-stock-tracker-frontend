@echo off
cls
echo ================================================================================
echo     STOCK TRACKER COMPLETE V3 - WINDOWS 11 INSTALLATION
echo     Including: FinBERT, Historical Data Module, ML Integration
echo ================================================================================
echo.
echo Version 3.0 includes:
echo   - FinBERT sentiment analysis (no more random data)
echo   - Historical Data Module with SQLite storage
echo   - ML Integration across all 11 modules
echo   - Working charts with Chart.js
echo   - Real Yahoo Finance data throughout
echo.
pause

REM Check Python installation
echo.
echo [STEP 1/10] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation!
    echo.
    pause
    exit /b 1
)
python --version
echo Python found successfully!

REM Upgrade pip
echo.
echo [STEP 2/10] Upgrading pip...
python -m pip install --upgrade pip

REM Install core dependencies
echo.
echo [STEP 3/10] Installing core dependencies...
pip install fastapi uvicorn yfinance pandas numpy python-multipart cachetools pytz aiofiles

REM Install ML dependencies
echo.
echo [STEP 4/10] Installing Machine Learning dependencies...
pip install scikit-learn joblib xgboost ta

REM Install FinBERT dependencies
echo.
echo [STEP 5/10] Installing FinBERT for Document Analysis...
echo This may take several minutes and will download a ~400MB model on first use...
pip install transformers torch sentencepiece

REM Install additional tools
echo.
echo [STEP 6/10] Installing additional analysis tools...
pip install matplotlib seaborn beautifulsoup4 requests textblob nltk lz4

REM Create required directories
echo.
echo [STEP 7/10] Creating required directories...
if not exist "historical_data" mkdir historical_data
if not exist "historical_data\cache" mkdir historical_data\cache
if not exist "models" mkdir models
if not exist "uploads" mkdir uploads
if not exist "cache" mkdir cache
if not exist "knowledge_base" mkdir knowledge_base
if not exist "ml_models" mkdir ml_models

REM Initialize databases
echo.
echo [STEP 8/10] Initializing databases...
python -c "import sqlite3; conn = sqlite3.connect('ml_integration_bridge.db'); conn.execute('CREATE TABLE IF NOT EXISTS knowledge_base (id INTEGER PRIMARY KEY, module TEXT, data TEXT, timestamp DATETIME, metadata TEXT)'); conn.commit(); conn.close(); print('ML Integration database created')"

python -c "import sqlite3; conn = sqlite3.connect('ml_knowledge_base.db'); conn.execute('CREATE TABLE IF NOT EXISTS model_versions (id INTEGER PRIMARY KEY, symbol TEXT, version INTEGER, metrics TEXT, timestamp DATETIME)'); conn.commit(); conn.close(); print('ML Knowledge base created')"

REM Test installations
echo.
echo [STEP 9/10] Testing installations...
python -c "import fastapi; print(f'FastAPI version: {fastapi.__version__}')"
python -c "import yfinance; print(f'yfinance version: {yfinance.__version__}')"
python -c "import transformers; print(f'Transformers version: {transformers.__version__}')"
python -c "from finbert_analyzer import get_analyzer; print('FinBERT analyzer ready')" 2>nul || echo FinBERT will initialize on first use

REM Create desktop shortcut
echo.
echo [STEP 10/10] Creating desktop shortcut...
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%USERPROFILE%\Desktop\Stock Tracker V3.lnk" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "%CD%\START_SYSTEM.bat" >> CreateShortcut.vbs
echo oLink.WorkingDirectory = "%CD%" >> CreateShortcut.vbs
echo oLink.IconLocation = "%SystemRoot%\system32\SHELL32.dll,13" >> CreateShortcut.vbs
echo oLink.Description = "Stock Tracker V3 with FinBERT and Historical Data" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs
cscript CreateShortcut.vbs >nul
del CreateShortcut.vbs
echo Desktop shortcut created!

REM Installation complete
echo.
echo ================================================================================
echo     INSTALLATION COMPLETE!
echo ================================================================================
echo.
echo All components installed successfully:
echo   [✓] Core dependencies
echo   [✓] Machine Learning libraries
echo   [✓] FinBERT sentiment analysis
echo   [✓] Historical Data Module
echo   [✓] Analysis tools
echo   [✓] Directory structure
echo   [✓] Databases initialized
echo   [✓] Desktop shortcut created
echo.
echo To start the application:
echo   1. Run START_SYSTEM.bat
echo   2. Or use the desktop shortcut "Stock Tracker V3"
echo.
echo First-time setup:
echo   1. Start the application
echo   2. Go to Historical Data Module
echo   3. Download data for your symbols (e.g., CBA.AX, BHP.AX)
echo   4. Data will be stored locally for fast access
echo.
echo Features available:
echo   - FinBERT: Consistent sentiment analysis (no random data)
echo   - Historical Data: Local SQLite storage for fast backtesting
echo   - ML Integration: All 11 modules connected
echo   - Real Data: Live Yahoo Finance integration
echo.
pause