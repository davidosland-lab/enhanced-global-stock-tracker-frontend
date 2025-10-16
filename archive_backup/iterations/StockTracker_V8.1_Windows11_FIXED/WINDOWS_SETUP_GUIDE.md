# Stock Tracker V8 - Windows Setup Guide

## ⚠️ IMPORTANT: Local vs Cloud Access

### Option 1: Local Windows Installation (Recommended)

If you're running this on your Windows machine:

1. **Extract the ZIP file** to a folder like `C:\StockTracker`

2. **Install Python** (if not installed):
   - Download from https://python.org (3.8 or higher)
   - CHECK "Add Python to PATH" during installation

3. **Run the installer**:
   ```cmd
   INSTALL_WINDOWS11.bat
   ```

4. **Start the services**:
   ```cmd
   START_TRACKER.bat
   ```
   This will start:
   - Main API on http://localhost:8002
   - ML Backend on http://localhost:8003
   - FinBERT on http://localhost:8004
   - Web Interface on http://localhost:8080

5. **Open in browser**:
   - Navigate to http://localhost:8080
   - Use `index_fixed.html` if the default index doesn't work

### Option 2: Access Cloud Sandbox Services

If you're accessing the services running in the cloud sandbox:

**Use these URLs directly in your browser:**
- Web Interface: https://8080-i2ch499gc6d7qpm0yvxy4-6532622b.e2b.dev
- Main API: https://8002-i2ch499gc6d7qpm0yvxy4-6532622b.e2b.dev
- ML Backend: https://8003-i2ch499gc6d7qpm0yvxy4-6532622b.e2b.dev
- FinBERT: https://8004-i2ch499gc6d7qpm0yvxy4-6532622b.e2b.dev

---

## 🔧 Troubleshooting Connection Issues

### "ERR_CONNECTION_REFUSED" Errors

This happens when:
1. **Services aren't running locally** - Run `START_TRACKER.bat`
2. **Firewall blocking ports** - Allow ports 8002-8004, 8080
3. **Wrong environment** - Use `index_fixed.html` which auto-detects

### How index_fixed.html Works

The fixed version automatically detects your environment:
- **Local Windows**: Uses `http://localhost:XXXX`
- **Cloud Sandbox**: Uses `https://XXXX-sandbox.e2b.dev`

---

## 📋 Quick Checklist

### For Windows Local Installation:

- [ ] Python 3.8+ installed
- [ ] Ran INSTALL_WINDOWS11.bat
- [ ] Ran START_TRACKER.bat
- [ ] Services running (check console window)
- [ ] Opened http://localhost:8080
- [ ] If issues, try index_fixed.html

### For Cloud Access:

- [ ] Use the sandbox URLs directly
- [ ] Don't need to install anything locally
- [ ] Services already running in cloud

---

## 🚀 Testing Services

### Test if services are running (Windows):

Open Command Prompt and run:
```cmd
curl http://localhost:8002/api/status
curl http://localhost:8003/api/ml/status
```

If you get JSON responses, services are running!

### Test from PowerShell:
```powershell
Invoke-WebRequest -Uri http://localhost:8002/api/status
```

---

## 📝 Using the Fixed Version

1. **Rename files** (if needed):
   ```cmd
   rename index.html index_original.html
   rename index_fixed.html index.html
   ```

2. **The fixed version will**:
   - Auto-detect if running locally or in cloud
   - Use correct API endpoints
   - Show status of each service
   - Display helpful messages if services are offline

---

## 🔍 Verify Installation

Run this to check everything:
```cmd
VERIFY_INSTALLATION.bat
```

This checks:
- All files present
- Python installed
- Services configured correctly
- No fake data (real ML implementation)

---

## 💡 Pro Tips

1. **Keep the console window open** - Services run in it
2. **Check the console** for any error messages
3. **Use Task Manager** to verify python.exe processes
4. **Ports in use?** Kill existing Python processes:
   ```cmd
   taskkill /F /IM python.exe
   ```

5. **For development**, you can run services individually:
   ```cmd
   cd backends
   python backend.py        # Terminal 1
   python ml_backend.py     # Terminal 2
   python finbert_backend.py # Terminal 3
   ```

---

## ✅ Success Indicators

You know it's working when:
- All status indicators show "Online" (green)
- No console errors in browser (F12)
- Can train ML models (takes 10-60 seconds)
- Can fetch stock data
- All modules load correctly

---

## 🆘 Still Having Issues?

1. **Check Windows Firewall** - Allow Python through
2. **Run as Administrator** - Right-click START_TRACKER.bat
3. **Check Python version**: `python --version` (need 3.8+)
4. **Reinstall packages**: `pip install -r requirements.txt --force-reinstall`
5. **Use the cloud version** if local doesn't work

Remember: The cloud sandbox services are already running and accessible via the provided URLs!