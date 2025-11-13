# 🔧 TROUBLESHOOTING: flask-cors Module Not Found

**Error Message:**
```
ModuleNotFoundError: No module named 'flask_cors'
```

---

## ✅ QUICK FIX (Most Common Solution)

The issue is that the `flask-cors` package needs to be installed in your Python environment. Here's how to fix it:

### **Windows:**

```batch
# Step 1: Navigate to your FinBERT directory
cd C:\Users\david\AOPT\FinBERT_v4.4_PHASE1_PAPER_TRADING_DEPLOY

# Step 2: Activate virtual environment (if you have one)
venv\Scripts\activate

# Step 3: Install flask-cors directly
pip install flask-cors

# Step 4: Start the server
python app_finbert_v4_dev.py
```

### **Alternative: Reinstall All Requirements**

If the quick fix doesn't work, reinstall all dependencies:

```batch
# Make sure you're in the FinBERT directory
cd C:\Users\david\AOPT\FinBERT_v4.4_PHASE1_PAPER_TRADING_DEPLOY

# Activate virtual environment (if you have one)
venv\Scripts\activate

# Upgrade pip first
python -m pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt

# Verify flask-cors is installed
pip show flask-cors

# Start the server
python app_finbert_v4_dev.py
```

---

## 🔍 DIAGNOSTIC STEPS

### 1. Check if requirements.txt has flask-cors

Open `requirements.txt` and verify line 5 contains:
```
flask-cors>=4.0.0
```

✅ **If YES**: Proceed to step 2
❌ **If NO**: You have an old version. Download the fixed ZIP file.

### 2. Check which Python environment you're using

```batch
# Show Python location
where python

# Show pip location
where pip

# List installed packages
pip list
```

Look for `Flask-CORS` in the output. If it's missing, that's your problem.

### 3. Verify virtual environment activation

```batch
# Windows - Check if activated
echo %VIRTUAL_ENV%

# If empty, activate it:
venv\Scripts\activate

# Then check again
echo %VIRTUAL_ENV%
```

---

## 🚀 NUCLEAR OPTION (If nothing else works)

Delete everything and start fresh:

```batch
# Step 1: Create a NEW virtual environment
python -m venv venv_new

# Step 2: Activate it
venv_new\Scripts\activate

# Step 3: Upgrade pip
python -m pip install --upgrade pip

# Step 4: Install requirements
pip install -r requirements.txt

# Step 5: Verify installation
pip show flask-cors

# Step 6: Start server
python app_finbert_v4_dev.py
```

---

## 📝 MANUAL VERIFICATION CHECKLIST

Before running the server, verify:

- [ ] I am in the correct directory (`FinBERT_v4.4_PHASE1_PAPER_TRADING_DEPLOY`)
- [ ] My `requirements.txt` contains `flask-cors>=4.0.0`
- [ ] I have activated my virtual environment (if using one)
- [ ] I ran `pip install -r requirements.txt`
- [ ] I can see `Flask-CORS` when running `pip list`
- [ ] My Python version is 3.8 or higher (`python --version`)

---

## 🆘 STILL NOT WORKING?

If you've tried everything above and still get the error:

### Option A: Install minimal dependencies only

```batch
pip install flask flask-cors yfinance pandas numpy requests ta
python app_finbert_v4_dev.py
```

### Option B: Use system Python (without virtual environment)

```batch
# Deactivate venv if active
deactivate

# Install globally
pip install flask-cors

# Run server
python app_finbert_v4_dev.py
```

### Option C: Check for conflicts

```batch
# Uninstall flask-cors
pip uninstall flask-cors -y

# Reinstall with specific version
pip install flask-cors==4.0.1

# Try again
python app_finbert_v4_dev.py
```

---

## 📞 REPORT BACK

After trying the fixes, please report:

1. **Which fix worked?** (Quick Fix / Reinstall / Nuclear Option)
2. **Output of:** `pip show flask-cors`
3. **Output of:** `python --version`
4. **Did the server start?** YES / NO

This will help improve the installation process for future users.

---

## ✨ SUCCESS INDICATOR

When everything is working, you should see:

```
================================================================================
  FinBERT v4.4 - Starting Server
  Phase 1: Enhanced Accuracy + Paper Trading
================================================================================

 * Serving Flask app 'app_finbert_v4_dev'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment.
 * Running on http://127.0.0.1:8050
Press CTRL+C to quit
```

Then open your browser to: **http://127.0.0.1:8050**

---

**Last Updated:** November 5, 2025  
**Hotfix Version:** d5980be
