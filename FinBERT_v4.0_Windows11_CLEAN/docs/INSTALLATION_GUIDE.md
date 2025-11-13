# FinBERT v4.0 - Installation Guide

## Quick Installation

### Step 1: Extract Package
Extract the ZIP file to `C:\FinBERT_v4\`

### Step 2: Run Installer
```cmd
Right-click Command Prompt → Run as Administrator
cd C:\FinBERT_v4\FinBERT_v4.0_Windows11_CLEAN
scripts\INSTALL_WINDOWS11.bat
```

### Step 3: Choose Installation Type
- [1] FULL - Complete AI/ML (900 MB, 10-20 min)
- [2] MINIMAL - Basic only (50 MB, 2-3 min)

### Step 4: Start Application
```cmd
START_FINBERT_V4.bat
```

### Step 5: Access
Open browser to http://127.0.0.1:5001

## Common Issues

### Python Not Found
- Install from https://www.python.org/downloads/
- Check "Add Python to PATH"

### Port Already in Use
- Change port in config_dev.py
- Or kill process: `netstat -ano | findstr :5001`

### Installation Fails
- Run as Administrator
- Check internet connection
- Verify Python 3.8+

For more help, see README.md
