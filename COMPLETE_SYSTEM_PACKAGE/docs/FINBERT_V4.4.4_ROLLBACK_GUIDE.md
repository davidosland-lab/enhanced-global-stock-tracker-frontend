# FinBERT v4.4.4 - Rollback Guide

## 📦 Rollback Point Information

**Version**: FinBERT v4.4.4 MARKERS_VISIBLE  
**Date**: 2025-11-06 20:40:28  
**Package**: `FinBERT_v4.4.4_MARKERS_VISIBLE_20251106_204028.zip` (217KB)  
**Status**: ✅ STABLE - Known Working Version  
**Purpose**: Safe rollback point before major changes  

---

## 🎯 What is FinBERT v4.4.4?

FinBERT v4.4.4 is the **complete stock prediction platform** with:

### Core Features
- **4-Model Ensemble System**:
  - LSTM Neural Network (45% weight)
  - Trend Analysis (25% weight)
  - Technical Indicators (15% weight)
  - **FinBERT Sentiment Analysis** (15% weight) ⭐ Real NLP sentiment
  
- **Paper Trading System**: Virtual $10,000 account
- **Backtesting Engine**: Historical strategy testing
- **Portfolio Analysis**: Multi-stock correlation analysis
- **Parameter Optimization**: Grid/random search
- **Prediction Hold System**: Multi-timezone support
- **Trade Markers Visualization**: ✅ BUY/SELL markers visible on charts

### Key Differences from Overnight Screener

| Feature | FinBERT v4.4.4 | Overnight Screener (Phase 3) |
|---------|----------------|------------------------------|
| **Sentiment** | Real FinBERT (transformers) | Simple SPI gap prediction |
| **Purpose** | Real-time trading predictions | Overnight batch screening |
| **Interface** | Web UI (Flask) | Batch reports (HTML) |
| **Trading** | Paper trading + backtesting | Report generation only |
| **Stocks** | Any symbol (US + international) | 240 ASX stocks |
| **Execution** | On-demand | Scheduled (10 PM - 7 AM) |
| **Dependencies** | TensorFlow, transformers | yfinance, pandas |

---

## 📂 Package Structure

```
FinBERT_v4.4.4_CORRECTED/
├── app_finbert_v4_dev.py          # Main Flask application
├── config_dev.py                   # Configuration
├── models/
│   ├── finbert_sentiment.py       # ⭐ Real FinBERT sentiment
│   ├── news_sentiment_real.py     # News analysis
│   ├── lstm_predictor.py          # LSTM model
│   ├── train_lstm.py              # Custom training
│   ├── prediction_manager.py      # Prediction coordination
│   ├── trading/                   # Paper trading system
│   │   ├── paper_trading_engine.py
│   │   ├── portfolio_manager.py
│   │   ├── order_manager.py
│   │   └── risk_manager.py
│   └── backtesting/               # Backtesting framework
│       ├── data_loader.py
│       ├── prediction_engine.py
│       ├── trading_simulator.py
│       └── portfolio_engine.py
├── static/                        # Web assets (CSS, JS)
├── templates/                     # HTML templates
├── INSTALL.bat                    # Installation script
├── START_FINBERT.bat             # Startup script
├── VERIFY_INSTALL.bat            # Installation checker
├── requirements.txt              # Dependencies
├── README.md                     # User guide
├── LSTM_TRAINING_GUIDE.md        # Training documentation
└── CUSTOM_TRAINING_GUIDE.md      # Advanced training

```

---

## 🔄 Rollback Scenarios

### Scenario 1: After Breaking Changes
**When to Use**: New development breaks FinBERT functionality

**Steps**:
1. Stop any running processes
2. Extract rollback package
3. Run restoration script
4. Verify installation
5. Restart server

### Scenario 2: Before Major Updates
**When to Use**: About to make significant changes

**Steps**:
1. Create git tag for current state
2. Test rollback procedure
3. Make changes
4. If issues arise, use rollback

### Scenario 3: Dependency Conflicts
**When to Use**: Package updates break compatibility

**Steps**:
1. Restore v4.4.4 package
2. Reinstall from v4.4.4 requirements.txt
3. Clear Python cache
4. Restart

---

## 🛠️ Rollback Methods

### Method 1: From ZIP Package (Fastest)

```batch
REM 1. Navigate to project directory
cd C:\path\to\project

REM 2. Extract rollback package
unzip FinBERT_v4.4.4_MARKERS_VISIBLE_20251106_204028.zip

REM 3. Copy files to main directory
xcopy /E /Y FinBERT_v4.4.4_CORRECTED\* .

REM 4. Run installation
INSTALL.bat

REM 5. Verify
VERIFY_INSTALL.bat

REM 6. Start server
START_FINBERT.bat
```

### Method 2: From Git Tag (Recommended)

```bash
# 1. Check available rollback tags
git tag -l "finbert-v4.4.4*"

# 2. Rollback to tag
git checkout finbert-v4.4.4-rollback-point

# 3. Reinstall dependencies
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# 4. Start server
python app_finbert_v4_dev.py
```

### Method 3: From Backup Branch

```bash
# 1. Switch to backup branch
git checkout finbert-v4.4.4-stable-backup

# 2. Create new working branch
git checkout -b finbert-v4.4.4-restored

# 3. Reinstall and test
pip install -r requirements.txt
python app_finbert_v4_dev.py
```

---

## 📋 Pre-Rollback Checklist

Before performing rollback:

- [ ] **Backup Current Work**: Save any uncommitted changes
- [ ] **Document Issues**: Note what went wrong
- [ ] **Stop Services**: Close all running Flask/Python processes
- [ ] **Check Dependencies**: Note current package versions
- [ ] **Export Data**: Backup any trade history or custom models
- [ ] **Close Browser**: Close all FinBERT web UI tabs

---

## 🔧 Restoration Script

Create `ROLLBACK_TO_FINBERT_V4.4.4.bat`:

```batch
@echo off
REM ============================================================================
REM FinBERT v4.4.4 Rollback Script
REM ============================================================================

echo.
echo ============================================================================
echo FINBERT v4.4.4 ROLLBACK - STARTING
echo ============================================================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo WARNING: Not running as administrator
    echo Some operations may fail
    echo.
)

REM Step 1: Backup current state
echo [1/7] Backing up current state...
if exist "backup_before_rollback" rmdir /s /q "backup_before_rollback"
mkdir "backup_before_rollback"
xcopy /E /Y models backup_before_rollback\models\
xcopy /E /Y static backup_before_rollback\static\
xcopy /E /Y templates backup_before_rollback\templates\
copy app*.py backup_before_rollback\
echo    ✓ Current state backed up

REM Step 2: Extract rollback package
echo.
echo [2/7] Extracting rollback package...
if not exist "FinBERT_v4.4.4_MARKERS_VISIBLE_20251106_204028.zip" (
    echo ERROR: Rollback package not found!
    echo Please download: FinBERT_v4.4.4_MARKERS_VISIBLE_20251106_204028.zip
    pause
    exit /b 1
)

powershell -command "Expand-Archive -Path 'FinBERT_v4.4.4_MARKERS_VISIBLE_20251106_204028.zip' -DestinationPath '.' -Force"
echo    ✓ Package extracted

REM Step 3: Copy files
echo.
echo [3/7] Restoring FinBERT v4.4.4 files...
xcopy /E /Y FinBERT_v4.4.4_CORRECTED\* .
echo    ✓ Files restored

REM Step 4: Activate virtual environment
echo.
echo [4/7] Setting up Python environment...
if exist "venv" (
    call venv\Scripts\activate
    echo    ✓ Virtual environment activated
) else (
    echo    ! Virtual environment not found, creating...
    python -m venv venv
    call venv\Scripts\activate
    echo    ✓ Virtual environment created
)

REM Step 5: Install dependencies
echo.
echo [5/7] Installing dependencies...
pip install -r requirements.txt --quiet
if %errorLevel% neq 0 (
    echo    ✗ Dependency installation failed
    pause
    exit /b 1
)
echo    ✓ Dependencies installed

REM Step 6: Verify installation
echo.
echo [6/7] Verifying installation...
if exist "VERIFY_INSTALL.bat" (
    call VERIFY_INSTALL.bat
) else (
    echo    ! Verification script not found, skipping
)

REM Step 7: Cleanup
echo.
echo [7/7] Cleaning up...
if exist "FinBERT_v4.4.4_CORRECTED" rmdir /s /q "FinBERT_v4.4.4_CORRECTED"
echo    ✓ Cleanup complete

echo.
echo ============================================================================
echo ROLLBACK COMPLETE
echo ============================================================================
echo.
echo FinBERT v4.4.4 has been restored successfully!
echo.
echo Next steps:
echo   1. Start the server: START_FINBERT.bat
echo   2. Open browser: http://localhost:5002
echo   3. Test predictions and trade markers
echo.
echo Your previous version was backed up to: backup_before_rollback\
echo.
pause
```

---

## ✅ Post-Rollback Verification

After rollback, verify these features work:

### 1. Server Startup
```batch
START_FINBERT.bat
```
Expected: Server starts on http://localhost:5002

### 2. Basic Prediction
- Open: http://localhost:5002
- Enter: `AAPL`
- Click: "Get Prediction"
- Verify: All 4 models show predictions

### 3. FinBERT Sentiment
- Check prediction result
- Verify: "FinBERT Sentiment" section shows news analysis
- Expected: Positive/Negative/Neutral with confidence

### 4. Trade Markers
- Click: "View Backtest"
- Enter: `AAPL`, select date range
- Run backtest
- Verify: Green (BUY) and Red (SELL) markers visible on chart

### 5. Paper Trading
- Click: "Paper Trading"
- Place a test trade
- Verify: Trade executes and shows in history

### 6. Custom Training
- Navigate to training section
- Select stock: `CBA.AX`
- Start training
- Verify: Training completes without errors

---

## 🐛 Troubleshooting Rollback Issues

### Issue 1: Import Errors After Rollback

**Symptom**: `ModuleNotFoundError` or `ImportError`

**Solution**:
```batch
REM Clear Python cache
del /s /q __pycache__
del /s /q *.pyc

REM Reinstall dependencies
pip uninstall -y -r requirements.txt
pip install -r requirements.txt
```

### Issue 2: Port 5002 Already in Use

**Symptom**: `Address already in use`

**Solution**:
```batch
REM Find process on port 5002
netstat -ano | findstr :5002

REM Kill process (replace PID with actual process ID)
taskkill /PID <PID> /F

REM Restart server
START_FINBERT.bat
```

### Issue 3: FinBERT Model Not Loading

**Symptom**: Sentiment analysis fails or shows "N/A"

**Solution**:
```batch
REM Clear transformers cache
rmdir /s /q %USERPROFILE%\.cache\huggingface

REM Reinstall transformers
pip uninstall transformers
pip install transformers==4.35.2

REM Restart server
```

### Issue 4: Trade Markers Not Visible

**Symptom**: Chart shows but no BUY/SELL markers

**Solution**:
1. Check browser console (F12) for JavaScript errors
2. Clear browser cache (Ctrl+F5)
3. Verify static files copied correctly:
   ```batch
   dir static\js\backtest.js
   ```
4. Restart server

### Issue 5: Database Errors

**Symptom**: `sqlite3.OperationalError`

**Solution**:
```batch
REM Backup old database
copy trades.db trades_backup.db

REM Delete and recreate
del trades.db
python app_finbert_v4_dev.py
```

---

## 📊 Version Comparison

| Component | v4.4.4 | Overnight Screener (Phase 3) |
|-----------|--------|------------------------------|
| **Sentiment Model** | FinBERT (transformers) | SPI gap prediction |
| **Real-time Trading** | ✅ Paper trading | ❌ Reports only |
| **Backtesting** | ✅ Full framework | ❌ No backtesting |
| **Trade Markers** | ✅ Visible on charts | ❌ Not applicable |
| **Web UI** | ✅ Flask app | ❌ HTML reports |
| **LSTM Training** | ✅ Custom training UI | ✅ Automated training |
| **Email Notifications** | ❌ Not included | ✅ SMTP integration |
| **Batch Processing** | ❌ On-demand only | ✅ 240 stocks overnight |
| **Deployment** | Windows ZIP (217KB) | Windows ZIP (116KB) |

---

## 🔐 Backup Locations

FinBERT v4.4.4 is backed up in multiple locations:

### 1. Git Repository
- **Branch**: `finbert-v4.4.4-stable-backup`
- **Tag**: `finbert-v4.4.4-rollback-point`
- **Remote**: GitHub (pushed)

### 2. Local Files
- **ZIP**: `FinBERT_v4.4.4_MARKERS_VISIBLE_20251106_204028.zip`
- **Location**: Project root
- **Size**: 217KB

### 3. Backup Directory
- **Path**: `backup/finbert_v4.4.4/`
- **Contents**: Full extracted package
- **Created**: 2025-11-07

---

## 📝 Rollback History

| Date | Action | Reason | Result |
|------|--------|--------|--------|
| 2025-11-07 | Created rollback point | Before Phase 3 integration | ✅ Success |

---

## 🆘 Emergency Rollback

If everything fails, use this emergency procedure:

```batch
REM 1. Delete everything except ZIP
del /s /q *.py
del /s /q *.pyc
rmdir /s /q models
rmdir /s /q static
rmdir /s /q templates

REM 2. Extract fresh copy
powershell -command "Expand-Archive -Path 'FinBERT_v4.4.4_MARKERS_VISIBLE_20251106_204028.zip' -DestinationPath '.' -Force"

REM 3. Copy files
xcopy /E /Y FinBERT_v4.4.4_CORRECTED\* .

REM 4. Fresh Python environment
rmdir /s /q venv
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

REM 5. Start
START_FINBERT.bat
```

---

## 📞 Support

If rollback fails or you encounter issues:

1. **Check Logs**: Review `flask_error.log` and console output
2. **Verify Files**: Ensure ZIP package is not corrupted
3. **Clean Install**: Delete everything and start fresh from ZIP
4. **Check Requirements**: Verify Python 3.8+ is installed
5. **Test Network**: Ensure internet connection for dependencies

---

## 📚 Related Documentation

- `README.md` - FinBERT v4.4.4 user guide
- `LSTM_TRAINING_GUIDE.md` - Custom model training
- `CUSTOM_TRAINING_GUIDE.md` - Advanced training options
- `ALL_PHASES_COMPLETE.md` - Feature completion status
- `TROUBLESHOOTING_FLASK_CORS.md` - Common issues

---

## ✅ Rollback Checklist

When performing rollback:

- [ ] Backup current work
- [ ] Stop all services
- [ ] Extract ZIP package
- [ ] Copy files to main directory
- [ ] Reinstall dependencies
- [ ] Verify installation
- [ ] Test server startup
- [ ] Test predictions
- [ ] Test FinBERT sentiment
- [ ] Test trade markers
- [ ] Test paper trading
- [ ] Test backtesting
- [ ] Document rollback in history

---

**Last Updated**: 2025-11-07  
**Rollback Point Version**: FinBERT v4.4.4 MARKERS_VISIBLE  
**Package Date**: 2025-11-06 20:40:28  
**Status**: ✅ VERIFIED AND READY FOR USE
