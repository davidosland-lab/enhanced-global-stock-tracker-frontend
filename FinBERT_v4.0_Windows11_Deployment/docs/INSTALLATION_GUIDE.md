# FinBERT v4.0 - Detailed Installation Guide for Windows 11

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Step-by-Step Installation](#step-by-step-installation)
3. [Installation Options](#installation-options)
4. [Verification](#verification)
5. [Common Installation Issues](#common-installation-issues)

---

## Prerequisites

### Required Software

#### Python 3.8 or Higher
1. Download Python from [python.org](https://www.python.org/downloads/)
2. **CRITICAL:** Check "Add Python to PATH" during installation
3. Verify installation:
   ```cmd
   python --version
   ```
   Should show: `Python 3.8.x` or higher

#### Microsoft Visual C++ Redistributable (for TensorFlow)
- Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe
- Only required for FULL installation with AI/ML features
- Already installed on most Windows 11 systems

### System Requirements

**Minimum (MINIMAL Install):**
- Windows 11 (any edition)
- 4 GB RAM
- 500 MB free disk space
- Internet connection for installation

**Recommended (FULL Install):**
- Windows 11 Pro or better
- 8 GB RAM or more
- 2 GB free disk space
- Stable internet connection
- CPU with AVX support (for TensorFlow optimization)

---

## Step-by-Step Installation

### Step 1: Extract the Package

1. Locate the downloaded `FinBERT_v4.0_Windows11_Deployment.zip`
2. Right-click → **Extract All...**
3. Choose destination folder (e.g., `C:\FinBERT_v4`)
4. Click **Extract**

**Result:** You should see a folder with:
```
FinBERT_v4.0_Windows11_Deployment/
├── scripts/
│   └── INSTALL_WINDOWS11.bat
├── START_FINBERT_V4.bat
├── app_finbert_v4_dev.py
├── requirements-full.txt
├── requirements-minimal.txt
└── ... (other files)
```

### Step 2: Open Command Prompt as Administrator

**Why Administrator?** Some packages (like TensorFlow) may need elevated permissions.

**How to open:**
1. Press `Win + X`
2. Select **"Terminal (Admin)"** or **"Command Prompt (Admin)"**
3. Click **Yes** on the UAC prompt

**Navigate to installation folder:**
```cmd
cd C:\FinBERT_v4\FinBERT_v4.0_Windows11_Deployment
```

### Step 3: Run Installation Script

```cmd
scripts\INSTALL_WINDOWS11.bat
```

**What happens:**
1. Script checks Python installation
2. Verifies Python version (3.8+)
3. Creates virtual environment (isolated Python environment)
4. Asks you to choose installation type:
   ```
   Choose installation type:
   [1] FULL INSTALL - Complete AI/ML (TensorFlow + FinBERT + News Scraping)
   [2] MINIMAL INSTALL - Basic features only (No AI/ML)
   ```

### Step 4: Choose Installation Type

#### Option 1: FULL INSTALL (Recommended)
- **Enter:** `1`
- **Size:** ~900 MB
- **Time:** 10-20 minutes (depends on internet speed)
- **Features:**
  - ✅ Real FinBERT sentiment analysis
  - ✅ TensorFlow LSTM predictions
  - ✅ News scraping (Yahoo Finance + Finviz)
  - ✅ Advanced technical analysis
  - ✅ All AI/ML capabilities

**Installation progress:**
```
Installing dependencies...
Installing Flask==2.3.0... ✓
Installing yfinance==0.2.28... ✓
Installing pandas==2.0.3... ✓
Installing numpy==1.24.3... ✓
Installing scikit-learn==1.3.0... ✓
Installing beautifulsoup4==4.12.2... ✓
Installing tensorflow... (this takes 5-10 minutes) ✓
Installing torch... (this takes 5-10 minutes) ✓
Installing transformers... ✓
```

#### Option 2: MINIMAL INSTALL
- **Enter:** `2`
- **Size:** ~50 MB
- **Time:** 2-3 minutes
- **Features:**
  - ✅ Basic price charts
  - ✅ Technical indicators (SMA, RSI, MACD)
  - ✅ Simple predictions
  - ❌ No sentiment analysis
  - ❌ No LSTM predictions
  - ❌ No news scraping

**Installation progress:**
```
Installing minimal dependencies...
Installing Flask==2.3.0... ✓
Installing yfinance==0.2.28... ✓
Installing pandas==2.0.3... ✓
Installing numpy==1.24.3... ✓
Installing scikit-learn==1.3.0... ✓
```

### Step 5: Verify Installation

The script automatically verifies installation:

```
Verifying installation...
✓ Flask installed successfully
✓ yfinance installed successfully
✓ pandas installed successfully
✓ numpy installed successfully
✓ scikit-learn installed successfully
✓ beautifulsoup4 installed successfully
✓ aiohttp installed successfully
✓ tensorflow installed successfully (FULL only)
✓ torch installed successfully (FULL only)
✓ transformers installed successfully (FULL only)

SUCCESS! FinBERT v4.0 installation complete!
```

**If any check fails:**
- Note the failed package name
- See [Common Installation Issues](#common-installation-issues) below

### Step 6: Start the Application

```cmd
START_FINBERT_V4.bat
```

**What happens:**
1. Activates virtual environment
2. Checks for required files
3. Starts Flask server on port 5001
4. Opens browser automatically

**Expected output:**
```
========================================
FinBERT v4.0 - Stock Analysis System
========================================

Activating virtual environment...
Starting FinBERT v4.0 server...

 * Serving Flask app 'app_finbert_v4_dev'
 * Debug mode: off
 * Running on http://127.0.0.1:5001

Press CTRL+C to stop the server

Open your browser to: http://127.0.0.1:5001
```

### Step 7: Access the Application

**Automatic:** Browser should open to http://127.0.0.1:5001

**Manual:**
1. Open any web browser (Chrome, Edge, Firefox)
2. Navigate to: `http://127.0.0.1:5001`

**First Load:**
- UI should display with search bar
- Enter a stock symbol (e.g., `AAPL`, `TSLA`, `MSFT`)
- Click **"Analyze Stock"**

---

## Installation Options

### Comparison Table

| Feature | FULL Install | MINIMAL Install |
|---------|--------------|-----------------|
| **Download Size** | 900 MB | 50 MB |
| **Install Time** | 10-20 min | 2-3 min |
| **Disk Space** | 2 GB | 500 MB |
| **Price Charts** | ✅ | ✅ |
| **Technical Indicators** | ✅ | ✅ |
| **Real News Scraping** | ✅ | ❌ |
| **FinBERT Sentiment** | ✅ | ❌ |
| **LSTM Predictions** | ✅ | ❌ |
| **GPU Acceleration** | ✅ (if available) | ❌ |

### When to Choose FULL Install

Choose FULL if you want:
- Real sentiment analysis from financial news
- Advanced AI/ML predictions with LSTM
- Complete feature set for research/analysis
- GPU-accelerated computations (if NVIDIA GPU available)

### When to Choose MINIMAL Install

Choose MINIMAL if you:
- Have limited disk space or slow internet
- Only need basic charting and technical analysis
- Want to test the application quickly
- Don't need sentiment or advanced ML features

### Upgrading from MINIMAL to FULL

You can upgrade later without reinstalling:

```cmd
cd FinBERT_v4.0_Windows11_Deployment
venv\Scripts\activate
pip install -r requirements-full.txt
pip install tensorflow torch transformers sentencepiece
```

Time: ~10-15 minutes

---

## Verification

### Manual Verification Checklist

After installation, verify these components:

#### 1. Virtual Environment
```cmd
cd FinBERT_v4.0_Windows11_Deployment
dir venv
```
Should show: `Scripts\` folder with `python.exe` and `activate.bat`

#### 2. Python Packages (FULL Install)
```cmd
venv\Scripts\activate
pip list
```
Should show:
- Flask (2.3.0 or higher)
- yfinance (0.2.28 or higher)
- pandas (2.0.3 or higher)
- numpy (1.24.3 or higher)
- tensorflow (2.13.0 or higher)
- torch (2.0.0 or higher)
- transformers (4.30.0 or higher)

#### 3. Core Files
Verify these files exist:
- `app_finbert_v4_dev.py` (main Flask application)
- `config_dev.py` (configuration)
- `finbert_v4_enhanced_ui.html` (UI with ECharts)
- `models/finbert_sentiment.py` (sentiment analyzer)
- `models/news_sentiment_real.py` (news scraper)
- `models/lstm_predictor.py` (LSTM predictions)

#### 4. Test Run
```cmd
START_FINBERT_V4.bat
```
- Server should start without errors
- Browser should open to http://127.0.0.1:5001
- UI should load with search bar

#### 5. Test Stock Analysis
In the web interface:
1. Enter: `AAPL`
2. Click: **"Analyze Stock"**
3. Wait 5-10 seconds

**Expected results:**
- Price chart with candlesticks (no overlapping!)
- Volume chart
- Technical indicators (SMA, RSI, MACD)
- Predictions section
- **FULL only:** Sentiment analysis with recent news articles

---

## Common Installation Issues

### Issue 1: "Python is not recognized"

**Symptoms:**
```
'python' is not recognized as an internal or external command
```

**Cause:** Python not in system PATH

**Solution:**
1. Reinstall Python from python.org
2. **CHECK:** "Add Python to PATH" during installation
3. Restart Command Prompt
4. Verify: `python --version`

**Alternative:**
Use full path to python.exe:
```cmd
C:\Python39\python.exe -m venv venv
```

### Issue 2: "pip install fails with SSL error"

**Symptoms:**
```
WARNING: Retrying due to connection errors
SSL: CERTIFICATE_VERIFY_FAILED
```

**Cause:** Corporate firewall or antivirus blocking HTTPS

**Solution 1 (Temporary - Use with Caution):**
```cmd
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements-full.txt
```

**Solution 2 (Better - Fix SSL):**
1. Update pip: `python -m pip install --upgrade pip`
2. Update certificates: `pip install --upgrade certifi`
3. Retry installation

### Issue 3: "TensorFlow installation fails"

**Symptoms:**
```
ERROR: Could not build wheels for tensorflow
ERROR: Failed building wheel for h5py
```

**Cause:** Missing Microsoft Visual C++ Redistributable

**Solution:**
1. Download: https://aka.ms/vs/17/release/vc_redist.x64.exe
2. Install the redistributable
3. Restart Command Prompt
4. Retry: `pip install tensorflow`

### Issue 4: "torch installation hangs"

**Symptoms:**
- Installation stops at "Installing torch..."
- Progress bar doesn't move for 10+ minutes

**Cause:** Large download (2+ GB) over slow connection

**Solution:**
- Be patient - torch is very large
- Monitor network activity (should see download traffic)
- If truly stuck (no network activity for 20+ min):
  ```cmd
  CTRL+C
  pip install torch --no-cache-dir
  ```

### Issue 5: "Permission denied" errors

**Symptoms:**
```
ERROR: Could not install packages due to an EnvironmentError: [WinError 5] Access is denied
```

**Cause:** Insufficient permissions

**Solution:**
1. Close Command Prompt
2. Right-click Command Prompt → **Run as Administrator**
3. Navigate back to installation folder
4. Retry installation

### Issue 6: "Module not found" when starting

**Symptoms:**
```
ModuleNotFoundError: No module named 'flask'
```

**Cause:** Virtual environment not activated

**Solution:**
Always use the startup script:
```cmd
START_FINBERT_V4.bat
```

**Or manually activate:**
```cmd
venv\Scripts\activate
python app_finbert_v4_dev.py
```

### Issue 7: "Port 5001 already in use"

**Symptoms:**
```
OSError: [Errno 48] Address already in use
```

**Cause:** Another application using port 5001

**Solution 1 - Stop other application:**
```cmd
netstat -ano | findstr :5001
taskkill /PID <PID_NUMBER> /F
```

**Solution 2 - Use different port:**
Edit `config_dev.py`:
```python
PORT = 5002  # Change from 5001 to 5002
```

### Issue 8: "Charts not displaying"

**Symptoms:**
- UI loads but charts are blank
- Browser console shows "echarts is not defined"

**Cause:** CDN blocked or offline

**Solution:**
1. Check internet connection
2. Open browser console (F12)
3. Look for network errors
4. Try different browser (Chrome, Edge, Firefox)
5. Disable browser extensions (especially ad blockers)

### Issue 9: "No sentiment data for stock"

**Symptoms:**
```
Sentiment: Not available
News: No recent articles found
```

**Cause:** Stock has no recent news (expected behavior)

**NOT a bug:** System correctly returns empty results instead of fake data

**Stocks with good news coverage:**
- US Large Caps: AAPL, TSLA, MSFT, GOOGL, AMZN
- US High Profile: NVDA, META, NFLX

**Stocks with limited news:**
- Small caps
- International stocks (CBA.AX, etc.)
- Low-volume tickers

### Issue 10: "Slow sentiment analysis"

**Symptoms:**
- Analysis takes 30+ seconds
- Browser shows "Loading..." for long time

**Cause:** First run downloads FinBERT model (~500MB)

**Solution:**
- Be patient on first analysis of any stock
- Model is cached after first download
- Subsequent analyses should be faster (5-10 seconds)
- Check disk space (need 1GB free for model cache)

---

## Getting Help

### Documentation

- **README.md** - Quick start guide
- **USER_GUIDE.md** - Feature documentation
- **TROUBLESHOOTING.md** - Common issues and solutions

### Log Files

If issues persist, check log files:

```cmd
cd FinBERT_v4.0_Windows11_Deployment
type sentiment_cache.log
```

### System Information

Provide this information when seeking help:

```cmd
python --version
pip --version
pip list | findstr "tensorflow torch transformers"
```

---

## Next Steps

Once installation is verified:

1. Read **USER_GUIDE.md** to learn about features
2. Try analyzing different stocks (AAPL, TSLA, MSFT)
3. Explore sentiment analysis with news articles (FULL install only)
4. Review predictions and technical indicators
5. Experiment with different timeframes and symbols

**Installation Complete!** 🎉

You now have a fully functional AI-powered stock analysis system with:
- ✅ Real financial news scraping (no mock data!)
- ✅ FinBERT sentiment analysis (97% accuracy)
- ✅ TensorFlow LSTM predictions
- ✅ Fixed candlestick charts (no overlapping!)
- ✅ Complete technical analysis suite
