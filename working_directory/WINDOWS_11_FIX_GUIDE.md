# Windows 11 Localhost Connection Fix Guide

## 🔧 Complete Solution for Windows 11 Development

### Problem Summary
Windows 11 has known issues with localhost connections, especially when using:
- WSL (Windows Subsystem for Linux)
- Windows Defender Firewall
- IPv6/IPv4 dual stack configurations
- Edge/Chrome browser security features

### ✅ VERIFIED SOLUTION

#### 1. Backend Configuration (Already Fixed)
The backend at `backend_fixed_v2.py` is correctly configured with:
```python
# CORS enabled for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Running on all interfaces
uvicorn.run(app, host="0.0.0.0", port=8002, log_level="info")
```

#### 2. Frontend Configuration (Key Fix)
All modules now use hardcoded localhost URLs:
```javascript
// CORRECT - Windows 11 Compatible
const BACKEND_URL = 'http://localhost:8002';

// NOT: window.location.hostname based URLs
// NOT: Dynamic protocol detection
// NOT: Conditional URL building
```

#### 3. Windows Firewall Rules
Run these commands in PowerShell as Administrator:

```powershell
# Allow Python through firewall
New-NetFirewallRule -DisplayName "Python Backend API" -Direction Inbound -Program "C:\Python\python.exe" -Action Allow -Protocol TCP -LocalPort 8002

# Alternative: Allow specific port
New-NetFirewallRule -DisplayName "Stock Tracker API Port" -Direction Inbound -LocalPort 8002 -Protocol TCP -Action Allow
```

#### 4. Hosts File Configuration
Edit `C:\Windows\System32\drivers\etc\hosts` as Administrator:
```
127.0.0.1    localhost
::1          localhost
```

#### 5. Browser Settings

**Chrome/Edge:**
1. Navigate to `chrome://flags` or `edge://flags`
2. Search for "localhost"
3. Set "Allow invalid certificates for resources loaded from localhost" to **Enabled**
4. Restart browser

**Disable CORS for testing (if needed):**
```batch
# Chrome
"C:\Program Files\Google\Chrome\Application\chrome.exe" --disable-web-security --user-data-dir="C:\temp\chrome_test"

# Edge
"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --disable-web-security --user-data-dir="C:\temp\edge_test"
```

### 🔍 Diagnostic Steps

#### Test Backend Connection:
```batch
# Command Prompt
curl http://localhost:8002/api/stock/AAPL

# PowerShell
Invoke-WebRequest -Uri "http://localhost:8002/api/stock/AAPL"
```

#### Check Port Availability:
```batch
netstat -an | findstr :8002
```

#### Verify Python Process:
```batch
tasklist | findstr python
```

### 📁 File Structure for Windows

```
C:\Projects\stock-tracker\
├── working_directory\
│   ├── backend_fixed_v2.py
│   ├── start.bat           # Windows startup script
│   ├── modules\
│   │   ├── predictions\
│   │   │   └── prediction_centre_advanced.html
│   │   ├── technical_analysis_enhanced.html
│   │   └── technical_analysis_desktop.html
│   └── requirements.txt
```

### 🚀 Windows Startup Script

The `start.bat` file is already configured:
```batch
@echo off
echo Starting Stock Tracker Backend...
cd /d %~dp0
pip install -r requirements.txt
python backend_fixed_v2.py
```

### 🔒 Security Considerations

1. **Windows Defender:** May block Python scripts
   - Add exception for project folder
   - Allow python.exe in Windows Security

2. **Antivirus Software:** May interfere with localhost connections
   - Add exception for port 8002
   - Whitelist python.exe

3. **Corporate Firewall:** May block local development
   - Contact IT for exceptions
   - Use alternative ports if needed

### ✨ Quick Fix Checklist

- [ ] Backend running on port 8002
- [ ] All HTML files use `http://localhost:8002` hardcoded
- [ ] Windows Firewall exception added
- [ ] Browser CORS/security relaxed for localhost
- [ ] Python allowed through Windows Defender
- [ ] Hosts file has localhost entries
- [ ] No WSL/Docker complications

### 📊 Testing URLs

After starting backend with `start.bat`:

1. **API Test:** http://localhost:8002/api/stock/AAPL
2. **Technical Analysis:** Open `technical_analysis_enhanced.html` directly in browser
3. **Prediction Centre:** Open `prediction_centre_advanced.html` directly in browser
4. **Desktop Version:** Open `technical_analysis_desktop.html` directly in browser

### 🆘 Troubleshooting

**Error: "Failed to fetch" or CORS errors**
- Ensure backend is running (`python backend_fixed_v2.py`)
- Check firewall settings
- Use hardcoded `http://localhost:8002` in frontend

**Error: "Connection refused"**
- Check if port 8002 is in use: `netstat -an | findstr :8002`
- Restart backend
- Try 127.0.0.1 instead of localhost

**Error: "ERR_CONNECTION_RESET"**
- Windows Defender blocking connection
- Add firewall exception
- Disable IPv6 if causing issues

### 🎯 Verification

Run the diagnostic tool to verify everything is working:
```html
Open diagnostic_tool.html in browser to test all connections
```

---
**Last Updated:** October 2024
**Status:** All Windows 11 issues resolved with hardcoded localhost approach