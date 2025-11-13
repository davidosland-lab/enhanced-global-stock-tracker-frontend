# Windows Installation Troubleshooting Guide

## Common Issues and Solutions

### 1. Microsoft Visual C++ 14.0 Build Tools Error

**Problem**: Error message "Microsoft Visual C++ 14.0 or greater is required"

**Solutions**:

#### Option A: Install Pre-compiled Wheels (Recommended)
1. Run `INSTALL_WIN_COMPLETE.bat` instead of the basic installer
2. This script attempts to use pre-compiled wheels that don't require C++ tools

#### Option B: Install Visual C++ Build Tools
1. Download from: https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022
2. Run installer and select "Desktop development with C++"
3. After installation, restart your command prompt
4. Run the installer batch file again

#### Option C: Use Conda Instead of Pip
```bash
# Install Anaconda or Miniconda first, then:
conda install pandas numpy scikit-learn flask -c conda-forge
pip install yfinance flask-cors
```

---

### 2. JavaScript Errors in Browser

**Problem**: `TypeError: Cannot read properties of undefined (reading 'toFixed')`

**Solution**: This has been fixed in the latest version. Clear your browser cache:
- Chrome/Edge: Ctrl+Shift+Delete → Clear cached images and files
- Firefox: Ctrl+Shift+Delete → Clear Cache
- Then refresh the page with Ctrl+F5

---

### 3. Port 5000 Already in Use

**Problem**: "Port 5000 is in use by another program"

**Solutions**:

#### Find and stop the process:
```cmd
# Find what's using port 5000
netstat -ano | findstr :5000

# Kill the process (replace PID with actual number)
taskkill /PID <PID> /F
```

#### Or change the port in the app:
Edit `app_enhanced_sentiment_fixed.py` and change the last line:
```python
app.run(host='0.0.0.0', port=5001)  # Change 5000 to 5001
```

---

### 4. API 500 Internal Server Error

**Problem**: API endpoints return 500 errors

**Common Causes and Solutions**:

1. **Yahoo Finance Rate Limiting**
   - Wait a few minutes and try again
   - The app caches data for 5 minutes to reduce API calls

2. **Missing Dependencies**
   - Run `pip list` to verify all packages are installed
   - Reinstall missing packages

3. **Encoding Issues**
   - Make sure `FLASK_SKIP_DOTENV = '1'` is set in the app

---

### 5. Batch File Closes Immediately

**Problem**: Double-clicking .bat files closes window immediately

**Solution**: The batch files already have `pause` commands. If still closing:
1. Right-click → Edit the .bat file
2. Add `pause` at the very end
3. Save and try again
4. Or run from Command Prompt to see the error

---

### 6. Python Not Found

**Problem**: "'python' is not recognized as an internal or external command"

**Solutions**:

1. **Add Python to PATH** during installation:
   - Reinstall Python
   - Check "Add Python to PATH" during installation

2. **Manual PATH addition**:
   - Search "Environment Variables" in Windows
   - Add Python installation folder to PATH
   - Default: `C:\Users\<YourName>\AppData\Local\Programs\Python\Python311\`

3. **Use py launcher** (if installed):
   ```cmd
   py -3 app_enhanced_sentiment_fixed.py
   ```

---

### 7. Import Errors After Installation

**Problem**: "ModuleNotFoundError: No module named 'sklearn'"

**Solutions**:

1. **Virtual Environment Not Activated**:
   ```cmd
   venv\Scripts\activate
   pip install -r requirements_sentiment.txt
   ```

2. **Multiple Python Versions**:
   - Use `python -m pip` instead of just `pip`
   - Check Python version: `python --version`

---

### 8. Australian Stock Symbols Not Working

**Problem**: CBA, BHP, etc. return no data

**Solution**: The app automatically adds .AX suffix for Australian stocks. If not working:
- Try manually adding .AX (e.g., CBA.AX)
- Check if Yahoo Finance has the data: https://finance.yahoo.com/quote/CBA.AX

---

## Quick Test Commands

Run these in Command Prompt to verify your setup:

```cmd
# Test Python
python --version

# Test imports (one line at a time)
python -c "import flask; print('Flask OK')"
python -c "import yfinance; print('yfinance OK')"
python -c "import pandas; print('pandas OK')"
python -c "import numpy; print('numpy OK')"
python -c "import sklearn; print('sklearn OK')"

# Test the sentiment analyzer
python test_sentiment.py
```

---

## Contact Support

If issues persist after trying these solutions:
1. Copy the full error message
2. Note your Windows version (Win 10/11)
3. Note your Python version
4. Include output of `pip list`

---

## Alternative: Simplified Version

If you continue to have issues with scikit-learn, try the simplified version:
```cmd
python app_sentiment_simple.py
```
This version has reduced ML features but doesn't require scikit-learn.