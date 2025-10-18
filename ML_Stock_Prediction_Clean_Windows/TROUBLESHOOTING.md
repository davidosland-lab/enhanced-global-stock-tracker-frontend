# 🔧 Troubleshooting Guide

## ❌ Yahoo Finance Connection Error

### Problem:
```
ERROR - Failed to get ticker 'AAPL' reason: Expecting value: line 1 column 1 (char 0)
ERROR - AAPL: No price data found, symbol may be delisted
```

### Solutions:

#### Solution 1: Test Connection
Run `5_test_connection.bat` to diagnose the issue.

#### Solution 2: Use Sample Data (Quick Fix)
1. Run `6_generate_sample_data.bat` to create test data
2. This generates realistic stock data for testing
3. The system will work with this data for development/testing

#### Solution 3: Check Network
- **Firewall/Antivirus**: May be blocking Yahoo Finance
- **Corporate Network**: Often blocks financial APIs
- **Try Different Network**: Use mobile hotspot or home network

#### Solution 4: Use VPN
Yahoo Finance may be blocked in your region or network.
Try using a VPN connected to US servers.

#### Solution 5: Alternative Data Sources

**Alpha Vantage (Free)**
1. Get API key: https://www.alphavantage.co/support/#api-key
2. Install: `pip install alpha-vantage`
3. Modify ml_core.py to use Alpha Vantage

**IEX Cloud (Free Tier)**
1. Sign up: https://iexcloud.io/
2. Install: `pip install pyEX`
3. Modify ml_core.py to use IEX

#### Solution 6: Manual Fix for yfinance
Sometimes yfinance needs updating:
```cmd
pip install --upgrade yfinance
```

Or try the development version:
```cmd
pip install git+https://github.com/ranaroussi/yfinance.git
```

## ⚠️ Port 8000 Already in Use

### Solution:
1. Edit `config.py`
2. Change `PORT = 8000` to `PORT = 8001` (or any free port)
3. Access at http://localhost:8001 instead

## 💾 Memory Issues

### Solution:
1. Keep `USE_SENTIMENT = False` in config.py
2. Close other applications
3. Reduce `DEFAULT_TRAINING_DAYS` in config.py

## 🐍 Python Version Issues

### If you have Python 3.12:
The included requirements.txt should work.

### If you have Python 3.10 or 3.11:
You can use the original numpy version:
```cmd
pip install numpy==1.24.3
```

## 📦 Installation Fails

### Missing packages:
```cmd
pip install --upgrade pip
pip install -r requirements.txt
```

### Permission errors:
Run Command Prompt as Administrator

## 🔄 System Won't Start

1. Run `2_test_system.bat` to check for issues
2. Run `4_quick_test.bat` for detailed diagnostics
3. Check console output for specific error messages

## 📊 No Predictions Showing

### Causes:
- Not enough training data (need 90+ days)
- Training failed
- Connection timeout

### Solutions:
1. Use sample data: Run `6_generate_sample_data.bat`
2. Train with more days: Increase training period
3. Check console for training errors

## 🌐 API Timeout Errors

### Solution:
Edit `config.py` and increase timeouts:
```python
REQUEST_TIMEOUT = 30  # Increase from 10
TRAINING_TIMEOUT = 120  # Increase from 60
```

## 📈 Low Prediction Accuracy

### This is normal because:
- Stock markets are inherently unpredictable
- 55-75% accuracy is actually good for stock prediction
- External factors affect markets that ML can't predict

### To improve:
1. Use more training data (180+ days)
2. Train more frequently (daily/weekly)
3. Enable sentiment analysis (requires more resources)

## 🔍 Diagnostic Tools

We've included several diagnostic tools:

1. **`2_test_system.bat`** - Basic system check
2. **`4_quick_test.bat`** - Detailed package testing
3. **`5_test_connection.bat`** - Yahoo Finance connectivity
4. **`diagnostic.py`** - Full system diagnostic

Run these in order to identify issues.

## 💡 Still Having Issues?

1. **Document the error**: Copy the full error message
2. **Check versions**: Run `python --version` and `pip list`
3. **Try sample data**: Use `6_generate_sample_data.bat` to bypass Yahoo Finance
4. **Restart**: Sometimes a fresh start helps:
   - Close all Command Prompts
   - Restart your computer
   - Try again

## ✅ Working Confirmation

You'll know it's working when:
1. `4_quick_test.bat` shows "ALL TESTS PASSED!"
2. Server starts without errors
3. Web interface loads at http://localhost:8000
4. You can train a model and get predictions

---

**Remember**: The Yahoo Finance issue is common and doesn't mean the system is broken. Use the sample data generator to test the ML functionality!