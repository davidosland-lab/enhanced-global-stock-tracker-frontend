# Troubleshooting: Flask-CORS Import Error

## Problem

You see this error when starting the server:

```
ModuleNotFoundError: No module named 'flask_cors'
```

## Root Cause

The `flask-cors` package was not installed during the initial setup. This happened because the original `INSTALL.bat` was hardcoding package names instead of using `requirements.txt`.

## Quick Fix

Run the emergency fix script:

```batch
FIX_FLASK_CORS.bat
```

This will:
1. Activate your virtual environment
2. Install flask-cors>=4.0.0
3. Verify the installation

## Manual Fix

If the automatic fix doesn't work, try these steps:

### Option 1: Install flask-cors directly

```batch
# Activate virtual environment
venv\Scripts\activate.bat

# Install flask-cors
pip install flask-cors>=4.0.0

# Verify
python -c "import flask_cors; print('OK')"
```

### Option 2: Reinstall all dependencies

```batch
# Activate virtual environment
venv\Scripts\activate.bat

# Upgrade pip
python -m pip install --upgrade pip

# Install all dependencies from requirements.txt
pip install -r requirements.txt

# Verify
python diagnose_environment.py
```

### Option 3: Force reinstall

```batch
# Activate virtual environment
venv\Scripts\activate.bat

# Force reinstall flask-cors
pip install flask-cors --force-reinstall

# Verify
python -c "import flask_cors; print('OK')"
```

## Verification

After fixing, verify the installation:

```batch
VERIFY_INSTALL.bat
```

You should see:

```
[OK] flask-cors            Installed
```

## Why This Happened

The original `INSTALL.bat` had this line:

```batch
pip install flask yfinance pandas numpy ta transformers torch scikit-learn apscheduler
```

This hardcoded list was missing:
- flask-cors
- requests
- keras
- tensorflow
- python-dateutil
- pytz

The **FIXED** `INSTALL.bat` now properly uses:

```batch
pip install -r requirements.txt
```

This ensures ALL dependencies from `requirements.txt` are installed, including `flask-cors`.

## Prevention

To avoid this in the future:

1. **Always use requirements.txt**: Never hardcode package lists
2. **Run VERIFY_INSTALL.bat**: After installation, verify all packages
3. **Check requirements.txt**: Make sure flask-cors>=4.0.0 is listed

## Related Issues

If you continue to have problems:

1. **Check Python version**: Requires Python 3.8+
   ```batch
   python --version
   ```

2. **Check virtual environment**: Make sure you're in the venv
   ```batch
   where python
   # Should show: C:\...\FinBERT\venv\Scripts\python.exe
   ```

3. **Check pip version**: Update pip if needed
   ```batch
   python -m pip install --upgrade pip
   ```

4. **Check internet connection**: pip needs internet to download packages

5. **Check firewall/antivirus**: May block pip downloads

## Complete Reinstall

If nothing works, try a complete reinstall:

```batch
# Delete virtual environment
rmdir /s /q venv

# Run installation again
INSTALL.bat
```

## Still Having Issues?

Check these files for more information:

- `ROOT_CAUSE_ANALYSIS.md` - Detailed analysis of the bug
- `INSTALL.txt` - Complete installation guide
- `README.md` - Full system documentation

## Technical Details

### What is flask-cors?

Flask-CORS is a Flask extension for handling Cross-Origin Resource Sharing (CORS). It's required for the web interface to communicate with the API endpoints.

### Where is it used?

In `app_finbert_v4_dev.py`:

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
```

Without this, API calls from the browser will fail with CORS errors.

### Requirements.txt Entry

```txt
flask-cors>=4.0.0
```

This ensures version 4.0.0 or higher is installed.

## Summary

**Quick Fix:** Run `FIX_FLASK_CORS.bat`

**Manual Fix:** `pip install flask-cors>=4.0.0`

**Verify:** Run `VERIFY_INSTALL.bat`

**Root Cause:** INSTALL.bat was using hardcoded packages instead of requirements.txt (now fixed)
