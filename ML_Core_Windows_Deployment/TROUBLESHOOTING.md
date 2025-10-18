# 🔧 Troubleshooting Guide - ML Core Enhanced with Sentiment

## Common Issues and Solutions

---

## 🚫 Issue: "ML Learning Frozen" / Interface Not Responding

### Symptoms:
- Browser console shows: `updateCacheStats @ ml_core_enhanced_interface.html:1227`
- Interface freezes when loading
- Training doesn't start or complete

### Solutions:

#### 1. **Server Not Running**
Check if the server is running:
```cmd
curl http://localhost:8000/
```
If no response, restart the server:
```cmd
run_ml_core.bat
```

#### 2. **Cache Stats Endpoint Issue**
The interface tries to fetch cache statistics on load. If this fails:
- Open browser console (F12)
- Check for network errors
- The interface now has a 5-second timeout to prevent freezing

#### 3. **Use Updated Interface**
Make sure you have the latest `ml_core_enhanced_interface.html` with timeout fixes

---

## ❌ Issue: Prediction Error - "0 samples required by StandardScaler"

### Cause:
Not enough historical data to calculate all 36 features (including 50-day moving averages)

### Solutions:

#### 1. **Train with More Data**
```powershell
# Use 252 days (1 year) for full feature calculation
Invoke-RestMethod -Uri "http://localhost:8000/api/train" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"symbol": "AAPL", "ensemble_type": "voting", "days": 252}'
```

#### 2. **Run Fix Script**
```cmd
python fix_prediction_windows.py
```

---

## 🐢 Issue: Slow Training / Long Install Time

### Cause:
First-time sentiment model download (transformer models can be large)

### Solutions:

#### 1. **First Install is Slow**
- FinBERT model download: ~400MB
- PyTorch installation: ~2GB
- This only happens once

#### 2. **Skip Sentiment If Needed**
If you don't need sentiment analysis:
- Comment out `from comprehensive_sentiment_analyzer import sentiment_analyzer`
- System will use neutral sentiment (0.5)

#### 3. **Use Lighter Requirements**
Create `requirements_minimal.txt` without transformers:
```txt
scikit-learn>=1.3.0
pandas>=2.0.0
numpy>=1.24.0
fastapi>=0.103.0
uvicorn[standard]>=0.23.0
yfinance>=0.2.28
```

---

## ⚠️ Issue: "Module transformers not found"

### Cause:
Sentiment analysis dependencies not installed

### Solutions:

#### 1. **Install Transformers**
```cmd
pip install transformers torch
```

#### 2. **Use Full Requirements**
```cmd
pip install -r requirements.txt
```

#### 3. **Skip Sentiment**
The system works without sentiment - it will use 0.5 (neutral) automatically

---

## 🔴 Issue: Port 8000 Already in Use

### Solutions:

#### 1. **Find Process Using Port**
```cmd
netstat -ano | findstr :8000
```

#### 2. **Kill Process**
```cmd
taskkill /PID [process_id] /F
```

#### 3. **Change Port**
Edit `ml_core_enhanced_production.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8080)  # Change to 8080
```

---

## 📉 Issue: Poor Prediction Accuracy

### Causes:
- Insufficient training data
- Market conditions changed
- Model needs retraining

### Solutions:

#### 1. **Retrain with Recent Data**
```powershell
# Train with fresh data
$symbols = @("AAPL", "MSFT", "GOOGL", "AMZN")
foreach ($symbol in $symbols) {
    Invoke-RestMethod -Uri "http://localhost:8000/api/train" `
      -Method Post `
      -ContentType "application/json" `
      -Body "{`"symbol`": `"$symbol`", `"ensemble_type`": `"voting`", `"days`": 480}"
}
```

#### 2. **Check Sentiment Score**
Low sentiment might indicate challenging market conditions

#### 3. **Increase Training Days**
More historical data can improve accuracy

---

## 💾 Issue: Database Errors

### Solutions:

#### 1. **Reset Databases**
```cmd
del *.db
```
Then restart - databases will recreate

#### 2. **Check Disk Space**
ML models can grow large (20MB+)

---

## 🌐 Issue: No Internet / Yahoo Finance Down

### Symptoms:
- Can't fetch stock data
- Training fails immediately

### Solutions:

#### 1. **Check Connection**
```cmd
ping finance.yahoo.com
```

#### 2. **Use Cached Data**
System caches data for 12 hours - can work offline temporarily

#### 3. **Alternative Data Source**
Could modify to use Alpha Vantage or other APIs

---

## 🔥 Issue: High CPU/Memory Usage

### Solutions:

#### 1. **Reduce Ensemble Models**
Use only RandomForest instead of all 5 models

#### 2. **Reduce Training Days**
Use 180 days instead of 480

#### 3. **Close Other Applications**
ML training needs resources

---

## 📊 Issue: Sentiment Analysis Not Working

### Symptoms:
- Sentiment always shows 0.5
- Warning: "Sentiment analyzer not available"

### Solutions:

#### 1. **Check Installation**
```python
from comprehensive_sentiment_analyzer import sentiment_analyzer
print(sentiment_analyzer.calculate_comprehensive_sentiment("AAPL"))
```

#### 2. **Install Dependencies**
```cmd
pip install transformers torch yfinance requests
```

#### 3. **Check Data Access**
Sentiment needs internet for:
- VIX data
- Treasury yields
- Global indices
- Earnings data

---

## 🆘 Quick Diagnostic Script

Save as `diagnose.py`:
```python
import sys
print("Python:", sys.version)

try:
    import sklearn
    print("✓ scikit-learn:", sklearn.__version__)
except:
    print("✗ scikit-learn not installed")

try:
    import fastapi
    print("✓ FastAPI installed")
except:
    print("✗ FastAPI not installed")

try:
    import yfinance
    print("✓ yfinance installed")
except:
    print("✗ yfinance not installed")

try:
    import transformers
    print("✓ Transformers installed (sentiment available)")
except:
    print("⚠ Transformers not installed (sentiment disabled)")

try:
    import requests
    r = requests.get("http://localhost:8000/")
    print("✓ Server running")
except:
    print("✗ Server not responding")

print("\nRun 'pip install -r requirements.txt' to install missing packages")
```

---

## 📞 Support Resources

- **GitHub Issues**: Report bugs at the repository
- **Documentation**: Check README_WINDOWS.md
- **Sentiment Guide**: See SENTIMENT_FEATURE_README.md
- **Test System**: Run `test_system.bat`

---

## ✅ Prevention Tips

1. **Always run in virtual environment**
2. **Keep 5GB free disk space**
3. **Use stable internet connection**
4. **Update packages monthly**
5. **Backup trained models regularly**
6. **Monitor system resources**
7. **Check logs in console for errors**

---

Remember: The system is designed to handle failures gracefully. If sentiment fails, it uses neutral (0.5). If training fails, previous models still work.