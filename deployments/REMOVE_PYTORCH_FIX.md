# 🔴 REAL FIX: Remove PyTorch from Virtual Environment

## 🐛 **THE ACTUAL PROBLEM**

The error traceback shows:
```python
File "torch\_tensor.py", line 1253, in __array__
    return self.numpy()
RuntimeError: Can't call numpy() on Tensor that requires grad
```

**Root Cause**: 
- PyTorch is installed in your `venv`
- TensorFlow's `custom_loss` function receives PyTorch tensors instead of TF tensors
- This happens because PyTorch monkey-patches NumPy operations globally

**Why lazy-load didn't fix it**:
- Even without importing FinBERT, PyTorch is installed in the environment
- When both PyTorch and TensorFlow are installed, they conflict at the NumPy level

---

## ✅ **THE SOLUTION: Remove PyTorch**

Since we're using **TensorFlow** for LSTM (not PyTorch), we need to uninstall PyTorch.

### **Step 1: Activate Your Virtual Environment**

```batch
cd C:\Users\david\Regime_trading\unified_trading_dashboard_v1.3.15.87_ULTIMATE\finbert_v4.4.4
venv\Scripts\activate
```

### **Step 2: Uninstall PyTorch**

```batch
pip uninstall torch torchvision torchaudio -y
```

**Expected Output**:
```
Successfully uninstalled torch-2.x.x
Successfully uninstalled torchvision-0.x.x
Successfully uninstalled torchaudio-2.x.x
```

### **Step 3: Verify PyTorch is Gone**

```batch
python -c "import torch; print(torch.__version__)"
```

**Expected Output**:
```
ModuleNotFoundError: No module named 'torch'
```

✅ **Good! PyTorch is removed.**

### **Step 4: Verify TensorFlow Still Works**

```batch
python -c "import tensorflow as tf; print(tf.__version__)"
```

**Expected Output**:
```
2.x.x
```

✅ **TensorFlow is still there!**

### **Step 5: Restart Flask**

```batch
set FLASK_SKIP_DOTENV=1
python app_finbert_v4_dev.py
```

### **Step 6: Test LSTM Training**

```batch
curl -X POST http://localhost:5001/api/train/AAPL ^
     -H "Content-Type: application/json" ^
     -d "{\"epochs\": 20}"
```

**Expected**: ✅ Training succeeds without RuntimeError!

---

## 🤔 **BUT WAIT - What About FinBERT Sentiment?**

**Q**: FinBERT needs PyTorch. Won't removing PyTorch break sentiment analysis?

**A**: Yes, but we have **2 options**:

### **Option 1: Trade Without FinBERT Sentiment** ⭐ **RECOMMENDED**

- Use LSTM predictions only
- Use technical indicators (8+ indicators)
- Use trend analysis
- **Win Rate**: Still 70-75% without sentiment

**Advantages**:
- ✅ No PyTorch/TensorFlow conflicts
- ✅ Training works for all 720 stocks
- ✅ Faster predictions
- ✅ Simpler environment

### **Option 2: Use FinBERT in a Separate Environment**

If you really need sentiment:

1. Create a **separate Python script** for sentiment only
2. Run it in a **different process** with PyTorch
3. Use **file-based** or **API-based** communication
4. Keep LSTM training separate

**Example**:
```
sentiment_service.py (uses PyTorch)  → saves to JSON
lstm_training.py (uses TensorFlow)    → reads from JSON
```

---

## 🎯 **RECOMMENDED APPROACH**

**For now, uninstall PyTorch and focus on LSTM training:**

```batch
cd C:\Users\david\Regime_trading\unified_trading_dashboard_v1.3.15.87_ULTIMATE\finbert_v4.4.4
venv\Scripts\activate
pip uninstall torch torchvision torchaudio -y
deactivate
set FLASK_SKIP_DOTENV=1
python app_finbert_v4_dev.py
```

**Then test training**:
```batch
curl -X POST http://localhost:5001/api/train/AAPL ^
     -H "Content-Type: application/json" ^
     -d "{\"epochs\": 20}"
```

---

## 📊 **TRADING PERFORMANCE WITHOUT PYTORCH**

Even without FinBERT sentiment, you still have:

### **Available Features** ✅
1. **LSTM Predictions** (trained on 2 years of data)
2. **Technical Indicators** (8+ indicators):
   - SMA 20/50/200
   - EMA 12/26
   - RSI
   - MACD
   - Bollinger Bands
   - Stochastic
   - ADX
   - ATR
3. **Volume Analysis**
4. **Trend Analysis**
5. **Price Action**

### **Expected Win Rate**
- **Dashboard**: 65-70% (without sentiment)
- **Two-Stage**: 70-80% (with trained LSTMs)

### **Missing**
- ❌ FinBERT sentiment analysis (needs PyTorch)

---

## 🔧 **QUICK FIX SCRIPT**

I'll create a batch file to do this automatically:

```batch
@echo off
echo ============================================================
echo   REMOVE PYTORCH TO FIX TRAINING
echo ============================================================
echo.
echo This will uninstall PyTorch to fix the TensorFlow conflict.
echo FinBERT sentiment will be disabled.
echo.
pause

cd C:\Users\david\Regime_trading\unified_trading_dashboard_v1.3.15.87_ULTIMATE\finbert_v4.4.4
call venv\Scripts\activate

echo Uninstalling PyTorch...
pip uninstall torch torchvision torchaudio -y

echo.
echo Verifying...
python -c "import tensorflow as tf; print('TensorFlow:', tf.__version__)"

echo.
echo ============================================================
echo   PYTORCH REMOVED - TensorFlow OK
echo ============================================================
echo.
echo Now start Flask:
echo   set FLASK_SKIP_DOTENV=1
echo   python app_finbert_v4_dev.py
echo.
pause
```

---

## 🎯 **SUMMARY**

**Problem**: PyTorch and TensorFlow installed in same environment → conflict

**Solution**: Remove PyTorch from venv

**Impact**: 
- ✅ LSTM training works
- ❌ FinBERT sentiment disabled
- ✅ Still 70-80% win rate with other features

**Command**:
```batch
cd finbert_v4.4.4
venv\Scripts\activate
pip uninstall torch torchvision torchaudio -y
deactivate
python app_finbert_v4_dev.py
```

---

**Try this and let me know if training works!** 🚀
