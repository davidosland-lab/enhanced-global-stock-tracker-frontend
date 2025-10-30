# FinBERT v4.0 - Troubleshooting Guide

## Table of Contents
1. [Installation Issues](#installation-issues)
2. [Server Startup Problems](#server-startup-problems)
3. [Analysis Errors](#analysis-errors)
4. [Chart Display Issues](#chart-display-issues)
5. [Sentiment Analysis Problems](#sentiment-analysis-problems)
6. [Performance Issues](#performance-issues)
7. [Network and Connection Errors](#network-and-connection-errors)
8. [Windows-Specific Issues](#windows-specific-issues)

---

## Installation Issues

### Python Not Found

**Error:**
```
'python' is not recognized as an internal or external command
```

**Cause:** Python not installed or not in system PATH

**Solutions:**

1. **Verify Python installation:**
   ```cmd
   where python
   ```
   If no output → Python not installed

2. **Install Python:**
   - Download from https://www.python.org/downloads/
   - **CRITICAL:** Check "Add Python to PATH" during installation
   - Restart Command Prompt after installation

3. **Add to PATH manually:**
   - Find Python installation folder (e.g., `C:\Python39\`)
   - System Properties → Environment Variables
   - Edit "Path" variable → Add `C:\Python39\` and `C:\Python39\Scripts\`
   - Restart Command Prompt

4. **Use full path temporarily:**
   ```cmd
   C:\Python39\python.exe --version
   ```

**Verify Fix:**
```cmd
python --version
pip --version
```
Should show version numbers

---

### Pip Install Fails with SSL Error

**Error:**
```
WARNING: Retrying due to connection errors
SSL: CERTIFICATE_VERIFY_FAILED
Could not fetch URL https://pypi.org/simple/
```

**Cause:** Corporate firewall, antivirus, or outdated SSL certificates

**Solutions:**

1. **Update pip and certifi:**
   ```cmd
   python -m pip install --upgrade pip
   pip install --upgrade certifi
   ```

2. **Temporary bypass (use with caution):**
   ```cmd
   pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements-full.txt
   ```

3. **Check firewall/antivirus:**
   - Temporarily disable antivirus
   - Add Python and pip to antivirus exceptions
   - Check corporate proxy settings

4. **Use alternative package source:**
   ```cmd
   pip install --index-url http://pypi.douban.com/simple/ --trusted-host pypi.douban.com flask
   ```

**Verify Fix:**
```cmd
pip install requests
```
Should complete without SSL errors

---

### TensorFlow Installation Fails

**Error:**
```
ERROR: Could not build wheels for tensorflow
ERROR: Failed building wheel for h5py
error: Microsoft Visual C++ 14.0 or greater is required
```

**Cause:** Missing Microsoft Visual C++ Build Tools

**Solutions:**

1. **Install Visual C++ Redistributable:**
   - Download: https://aka.ms/vs/17/release/vc_redist.x64.exe
   - Run installer
   - Restart computer
   - Retry: `pip install tensorflow`

2. **Install minimal build tools:**
   ```cmd
   pip install --upgrade setuptools wheel
   pip install tensorflow --no-cache-dir
   ```

3. **Use pre-built wheel:**
   - Download from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#tensorflow
   - Find correct version (Python 3.9, Windows, x64)
   - Install: `pip install tensorflow-2.13.0-cp39-cp39-win_amd64.whl`

4. **Skip TensorFlow (MINIMAL install):**
   ```cmd
   pip install -r requirements-minimal.txt
   ```
   Note: This disables LSTM predictions

**Verify Fix:**
```cmd
python -c "import tensorflow as tf; print(tf.__version__)"
```
Should print version number without errors

---

### Torch Installation Hangs

**Error:**
- Installation stops at "Installing torch..."
- No progress for 10+ minutes
- Progress bar stuck at 0%

**Cause:** Large download (2+ GB) over slow connection

**Solutions:**

1. **Be patient:**
   - Check network activity (download in progress)
   - Torch is 2+ GB, can take 20-30 minutes on slow connections
   - Don't interrupt unless truly stuck (no network activity for 20+ min)

2. **Cancel and retry with no cache:**
   ```cmd
   CTRL+C
   pip install torch --no-cache-dir
   ```

3. **Download manually:**
   - Visit: https://pytorch.org/get-started/locally/
   - Select: Windows, Pip, Python, CPU
   - Copy command (e.g., `pip3 install torch torchvision torchaudio`)
   - Run in Command Prompt

4. **Use CPU-only version (faster):**
   ```cmd
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
   ```

**Verify Fix:**
```cmd
python -c "import torch; print(torch.__version__)"
```
Should print version number

---

### Permission Denied Errors

**Error:**
```
ERROR: Could not install packages due to an EnvironmentError
[WinError 5] Access is denied
```

**Cause:** Insufficient permissions to write to directory

**Solutions:**

1. **Run as Administrator:**
   - Close Command Prompt
   - Right-click Command Prompt → "Run as Administrator"
   - Navigate to installation folder
   - Retry installation

2. **Install to user directory:**
   ```cmd
   pip install --user -r requirements-full.txt
   ```

3. **Check folder permissions:**
   - Right-click installation folder → Properties
   - Security tab → Edit → Add your user → Full Control
   - Apply → OK

4. **Use different location:**
   - Extract to `C:\Users\YourName\FinBERT\`
   - User folders typically have full permissions

**Verify Fix:**
```cmd
pip list
```
Should show installed packages

---

## Server Startup Problems

### Port 5001 Already in Use

**Error:**
```
OSError: [Errno 48] Address already in use
[Errno 10048] Only one usage of socket address is normally permitted
```

**Cause:** Another application using port 5001

**Solutions:**

1. **Find process using port:**
   ```cmd
   netstat -ano | findstr :5001
   ```
   Output shows: `TCP  127.0.0.1:5001  0.0.0.0:0  LISTENING  12345`
   PID = 12345

2. **Kill the process:**
   ```cmd
   taskkill /PID 12345 /F
   ```

3. **Change FinBERT port:**
   - Edit `config_dev.py`
   - Change: `PORT = 5002`
   - Restart server
   - Access: http://127.0.0.1:5002

4. **Check for multiple instances:**
   ```cmd
   tasklist | findstr python
   ```
   Kill extra python processes

**Verify Fix:**
```cmd
START_FINBERT_V4.bat
```
Server should start without errors

---

### Module Not Found Error

**Error:**
```
ModuleNotFoundError: No module named 'flask'
ModuleNotFoundError: No module named 'yfinance'
```

**Cause:** Virtual environment not activated or packages not installed

**Solutions:**

1. **Activate virtual environment:**
   ```cmd
   cd FinBERT_v4.0_Windows11_Deployment
   venv\Scripts\activate
   ```
   Prompt should show: `(venv) C:\...\FinBERT_v4.0_Windows11_Deployment>`

2. **Reinstall packages:**
   ```cmd
   pip install -r requirements-full.txt
   ```

3. **Verify installation:**
   ```cmd
   pip list | findstr flask
   ```
   Should show: `Flask  2.3.0`

4. **Use startup script (recommended):**
   ```cmd
   START_FINBERT_V4.bat
   ```
   Automatically activates venv

**Verify Fix:**
```cmd
python -c "import flask; print(flask.__version__)"
```
Should print version without error

---

### File Not Found: finbert_v4_enhanced_ui.html

**Error:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'finbert_v4_enhanced_ui.html'
```

**Cause:** Missing UI file or wrong working directory

**Solutions:**

1. **Check file exists:**
   ```cmd
   cd FinBERT_v4.0_Windows11_Deployment
   dir finbert_v4_enhanced_ui.html
   ```
   Should show file with size ~50 KB

2. **Re-extract package:**
   - Extract ZIP again
   - Ensure all files are present
   - Don't move files after extraction

3. **Run from correct directory:**
   ```cmd
   cd FinBERT_v4.0_Windows11_Deployment
   START_FINBERT_V4.bat
   ```

4. **Check app_finbert_v4_dev.py:**
   - Open in text editor
   - Verify line: `return send_file('finbert_v4_enhanced_ui.html')`
   - Should match exact filename

**Verify Fix:**
```cmd
START_FINBERT_V4.bat
```
Server should start and serve UI

---

## Analysis Errors

### Symbol Not Found

**Error:**
```
Error: Symbol 'XYZ' not found
Could not fetch data for symbol: XYZ
```

**Cause:** Invalid symbol or delisted stock

**Solutions:**

1. **Verify symbol on Yahoo Finance:**
   - Visit: https://finance.yahoo.com/
   - Search for company name
   - Use exact symbol (e.g., `AAPL`, not `APPLE`)

2. **Check for correct suffix:**
   - International stocks need exchange suffix
   - Australia: `CBA.AX`
   - UK: `BP.L`
   - Germany: `SAP.DE`

3. **Try alternative symbols:**
   - Some companies have multiple tickers
   - Class A vs Class B shares (e.g., `GOOGL` vs `GOOG`)

4. **Check if delisted:**
   - Recently delisted stocks won't have data
   - Use historical data only

**Verify Fix:**
Try known-good symbols: `AAPL`, `MSFT`, `TSLA`

---

### Analysis Takes Too Long

**Symptom:**
- "Loading..." shows for 60+ seconds
- Browser appears frozen
- No error message

**Cause:** First-time model download or network issues

**Solutions:**

1. **First run patience:**
   - FinBERT model downloads on first use (~500 MB)
   - Can take 5-10 minutes on slow connections
   - Subsequent analyses will be faster (cached)

2. **Check logs:**
   ```cmd
   type sentiment_cache.log
   ```
   Look for: "Downloading FinBERT model..."

3. **Increase browser timeout:**
   - Don't reload page during download
   - Wait for "Analysis complete" message

4. **Check network:**
   ```cmd
   ping huggingface.co
   ```
   Should respond without packet loss

5. **Manual model download (advanced):**
   ```python
   python
   >>> from transformers import AutoTokenizer, AutoModelForSequenceClassification
   >>> AutoTokenizer.from_pretrained("ProsusAI/finbert")
   >>> AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
   ```

**Verify Fix:**
Analysis should complete in 5-10 seconds after first model download

---

### No Data Returned

**Error:**
```
No historical data available for symbol
Empty dataset returned
```

**Cause:** Symbol has insufficient trading history

**Solutions:**

1. **Check trading history:**
   - Visit Yahoo Finance
   - Verify stock has been trading for 90+ days
   - New IPOs may not have enough data

2. **Reduce lookback period:**
   - Edit `config_dev.py`
   - Change: `LOOKBACK_DAYS = 30` (from 90)
   - Restart server

3. **Try different symbol:**
   - Use established stocks with long history
   - Avoid penny stocks and illiquid tickers

4. **Check API status:**
   ```python
   import yfinance as yf
   ticker = yf.Ticker("AAPL")
   hist = ticker.history(period="1mo")
   print(hist)
   ```
   Should return dataframe with prices

**Verify Fix:**
Try `AAPL` (should always have data)

---

## Chart Display Issues

### Charts Not Displaying

**Symptom:**
- Blank areas where charts should be
- Page loads but no visualizations

**Cause:** JavaScript errors, CDN blocked, or browser issues

**Solutions:**

1. **Check browser console:**
   - Press `F12` → Console tab
   - Look for errors (red text)
   - Common: "echarts is not defined"

2. **Verify CDN access:**
   - Open: https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js
   - Should see JavaScript code (not error page)
   - If blocked: Corporate firewall or content filter

3. **Clear browser cache:**
   ```
   CTRL + F5 (hard refresh)
   ```
   Or:
   - Settings → Privacy → Clear browsing data
   - Check "Cached images and files"
   - Clear data

4. **Try different browser:**
   - Chrome (recommended)
   - Edge
   - Firefox
   - Avoid Internet Explorer

5. **Disable browser extensions:**
   - Ad blockers can block CDN requests
   - Privacy extensions may break scripts
   - Try incognito/private mode

6. **Check JavaScript enabled:**
   - Browser settings → Site settings
   - JavaScript → Allowed

**Verify Fix:**
- Charts should display with candlesticks and volume bars
- Hovering should show tooltips

---

### Candlesticks Overlapping (Old Issue - Should Be Fixed)

**Symptom:**
- Candles overlap and unreadable
- Looks like a solid block instead of individual candles

**Cause:** This was the original bug with Chart.js

**Solution:**
- **Should already be fixed** in v4.0 with ECharts replacement
- If still seeing overlapping:
  1. Hard refresh: `CTRL + F5`
  2. Check you're using correct UI file (finbert_v4_enhanced_ui.html)
  3. Verify ECharts CDN loads: `F12` → Network tab → Look for echarts.min.js

**Verify Fix:**
- Candles should have consistent spacing
- No overlapping
- Each candle clearly visible

---

### Charts Load But Show No Data

**Symptom:**
- Chart containers display
- Axes show but no candles or lines
- "No data available" message

**Cause:** API returned empty dataset or JavaScript error

**Solutions:**

1. **Check browser console:**
   ```
   F12 → Console tab
   Look for: "chartData is empty" or similar
   ```

2. **Verify data returned:**
   ```
   F12 → Network tab → Click analyze button
   Find: POST /analyze
   Response → Should show JSON with historical_data array
   ```

3. **Check symbol validity:**
   - Try known-good symbol: `AAPL`
   - Verify API is returning data

4. **Check date range:**
   - Some stocks have gaps in trading history
   - Adjust `LOOKBACK_DAYS` in config_dev.py

**Verify Fix:**
Charts should populate with price data immediately after analysis

---

## Sentiment Analysis Problems

### No Sentiment Data for Stock

**Message:**
```
Sentiment: Not available
No recent news articles found
```

**Is this a bug?** No - this is expected behavior!

**Cause:** Stock genuinely has no recent news coverage

**Explanation:**
- **v4.0 uses REAL NEWS ONLY** (no mock data)
- Some stocks have limited media coverage:
  - Small-cap stocks
  - International stocks (CBA.AX, etc.)
  - Low-volume tickers
- System correctly returns "No data" instead of fake sentiment

**Stocks with GOOD news coverage:**
- US Large Caps: `AAPL`, `TSLA`, `MSFT`, `GOOGL`, `AMZN`
- High-profile: `NVDA`, `META`, `NFLX`, `AMD`
- Hot stocks: Recently in news (check Google News first)

**Stocks with LIMITED coverage:**
- Small caps (< $1B market cap)
- International stocks (outside US)
- ETFs and index funds
- Penny stocks

**Verify not a bug:**
1. Try `AAPL` → Should return 5-10 articles
2. Try `TSLA` → Should return 5-10 articles
3. Try `CBA.AX` → May return 0 articles (expected)

**If major US stocks also return no data → Real issue:**
- Check internet connection
- Check sentiment_cache.log for errors
- Verify news sources accessible

---

### Sentiment Analysis Very Slow

**Symptom:**
- Analysis hangs at "Analyzing sentiment..."
- Takes 30+ seconds even for cached symbols

**Cause:** First-time FinBERT model download

**Solutions:**

1. **First run patience:**
   - FinBERT model is ~500 MB
   - Downloads to `~/.cache/huggingface/`
   - Only downloads once (then cached)
   - Can take 10-20 minutes on first analysis

2. **Check download progress:**
   ```cmd
   type sentiment_cache.log
   ```
   Look for: "Downloading FinBERT model..."

3. **Verify cache location:**
   ```cmd
   dir %USERPROFILE%\.cache\huggingface\hub
   ```
   Should show: `models--ProsusAI--finbert`

4. **Manual pre-download:**
   ```python
   python
   >>> from transformers import AutoModelForSequenceClassification
   >>> model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
   ```
   Wait for download to complete, then exit

**Subsequent analyses should be fast (5-10 seconds)**

**Verify Fix:**
- First analysis: 30+ seconds (downloading model)
- Second analysis: 5-10 seconds (using cache)

---

### "Mock Sentiment" or Fake Data Detected

**Symptom:**
- Sentiment returns same value for different stocks
- News articles look generated/fake
- "Generated by hash" in logs

**This should NOT happen in v4.0!**

**Verification:**
Run test script to confirm real news:
```cmd
cd FinBERT_v4.0_Development
python test_news_scraping_simple.py
```

**Expected output:**
```
Testing: AAPL
  Articles: 9
  Sources: Real news from Finviz
  Example: "Apple Reports Record Q4 Earnings"

Testing: TSLA  
  Articles: 9
  Sources: Real news from Finviz
  Example: "Tesla Deliveries Beat Expectations"

Testing: CBA.AX
  Articles: 0
  Message: "No recent news found"
  NO FAKE DATA! ✓
```

**If seeing mock data:**
1. Check you're using v4.0 (not older version)
2. Verify `news_sentiment_real.py` exists in models/
3. Check app uses real news module:
   ```python
   # In app_finbert_v4_dev.py, should see:
   from models.news_sentiment_real import get_sentiment_sync
   ```
4. Verify no `get_mock_sentiment()` calls

**Files to check:**
- ❌ OLD: `finbert_sentiment.py` with `get_mock_sentiment()` method
- ✅ NEW: `news_sentiment_real.py` with real scraping

---

## Performance Issues

### High Memory Usage

**Symptom:**
- System becomes slow after running for hours
- Memory usage grows over time
- Eventually crashes with "Out of memory"

**Cause:** Model caching in memory, memory leaks

**Solutions:**

1. **Restart server periodically:**
   ```cmd
   CTRL+C (stop server)
   START_FINBERT_V4.bat (restart)
   ```

2. **Clear model cache:**
   ```cmd
   del /s /q %USERPROFILE%\.cache\huggingface\*
   ```
   Note: Models will re-download on next use

3. **Reduce batch size:**
   - Edit `config_dev.py`
   - Change: `LSTM_BATCH_SIZE = 16` (from 32)

4. **Increase system RAM:**
   - Minimum: 8 GB
   - Recommended: 16 GB

5. **Close other applications:**
   - Free up memory before analysis
   - Close browser tabs not in use

**Verify Fix:**
- Check Task Manager → Memory usage
- Should be < 2 GB for typical operation

---

### Slow First Analysis

**Symptom:**
- First stock analysis takes 5+ minutes
- Subsequent analyses are fast

**Cause:** Model downloads on first use (expected behavior)

**What's downloading:**
1. FinBERT model (~500 MB) - Sentiment analysis
2. News scraping (first requests) - Building cache
3. LSTM model initialization - Neural network setup

**Timeline:**
- 0-10 minutes: Downloading FinBERT model
- 10-15 minutes: Fetching historical data
- 15-20 minutes: Training LSTM (if enabled)
- Done: Subsequent analyses cached and fast

**Solutions:**
1. **Be patient on first run** (this is normal)
2. **Pre-download models** (see installation guide)
3. **Use MINIMAL install** (skip ML models entirely)

**Verify normal operation:**
- First analysis: 20-30 minutes (with downloads)
- Second analysis (same stock): < 5 seconds (cached)
- Third analysis (different stock): 5-10 seconds (models cached)

---

### CPU at 100% During Analysis

**Symptom:**
- CPU usage spikes to 100%
- Computer becomes unresponsive
- Fan runs at full speed

**Cause:** TensorFlow/PyTorch using all available cores (expected)

**Is this normal?** Yes, for ML operations!

**Solutions:**

1. **Limit CPU cores (advanced):**
   ```python
   # Add to config_dev.py
   import os
   os.environ['OMP_NUM_THREADS'] = '4'  # Use only 4 cores
   ```

2. **Run in background:**
   - Start analysis
   - Switch to other tasks
   - Check back when complete

3. **Use GPU (if available):**
   - TensorFlow can use NVIDIA GPU
   - Reduces CPU load significantly
   - Install: `pip install tensorflow-gpu`

4. **Upgrade CPU:**
   - Minimum: 4 cores
   - Recommended: 8 cores
   - Ideal: 16 cores with AVX support

**Verify normal:**
- CPU at 100% during analysis: Normal
- CPU returns to idle after: Normal
- CPU stays at 100% indefinitely: Problem (check for infinite loop)

---

## Network and Connection Errors

### Connection Timeout

**Error:**
```
requests.exceptions.ConnectTimeout
Connection to finance.yahoo.com timed out
```

**Cause:** Network issue or Yahoo Finance API down

**Solutions:**

1. **Check internet connection:**
   ```cmd
   ping google.com
   ping finance.yahoo.com
   ```

2. **Check Yahoo Finance status:**
   - Visit: https://finance.yahoo.com/
   - If site loads → API should work
   - If site down → Wait for restoration

3. **Increase timeout:**
   - Edit `news_sentiment_real.py`
   - Find: `timeout=10`
   - Change to: `timeout=30`

4. **Use VPN (if geo-blocked):**
   - Some regions block Yahoo Finance
   - Connect to US VPN server
   - Retry analysis

5. **Check firewall:**
   - Corporate firewall may block Yahoo
   - Whitelist: `*.yahoo.com`, `*.finviz.com`

**Verify Fix:**
```python
python
>>> import yfinance as yf
>>> ticker = yf.Ticker("AAPL")
>>> hist = ticker.history(period="1d")
>>> print(hist)
```
Should return data without timeout

---

### Rate Limiting

**Error:**
```
429 Too Many Requests
Rate limit exceeded
```

**Cause:** Too many API requests in short time

**Solutions:**

1. **Wait 15 minutes:**
   - Rate limits reset after time
   - Don't retry immediately

2. **Use cache:**
   - v4.0 has 15-minute cache
   - Re-analyzing same stock uses cache (no API call)

3. **Reduce request frequency:**
   - Don't analyze 100 stocks in rapid succession
   - Add delays between analyses

4. **Check cache working:**
   ```cmd
   type sentiment_cache.db
   ```
   Should exist and have recent modification time

**Verify Fix:**
Second analysis of same stock should be instant (cached)

---

## Windows-Specific Issues

### Antivirus Blocking Python

**Symptom:**
- pip install fails with "Access denied"
- Python script won't run
- "Windows Defender blocked this app"

**Cause:** Antivirus flagging Python as potential threat

**Solutions:**

1. **Add Python to exceptions:**
   - Windows Security → Virus & threat protection
   - Manage settings → Exclusions → Add exclusion
   - Add folder: `C:\Python39\` (or your Python path)
   - Add folder: `C:\Users\YourName\FinBERT_v4.0_Windows11_Deployment\`

2. **Temporarily disable real-time protection:**
   - Windows Security → Virus & threat protection
   - Manage settings → Real-time protection → OFF
   - Run installation
   - Turn back ON

3. **Use different antivirus:**
   - Some antivirus software overly aggressive
   - Consider switching or adjusting sensitivity

**Verify Fix:**
```cmd
python --version
pip install requests
```
Should work without "Access denied" errors

---

### Long Path Error

**Error:**
```
OSError: [Errno 36] File name too long
FileNotFoundError: [WinError 206] The filename or extension is too long
```

**Cause:** Windows has 260-character path limit (by default)

**Solutions:**

1. **Enable long paths:**
   - Open Registry Editor (regedit)
   - Navigate to: `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem`
   - Set: `LongPathsEnabled` = 1
   - Restart computer

2. **Extract to shorter path:**
   - Instead of: `C:\Users\VeryLongUserName\Downloads\Projects\FinBERT_v4.0_Windows11_Deployment\`
   - Use: `C:\FinBERT\`

3. **Use subst (virtual drive):**
   ```cmd
   subst F: "C:\Users\YourName\VeryLongPath\FinBERT_v4.0_Windows11_Deployment"
   cd F:\
   ```

**Verify Fix:**
Installation should proceed without path errors

---

### Windows Defender SmartScreen Warning

**Warning:**
```
Windows protected your PC
Microsoft Defender SmartScreen prevented an unrecognized app from starting
```

**Cause:** .bat scripts from internet flagged as potentially unsafe

**Is this dangerous?** No - our scripts are safe

**Solutions:**

1. **Click "More info" → "Run anyway"**
   - This is safe for our scripts
   - Windows just being cautious with downloaded scripts

2. **Verify script contents first:**
   - Right-click `START_FINBERT_V4.bat` → Edit
   - Review code (should be readable commands)
   - If looks safe → Run anyway

3. **Run commands manually:**
   - Instead of .bat file, copy commands
   - Paste into Command Prompt
   - Execute one by one

**Verify Fix:**
Scripts should run after clicking "Run anyway"

---

## Advanced Troubleshooting

### Enable Debug Logging

Add to `config_dev.py`:
```python
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='finbert_debug.log'
)
```

Restart server, then check logs:
```cmd
type finbert_debug.log
```

### Test Individual Components

**Test stock data fetching:**
```python
python
>>> import yfinance as yf
>>> ticker = yf.Ticker("AAPL")
>>> hist = ticker.history(period="1mo")
>>> print(hist.head())
```

**Test sentiment analysis:**
```python
python
>>> from models.news_sentiment_real import get_sentiment_sync
>>> result = get_sentiment_sync("AAPL")
>>> print(result)
```

**Test LSTM predictions:**
```python
python
>>> from models.lstm_predictor import LSTMPredictor
>>> predictor = LSTMPredictor()
>>> # Load test data and predict
```

### Check Dependencies

```cmd
pip check
```
Should report: "No broken requirements found."

If issues found:
```cmd
pip install --upgrade --force-reinstall <package_name>
```

### Reinstall from Scratch

If all else fails:

1. **Backup data** (if any):
   ```cmd
   copy sentiment_cache.db backup_sentiment_cache.db
   ```

2. **Delete virtual environment:**
   ```cmd
   rmdir /s /q venv
   ```

3. **Delete cache:**
   ```cmd
   del /s /q %USERPROFILE%\.cache\huggingface\
   ```

4. **Reinstall:**
   ```cmd
   scripts\INSTALL_WINDOWS11.bat
   ```

---

## Getting Further Help

### Collect Diagnostic Information

Before seeking help, collect:

1. **System info:**
   ```cmd
   systeminfo | findstr /B /C:"OS Name" /C:"OS Version" /C:"System Type"
   python --version
   pip --version
   ```

2. **Installed packages:**
   ```cmd
   pip list > installed_packages.txt
   ```

3. **Error logs:**
   ```cmd
   type sentiment_cache.log > logs.txt
   type finbert_debug.log >> logs.txt
   ```

4. **Browser console (if chart issues):**
   - Press F12 → Console tab
   - Screenshot any errors

### Where to Get Help

1. **Check documentation:**
   - README.md
   - INSTALLATION_GUIDE.md
   - USER_GUIDE.md

2. **Review error logs:**
   - sentiment_cache.log
   - finbert_debug.log

3. **Search similar issues:**
   - Google the exact error message
   - Check StackOverflow

4. **Project repository:**
   - Check GitHub issues
   - Review recent commits
   - Check release notes

---

## Quick Reference: Error Messages

| Error Message | Cause | Solution |
|---------------|-------|----------|
| `python not recognized` | Python not in PATH | Add to PATH or reinstall |
| `SSL: CERTIFICATE_VERIFY_FAILED` | SSL/firewall issue | Update certifi or use trusted hosts |
| `Could not build wheels` | Missing C++ tools | Install Visual C++ Redistributable |
| `Address already in use` | Port conflict | Kill process or change port |
| `ModuleNotFoundError` | Missing package | Activate venv and install |
| `Symbol not found` | Invalid ticker | Verify symbol on Yahoo Finance |
| `No recent news` | Limited coverage | Try different symbol (not a bug!) |
| `echarts is not defined` | CDN blocked | Check network/firewall |
| `Connection timeout` | Network issue | Check internet and Yahoo status |
| `429 Too Many Requests` | Rate limited | Wait 15 minutes, use cache |
| `File name too long` | Path limit | Enable long paths or use shorter path |
| `Windows protected your PC` | SmartScreen warning | Click "Run anyway" |

---

**Still stuck?** Re-read the relevant section above for detailed solutions!
