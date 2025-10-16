# StockTracker V10 - Diagnostic Package

## 🔍 Complete Diagnostic Tools

This package includes comprehensive diagnostic and troubleshooting tools to identify and fix any issues with your StockTracker installation.

## 📋 Diagnostic Tools Included

### 1. **FULL_DIAGNOSTIC.bat** - Complete System Check
- Runs comprehensive diagnostic and generates detailed report
- Checks all dependencies, ports, permissions, and services
- Saves report to `diagnostic_results` folder with timestamp
- **Use this FIRST to identify issues**

### 2. **comprehensive_diagnostic.py** - Python Diagnostic Script
- Core diagnostic engine
- Performs 10 different system checks:
  1. System Information
  2. Python Environment
  3. Required Packages
  4. Service Files
  5. Port Availability
  6. Yahoo Finance API
  7. SSL Certificates
  8. Database Functionality
  9. File Permissions
  10. Service Startup Test

### 3. **QUICK_FIX.bat** - Automatic Issue Resolver
- Attempts to fix common issues automatically:
  - Kills stuck Python processes
  - Clears SSL environment variables
  - Checks/creates virtual environment
  - Upgrades pip and setuptools
  - Installs missing packages
  - Clears database locks
  - Frees blocked ports
  - Tests service imports

### 4. **SERVICE_MONITOR.bat** - Real-time Service Monitor
- Live monitoring of all 5 services
- Shows port status (ACTIVE/NOT RUNNING)
- Performs health checks via HTTP
- Lists active Python processes
- Refreshes every 5 seconds

### 5. **TEST_INDIVIDUAL.bat** - Interactive Service Tester
- Test each service one at a time
- See exact error messages
- Import test for each backend
- Menu-driven interface

### 6. **DEBUG_START.bat** - Detailed Startup Debugger
- Shows each service starting step-by-step
- Checks if ports are listening
- Reports any failures
- Shows active Python processes

### 7. **START_POWERSHELL.bat** - PowerShell Startup
- Alternative startup using PowerShell
- Better process management
- Automatic restart on failure
- Real-time port monitoring

## 🚀 Troubleshooting Workflow

### Step 1: Run Full Diagnostic
```batch
FULL_DIAGNOSTIC.bat
```
This will identify all issues and save a detailed report.

### Step 2: Apply Quick Fix
```batch
QUICK_FIX.bat
```
This will attempt to automatically resolve common issues.

### Step 3: Test Individual Services
```batch
TEST_INDIVIDUAL.bat
```
Test each service separately to identify specific failures.

### Step 4: Monitor Services
```batch
SERVICE_MONITOR.bat
```
Monitor services in real-time to see which are running.

### Step 5: Try Alternative Startup
If regular START.bat fails, try:
```batch
START_POWERSHELL.bat
```

## 🔧 Common Issues and Solutions

### Issue: "Virtual environment not found"
**Solution**: Run `INSTALL.bat` to create and set up the virtual environment

### Issue: "Port already in use"
**Solution**: Run `QUICK_FIX.bat` which will free up the ports

### Issue: "Package not found"
**Solution**: 
1. Run `QUICK_FIX.bat` to auto-install missing packages
2. Or manually: `venv\Scripts\activate` then `pip install -r requirements.txt`

### Issue: "SSL certificate error"
**Solution**: `QUICK_FIX.bat` clears SSL environment variables automatically

### Issue: "Access denied" or permission errors
**Solution**: Run Command Prompt as Administrator

### Issue: Services start but immediately stop
**Solution**: 
1. Run `TEST_INDIVIDUAL.bat` to see exact error
2. Check `diagnostic_results` folder for detailed logs

## 📊 Understanding Diagnostic Output

### Green ✓ = Working correctly
### Yellow ⚠ = Warning, may need attention
### Red ✗ = Error, needs to be fixed

## 💡 Pro Tips

1. **Always run diagnostic first** - It will tell you exactly what's wrong
2. **Save diagnostic reports** - Keep them for reference
3. **Use Service Monitor** - Leave it running to watch service health
4. **Try PowerShell startup** - Often more reliable than batch files
5. **Check firewall/antivirus** - They may block Python or network ports

## 📁 Diagnostic Files Generated

- `diagnostic_results/` - Folder containing all diagnostic reports
- `diagnostic_report_[timestamp].txt` - Detailed system analysis
- Test database files (`.db`) - Created during testing

## 🆘 If All Else Fails

1. Delete the `venv` folder completely
2. Run `INSTALL.bat` to recreate environment
3. Run `FULL_DIAGNOSTIC.bat` to verify
4. Run `START.bat` or `START_POWERSHELL.bat`

## 📧 Information to Share for Support

If you need help, run `FULL_DIAGNOSTIC.bat` and share:
1. The generated report file
2. Your Python version (`python --version`)
3. Your Windows version
4. Any error messages you see

---
**Remember**: The diagnostic tools are designed to identify AND fix most issues automatically. Start with `FULL_DIAGNOSTIC.bat` and follow the recommendations!