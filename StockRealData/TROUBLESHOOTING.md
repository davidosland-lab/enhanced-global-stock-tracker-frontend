# Troubleshooting Guide

## 🔧 Batch File Crashing Issues

### Problem: install_and_run.bat closes immediately
**Solutions:**

1. **Run from Command Prompt to see errors:**
   ```cmd
   1. Open Command Prompt (Win+R, type "cmd", press Enter)
   2. Navigate to extraction folder: cd C:\YourPath\StockRealData
   3. Type: install_and_run.bat
   4. Now you can see any error messages
   ```

2. **Run debug.bat first:**
   - Double-click `debug.bat` to diagnose issues
   - This will show what's missing or misconfigured

3. **Common fixes:**
   - Ensure all files are extracted (not just the .bat file)
   - Run as Administrator (right-click → Run as administrator)
   - Check Python is in PATH

### Problem: "Python is not recognized"
**Solution:**
1. Download Python from https://www.python.org
2. During installation:
   - ✅ Check "Add Python to PATH" (IMPORTANT!)
   - ✅ Choose "Install for all users"
3. Restart computer after installation
4. Test: Open cmd and type `python --version`

### Problem: "Failed to create virtual environment"
**Solutions:**

1. **Option A - Manual fix:**
   ```cmd
   python -m pip install --upgrade pip
   python -m pip install virtualenv
   ```
   Then run `install_and_run.bat` again

2. **Option B - Use clean_install.bat:**
   - Run `clean_install.bat` for fresh installation
   - This removes old files and starts clean

3. **Option C - Run as Administrator:**
   - Right-click `install_and_run.bat`
   - Select "Run as administrator"

### Problem: "Package installation failed"
**Solutions:**

1. **Check internet connection** - packages download from internet

2. **Firewall/Antivirus blocking:**
   - Temporarily disable antivirus
   - Add Python to firewall exceptions
   - Use corporate proxy if needed:
     ```cmd
     set HTTP_PROXY=http://your-proxy:port
     set HTTPS_PROXY=http://your-proxy:port
     ```

3. **Try manual installation:**
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   pip install flask yfinance pandas plotly scikit-learn
   ```

### Problem: "No module named 'flask'"
**Solution:**
Virtual environment not activated properly.
1. Delete `venv` folder
2. Run `clean_install.bat`
3. Then run `start.bat`

### Problem: Port 8000 already in use
**Solutions:**

1. **Find and stop the process:**
   ```cmd
   netstat -ano | findstr :8000
   taskkill /PID <process_id> /F
   ```

2. **Or change the port:**
   - Edit `app.py`
   - Change last line from `port=8000` to `port=8080`
   - Access at http://localhost:8080

## 📝 File Structure Required

Make sure ALL these files are in the same folder:
```
StockRealData/
├── app.py                  # Main application
├── requirements.txt        # Python packages
├── install_and_run.bat    # Main installer
├── start.bat              # Quick start (after install)
├── debug.bat              # Diagnostic tool
├── clean_install.bat      # Fresh installation
├── README.md              # Documentation
└── TROUBLESHOOTING.md     # This file
```

## 🚀 Recommended Installation Steps

1. **First time setup:**
   ```
   1. Extract ALL files to a folder (e.g., C:\StockAnalysis)
   2. Run debug.bat to check system
   3. Run clean_install.bat for fresh setup
   4. Run start.bat to launch
   ```

2. **If crashes persist:**
   ```
   1. Open Command Prompt as Administrator
   2. Navigate to folder: cd C:\StockAnalysis\StockRealData
   3. Run: python -m venv venv
   4. Run: venv\Scripts\activate
   5. Run: pip install -r requirements.txt
   6. Run: python app.py
   ```

## ⚠️ Windows 11 Specific Issues

### PowerShell Execution Policy:
If using PowerShell instead of Command Prompt:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Windows Defender:
- May block Python scripts
- Add folder to exclusions:
  - Windows Security → Virus & threat protection
  - Manage settings → Add exclusions
  - Add folder containing the app

### Long Path Support:
If path too long errors:
1. Run `gpedit.msc`
2. Navigate to: Computer Configuration → Administrative Templates → System → Filesystem
3. Enable "Enable Win32 long paths"
4. Restart computer

## 💡 Quick Fixes

| Problem | Quick Fix |
|---------|-----------|
| Crashes immediately | Run from cmd to see error |
| Python not found | Reinstall Python with PATH |
| Pip not working | `python -m pip install --upgrade pip` |
| Packages fail | Check internet/firewall |
| Port in use | Change port in app.py |
| No venv folder | Run clean_install.bat |

## 📞 Still Having Issues?

1. Run `debug.bat` and note all error messages
2. Check you have:
   - Python 3.8 or higher
   - Internet connection
   - Admin rights (for some systems)
   - All files extracted together

---

For most issues, running `clean_install.bat` followed by `start.bat` resolves the problem!