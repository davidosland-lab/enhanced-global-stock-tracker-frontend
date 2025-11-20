# Event Risk Guard v1.3 - Deployment Guide

## 🆕 What's New in v1.3

### Market Regime Engine (Optional)
v1.3 adds sophisticated market regime detection and volatility forecasting:

**Features**:
- 🔍 **Regime Detection**: Hidden Markov Models (HMM) identify 3 market states:
  - 🟢 **CALM**: Low volatility, stable conditions
  - 🟡 **NORMAL**: Standard market conditions
  - 🔴 **HIGH_VOL**: Elevated volatility, turbulent markets
  
- 📊 **Volatility Forecasting**: GARCH(1,1) models predict next-day volatility
  - 1-day volatility forecast
  - Annualized volatility projection
  - Graceful fallback to EWMA if GARCH unavailable

- ⚠️ **Crash Risk Scoring**: Composite 0.0-1.0 risk score combining:
  - Current market regime
  - Forecasted volatility levels
  - Real-time ASX VIX (^XVI) data

**Installation**:
```bash
# Optional regime engine dependencies
pip install hmmlearn>=0.3.0  # HMM regime detection
pip install arch>=5.3.0       # GARCH volatility forecasting
pip install xgboost>=1.7.0    # Meta-model (optional)
```

**Graceful Degradation**:
- System works perfectly without these dependencies
- Falls back to simpler methods if packages missing:
  - HMM → Gaussian Mixture Model (GMM)
  - GARCH → Exponentially Weighted Moving Average (EWMA)
  - No crashes, just reduced sophistication

**Report Integration**:
- Regime analysis appears in HTML reports automatically
- Shows current regime, volatility, crash risk score
- Only displays when regime engine successfully initializes

---

## Quick Start (5 Minutes)

### Step 1: Extract Package
```bash
unzip event_risk_guard_v1.2_CLEAN.zip
cd event_risk_guard_v1.2_clean
```

### Step 2: Install Dependencies
```batch
INSTALL.bat
```
**Wait**: 2-5 minutes for dependencies to install

### Step 3: Configure API Keys (Optional)
```bash
copy .env.example .env
```
Edit `.env` and add your API keys (optional for basic functionality)

### Step 4: Run Pipeline
```batch
RUN_OVERNIGHT_PIPELINE_FIXED.bat
```

**That's it!** The pipeline will run and generate reports.

---

## What's Included

### Core Features (All Working ✅)
- ✅ **v1.2 Sentiment Analysis** - 7-day and 14-day trend tracking
- ✅ **v1.3 Market Regime Engine** - HMM regime detection, GARCH volatility forecasting (optional)
- ✅ **Stock Scanning** - 240+ ASX stocks across 11 sectors
- ✅ **Event Risk Guard** - Basel III, earnings, dividends protection
- ✅ **LSTM Predictions** - When trained (optional)
- ✅ **FinBERT Sentiment** - News sentiment analysis
- ✅ **Factor Analysis** - 6 constituent factors
- ✅ **Macro Beta** - Market correlation calculations
- ✅ **Web Dashboard** - Interactive visualization
- ✅ **CSV Export** - Full data export with event risk

### All Bugs Fixed ✅
1. ✅ Package bloat (553 files removed)
2. ✅ INSTALL.bat working (requirements.txt present)
3. ✅ Import errors (wrapper script added)
4. ✅ FinBERT modules (4 modules added)
5. ✅ Alpha Vantage imports (completely removed)
6. ✅ Config format (handles sectors at root level)
7. ✅ Sector weight KeyError (all sectors now scan successfully)
8. ✅ Pipeline method name (run_full_pipeline fixed)

### v1.3 Enhancements ✅
1. ✅ Market regime engine integrated (4 new modules)
2. ✅ VIX symbol fixed (^VIX → ^XVI for ASX)
3. ✅ Optional dependencies with graceful fallback
4. ✅ Report templates updated with regime information
5. ✅ Comprehensive MARKET_REGIME_ENGINE_REVIEW.md documentation

---

## System Requirements

### Minimum
- **OS**: Windows 10/11, Linux, macOS
- **Python**: 3.8 or higher (3.12 recommended)
- **RAM**: 4 GB
- **Disk**: 2 GB (for dependencies)
- **Internet**: Required for data fetching

### Recommended
- **OS**: Windows 11
- **Python**: 3.12
- **RAM**: 8 GB
- **Disk**: 5 GB
- **Internet**: High-speed connection

---

## Installation Steps (Detailed)

### 1. Extract Package
```bash
# Windows
unzip event_risk_guard_v1.2_CLEAN.zip
cd event_risk_guard_v1.2_clean

# Linux/Mac
unzip event_risk_guard_v1.2_CLEAN.zip
cd event_risk_guard_v1.2_clean
```

### 2. Verify Python Installation
```bash
python --version
# Should show: Python 3.8+ (3.12 recommended)
```

**If Python not found**:
- Download from: https://www.python.org/downloads/
- During installation: ✅ Check "Add Python to PATH"

### 3. Run Installation
```batch
# Windows
INSTALL.bat

# Linux/Mac
chmod +x INSTALL.bat
bash INSTALL.bat  # Or create equivalent .sh script
```

**What INSTALL.bat does**:
1. Detects Python version
2. Creates virtual environment (`venv/`)
3. Activates virtual environment
4. Upgrades pip
5. Installs all dependencies from `requirements.txt`
6. Shows success message

**Expected output**:
```
[1/5] Python detected successfully!
Python 3.12.x

[2/5] Creating virtual environment...

[3/5] Activating virtual environment...

[4/5] Installing required packages...
This may take a few minutes...

[5/5] Installation complete!
```

### 4. Configure Environment (Optional)
```bash
# Copy example environment file
copy .env.example .env

# Edit .env file (optional - system works without API keys)
notepad .env
```

**Optional API Keys**:
```env
# Alpha Vantage (not used anymore - legacy)
ALPHA_VANTAGE_API_KEY=your_key_here

# Finnhub (optional - for alternative data)
FINNHUB_API_KEY=your_key_here
```

**Note**: System works perfectly without API keys using yahooquery

---

## Usage

### Option 1: Overnight Screening Pipeline (Main Use)

```batch
RUN_OVERNIGHT_PIPELINE_FIXED.bat
```

**What it does**:
1. Analyzes market sentiment (SPI 200, US markets)
2. Scans 240+ ASX stocks
3. Assesses event risks (Basel III, earnings, dividends)
4. Generates predictions (LSTM + FinBERT)
5. Scores opportunities (0-100 scale)
6. Creates reports (HTML + CSV)

**Execution time**: 15-30 minutes (depends on internet speed)

**Output**:
- `reports/html/` - Morning report HTML files
- `reports/csv/` - CSV exports with full data
- `logs/screening/` - Execution logs

### Option 2: Web Dashboard

```batch
START_WEB_UI.bat
```

**Access**: Open browser to http://localhost:5000

**Features**:
- Interactive dashboard
- Real-time data visualization
- Factor analysis charts
- Event risk overview

### Option 3: LSTM Training

**Single Stock**:
```batch
TRAIN_LSTM_SINGLE.bat
```

**Overnight Batch**:
```batch
TRAIN_LSTM_OVERNIGHT_FIXED.bat
```

**Custom Training**:
```batch
TRAIN_LSTM_CUSTOM.bat
```

### Option 4: Testing

**Verify Installation**:
```batch
VERIFY_INSTALLATION.bat
```

**Test FinBERT**:
```batch
TEST_FINBERT.bat
```

**Test Email Notifications**:
```batch
TEST_EMAIL.bat
```

**Run Unit Tests**:
```batch
RUN_TESTS.bat
```

---

## Output Files

### Reports (Generated after each run)

**HTML Reports**: `reports/html/`
```
overnight_screening_YYYY-MM-DD_HHMMSS.html
```
- Market sentiment analysis
- Top opportunities (sorted by score)
- Event risk warnings
- Factor analysis
- Detailed stock information

**CSV Exports**: `reports/csv/`
```
screening_results_YYYY-MM-DD_HHMMSS.csv       # Full results
event_risk_summary_YYYY-MM-DD_HHMMSS.csv      # Event risks only
```

### Logs

**Pipeline Logs**: `logs/screening/overnight_pipeline.log`
- Execution timestamps
- Progress tracking
- Warnings and errors
- Performance metrics

**LSTM Training**: `logs/screening/lstm_training.log`
- Training progress
- Model performance
- Validation metrics

**Email Notifications**: `logs/screening/email_notifications.log`
- Email send status
- Delivery confirmations
- Error notifications

---

## Troubleshooting

### Issue: INSTALL.bat fails with "requirements.txt not found"

**Solution**: You're in the wrong directory
```bash
cd event_risk_guard_v1.2_clean
dir requirements.txt  # Should show the file
INSTALL.bat
```

### Issue: Python not found

**Solution**: Install Python or add to PATH
```bash
# Check Python installation
python --version

# If not found, download from python.org
# Or add to PATH (Windows):
# System Properties > Environment Variables > Path > Add Python directory
```

### Issue: Import errors (ModuleNotFoundError)

**Solution**: Use the FIXED batch file
```batch
# ❌ Don't use:
RUN_OVERNIGHT_PIPELINE.bat

# ✅ Use:
RUN_OVERNIGHT_PIPELINE_FIXED.bat
```

### Issue: "No module named 'models.screening.alpha_vantage_fetcher'"

**Solution**: You have an old version. Download the latest:
- `event_risk_guard_v1.2_CLEAN.zip` (232 KB)
- Commit: b3de83e or later

### Issue: KeyError: 'sectors'

**Solution**: You have an old version. Download the latest:
- `event_risk_guard_v1.2_CLEAN.zip` (232 KB)
- Commit: b3de83e or later

### Issue: TensorFlow installation fails

**Solution**: TensorFlow is optional
```
# Edit requirements.txt, comment out:
# tensorflow>=2.13.0
# keras>=2.13.0

# System will work with FinBERT sentiment only (no LSTM)
```

### Issue: Pipeline runs but no data

**Solution**: Check internet connection
- System needs internet to fetch stock data from Yahoo Finance
- Check firewall settings
- Verify yahooquery is installed: `pip show yahooquery`

---

## Configuration Files

### `models/config/asx_sectors.json`
**Purpose**: Defines ASX stock sectors and tickers
**Format**:
```json
{
  "financials": {
    "name": "Financials",
    "stocks": ["CBA.AX", "NAB.AX", ...]
  },
  "materials": {...}
}
```

**Customization**: Add/remove stocks or sectors as needed

### `models/config/event_calendar.csv`
**Purpose**: Tracks earnings dates and dividend ex-dates
**Format**:
```csv
symbol,event_type,event_date,description
CBA.AX,earnings,2025-08-15,Commonwealth Bank Earnings
```

**Customization**: Add upcoming events manually

### `models/config/screening_config.json`
**Purpose**: Pipeline configuration parameters
**Format**:
```json
{
  "spi_futures": {...},
  "us_indices": {...},
  "screening": {...},
  "performance": {...}
}
```

**Customization**: Adjust thresholds, limits, timeouts

---

## Advanced Usage

### Running Programmatically

```python
from models.screening.overnight_pipeline import OvernightPipeline

# Create pipeline
pipeline = OvernightPipeline()

# Run full screening
results = pipeline.run_complete_screening()

# Access results
print(f"Stocks scanned: {results['total_stocks']}")
print(f"Opportunities found: {len(results['opportunities'])}")
```

### Customizing Sectors

```python
# Scan specific sectors only
pipeline = OvernightPipeline()
results = pipeline.run_full_pipeline(
    sectors=['Financials', 'Healthcare'],
    stocks_per_sector=20
)
```

### Accessing Factor Analysis

```python
from models.screening.factor_view import FactorView

# Analyze opportunity factors
factor_view = FactorView()
factors = factor_view.decompose_score(opportunity)

print(f"Prediction confidence: {factors['prediction_confidence']}")
print(f"Technical strength: {factors['technical_strength']}")
# ... etc
```

---

## Production Deployment

### Scheduling with Task Scheduler (Windows)

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily at desired time (e.g., 8:00 AM)
4. Action: Start a program
5. Program: `C:\path\to\event_risk_guard_v1.2_clean\RUN_OVERNIGHT_PIPELINE_FIXED.bat`
6. Save and test

### Scheduling with Cron (Linux)

```bash
# Edit crontab
crontab -e

# Add daily run at 8 AM
0 8 * * * cd /path/to/event_risk_guard_v1.2_clean && ./RUN_OVERNIGHT_PIPELINE_FIXED.bat
```

### Email Notifications

Configure in `.env`:
```env
EMAIL_ENABLED=true
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_TO=recipient@example.com
```

---

## Performance Optimization

### Speed Up Installation
```bash
# Use pip cache
pip install --cache-dir ./pip_cache -r requirements.txt

# Install CPU-only PyTorch (smaller, faster)
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

### Speed Up Scanning
Edit `models/config/screening_config.json`:
```json
{
  "performance": {
    "max_workers": 10,        // Increase for more parallel processing
    "batch_size": 50,         // Increase batch size
    "cache_enabled": true,    // Enable caching
    "cache_ttl_minutes": 15   // Cache duration
  }
}
```

### Reduce Memory Usage
```bash
# Comment out TensorFlow in requirements.txt
# System will use FinBERT only (lighter)
```

---

## Support & Documentation

### Documentation Files
- `README.md` - v1.2 Release Notes
- `QUICK_START.md` - Quick start guide
- `IMPORT_ERRORS_FIXED.md` - Troubleshooting import issues
- `QUICK_ANSWER_SENTIMENT.md` - Sentiment FAQ
- `docs/SENTIMENT_CALCULATION_v1.2.md` - Technical formula
- `docs/SENTIMENT_SYSTEM_EXPLAINED.md` - User-friendly explanation
- `docs/TROUBLESHOOTING.md` - Common issues

### GitHub Repository
**Pull Request**: https://github.com/davidosland-lab/enhanced-global-stock-tracker-frontend/pull/8
**Branch**: finbert-v4.0-development

### Version Information
- **Version**: 1.2
- **Release Date**: 2025-11-19
- **Package Size**: 232 KB (86 files)
- **Latest Commit**: b3de83e

---

## Changelog

### v1.2 (2025-11-19)
- ✅ Added 7-day and 14-day trend analysis
- ✅ Rebalanced sentiment calculation (30% US, 25% Gap, 15% Agreement, 20% Medium-Term, 10% Confidence)
- ✅ Enhanced medium-term trend detection
- ✅ Fixed Alpha Vantage import errors
- ✅ Fixed config format handling
- ✅ Added wrapper script for import fixes
- ✅ Cleaned package (removed 553 unnecessary files)

### v1.1 (2025-11-17)
- Factor analysis (6 constituent factors)
- Macro beta calculation
- Event Risk Guard (Basel III, earnings, dividends)

### v1.0 (2025-11-13)
- Initial release with overnight screening pipeline

---

## Success Checklist

Before considering deployment complete, verify:

- ✅ INSTALL.bat runs without errors
- ✅ requirements.txt all packages installed
- ✅ RUN_OVERNIGHT_PIPELINE_FIXED.bat executes
- ✅ No import errors
- ✅ Reports generated in `reports/` directory
- ✅ CSV files exported
- ✅ Web dashboard accessible (optional)
- ✅ LSTM training works (optional)
- ✅ Email notifications sent (optional)

---

## Quick Reference

### Key Files
| File | Purpose |
|------|---------|
| `RUN_OVERNIGHT_PIPELINE_FIXED.bat` | **Main launcher** |
| `run_pipeline.py` | Import wrapper script |
| `requirements.txt` | Dependencies list |
| `INSTALL.bat` | Environment setup |
| `.env` | Configuration (optional) |

### Key Directories
| Directory | Contents |
|-----------|----------|
| `models/screening/` | Core pipeline modules |
| `models/config/` | Configuration files |
| `reports/html/` | HTML reports (output) |
| `reports/csv/` | CSV exports (output) |
| `logs/screening/` | Execution logs |
| `docs/` | Documentation |

### Batch Files
| File | Purpose |
|------|---------|
| `RUN_OVERNIGHT_PIPELINE_FIXED.bat` | ✅ **Use this one!** |
| `START_WEB_UI.bat` | Web dashboard |
| `TRAIN_LSTM_SINGLE.bat` | Single stock training |
| `TRAIN_LSTM_OVERNIGHT_FIXED.bat` | Batch training |
| `VERIFY_INSTALLATION.bat` | Installation test |
| `TEST_FINBERT.bat` | FinBERT test |

---

**Ready to deploy!** 🚀

For issues or questions, refer to:
- `IMPORT_ERRORS_FIXED.md` - Import troubleshooting
- `docs/TROUBLESHOOTING.md` - Common problems
- GitHub PR #8 - Development discussion
