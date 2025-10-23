# 🔄 Stock Tracker Update Package

## Version: 5.0 - Windows 11 Fixed Edition

This update package contains all the scripts and tools needed to update an existing Stock Tracker installation to the latest version with Windows 11 fixes.

## 📦 Package Contents

### Update Scripts
1. **windows_update_deployment.bat** - Main update script (Command Prompt)
2. **windows_update_deployment.ps1** - PowerShell update script
3. **check_for_updates.bat** - Check if updates are available

### What Gets Updated
- ✅ All HTML modules to use hardcoded `http://localhost:8002`
- ✅ Latest backend_fixed_v2.py with all fixes
- ✅ New landing page dashboard (index.html)
- ✅ Diagnostic tool for connection testing
- ✅ All startup scripts updated
- ✅ Python dependencies updated

## 🚀 How to Update

### Option 1: Batch Script (Easiest)
1. Copy `windows_update_deployment.bat` to your Stock Tracker folder
2. Double-click to run
3. Follow the prompts

### Option 2: PowerShell Script
1. Copy `windows_update_deployment.ps1` to your Stock Tracker folder
2. Right-click → Run with PowerShell
3. Or run: `powershell -ExecutionPolicy Bypass -File windows_update_deployment.ps1`

### Option 3: Manual Update
1. Download the latest deployment package
2. Extract and overwrite existing files
3. Run `pip install -r requirements.txt --upgrade`

## ⚡ Quick Update Steps

```batch
# 1. Check current version
check_for_updates.bat

# 2. Run update if needed
windows_update_deployment.bat

# 3. Start the application
windows_start.bat

# 4. Open landing page
# Open index.html in browser
```

## 🔍 What the Update Does

### 1. Creates Backup
- Backs up all current files to `backup_[date]_[time]` folder
- Preserves your configuration and data

### 2. Stops Services
- Safely stops any running backend on port 8002
- Ensures clean update process

### 3. Downloads Latest Files
- Fetches latest modules from GitHub
- Updates all core components

### 4. Applies Windows 11 Fixes
- Hardcodes all backend URLs to `http://localhost:8002`
- Removes dynamic URL detection that causes issues
- Ensures maximum compatibility

### 5. Updates Dependencies
- Upgrades pip to latest version
- Updates all Python packages

### 6. Creates Summary
- Generates UPDATE_SUMMARY.txt with all changes
- Documents backup location

## 🛡️ Safety Features

- **Automatic Backup** - All files backed up before update
- **Version Checking** - Verifies you're updating to the right version
- **Rollback Option** - Can restore from backup if needed
- **No Data Loss** - Your settings and data are preserved

## 📋 Pre-Update Checklist

- [ ] Python 3.8+ installed
- [ ] Current installation is working
- [ ] No critical work in progress
- [ ] At least 50MB free disk space

## 🔄 Post-Update Verification

1. Run `diagnostic_tool.html` to test connections
2. Check backend is responding: `http://localhost:8002/api/stock/AAPL`
3. Verify all modules load correctly
4. Test with a stock symbol (e.g., AAPL, MSFT)

## ⚠️ Troubleshooting

### Update Script Won't Run
- Run as Administrator if needed
- Check PowerShell execution policy
- Ensure you're in the Stock Tracker directory

### Files Not Downloading
- Check internet connection
- Verify GitHub is accessible
- Try manual download method

### Backend Won't Start After Update
- Check Python version: `python --version`
- Reinstall requirements: `pip install -r requirements.txt`
- Check port 8002 is free: `netstat -an | findstr :8002`

### Modules Show Connection Errors
- Ensure backend is running
- Open diagnostic_tool.html
- Check Windows Firewall settings

## 🔙 How to Rollback

If you need to revert to the previous version:

1. Stop the backend (Ctrl+C)
2. Navigate to the backup folder created during update
3. Copy all files back to the main directory
4. Restart the application

## 📊 Version History

- **v5.0-windows-11-fix** (Current)
  - Fixed all Windows 11 localhost issues
  - Added landing page dashboard
  - Enhanced diagnostic tools
  - Hardcoded backend URLs

- **v4.0-prediction-centre**
  - Added Prediction Centre with backtesting
  - Learning metrics tracking
  - Model comparison features

- **v3.2-technical-analysis**
  - Technical analysis enhancements
  - 150+ indicators
  - Pattern recognition

## 📞 Support

For issues or questions:
1. Run `diagnostic_tool.html` for connection testing
2. Check `WINDOWS_11_FIX_GUIDE.md` for solutions
3. Visit GitHub repository for latest updates

## 📝 Notes

- This update is specifically designed for Windows 11 compatibility
- All modules will use `http://localhost:8002` after update
- No authentication or API keys required
- Uses real Yahoo Finance data only (no synthetic data)

---

**Update Package Version:** 5.0
**Release Date:** October 2025
**Status:** Production Ready