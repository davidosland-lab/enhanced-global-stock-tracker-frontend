# 🚀 ML Stock Predictor - Windows 11 Deployment Package

## 📋 Quick Start Guide

### Step 1: Extract the Package
1. Extract the ZIP file to a folder on your Windows 11 machine
2. Navigate to the extracted folder

### Step 2: Run Diagnostics (Optional but Recommended)
```cmd
TROUBLESHOOT.bat
```
This will check your system and identify any potential issues.

### Step 3: Start the Server
```cmd
START.bat
```
This will:
- Check Python installation
- Install required packages
- Start the server on port 8000
- Open your browser automatically

### Step 4: Access the Interface
Open your browser and go to:
```
http://localhost:8000
```

## 📁 Package Contents

| File | Description |
|------|-------------|
| `server.py` | Main server application (fixed for Windows 11) |
| `diagnostics.py` | System diagnostic tool |
| `requirements.txt` | Python package dependencies |
| `START.bat` | One-click server startup |
| `TROUBLESHOOT.bat` | Diagnostic and troubleshooting tool |
| `QUICK_TEST.bat` | Test server endpoints |
| `README.md` | This file |

## 🔧 Features

### ✅ What's Working:
- **Yahoo Finance Integration** - Real-time stock data
- **Alpha Vantage Backup** - Your API key (68ZFANK047DL0KSR) configured
- **Australian Stock Support** - Auto-detects and adds .AX suffix
- **Windows 11 Optimized** - Fixed CORS and routing issues
- **No Mock Data** - All real market data
- **Logging** - Detailed logs in `server.log`

### 📊 Supported Stocks:
- **Australian**: CBA, BHP, CSL, NAB, WBC, ANZ, etc. (auto .AX)
- **US**: AAPL, MSFT, GOOGL, AMZN, TSLA, etc.
- **International**: Most global exchanges supported

## 🛠️ Troubleshooting

### Issue: "Python is not installed"
**Solution**: 
1. Download Python from https://python.org
2. During installation, CHECK "Add Python to PATH"
3. Restart Command Prompt after installation

### Issue: "Port 8000 is in use"
**Solution**:
```cmd
# Find what's using port 8000
netstat -ano | findstr :8000

# Kill the process (replace XXXX with the PID)
taskkill /F /PID XXXX
```

### Issue: "404 Error" or "Cannot fetch data"
**Solution**:
1. Run `TROUBLESHOOT.bat` to diagnose
2. Check Windows Firewall settings
3. Try running Command Prompt as Administrator
4. Check `server.log` for detailed error messages

### Issue: "Module not found" errors
**Solution**:
```cmd
# Install missing packages
pip install -r requirements.txt
```

## 📡 API Endpoints

### Status Check
```
GET http://localhost:8000/api/status
```
Returns server status and component health

### Fetch Stock Data
```
POST http://localhost:8000/api/fetch
Content-Type: application/json

{
  "symbol": "CBA",
  "period": "1mo"
}
```
Returns real-time stock data

### Diagnostics
```
GET http://localhost:8000/api/diagnose
```
Returns detailed system diagnostics

## 🧪 Testing

### Quick Test with CURL:
```cmd
# Test server status
curl http://localhost:8000/api/status

# Test stock fetch
curl -X POST http://localhost:8000/api/fetch -H "Content-Type: application/json" -d "{\"symbol\":\"CBA\",\"period\":\"1mo\"}"
```

### Quick Test with PowerShell:
```powershell
# Test server status
Invoke-WebRequest -Uri http://localhost:8000/api/status -UseBasicParsing

# Test stock fetch
$body = '{"symbol":"CBA","period":"1mo"}'
Invoke-WebRequest -Uri http://localhost:8000/api/fetch -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
```

## 📝 Logs

The server creates a `server.log` file with detailed information:
- All requests and responses
- Error messages with stack traces
- Yahoo Finance and Alpha Vantage status
- System diagnostics

To view logs:
```cmd
type server.log
```

## 🔐 Security Notes

- The server runs on localhost only (127.0.0.1)
- CORS is configured to allow all origins for development
- For production, restrict CORS origins appropriately
- Alpha Vantage API key is embedded (consider environment variables for production)

## 💡 Tips

1. **Australian Stocks**: Just type "CBA" - it auto-converts to "CBA.AX"
2. **Rate Limits**: Alpha Vantage has 5 requests/minute limit
3. **Performance**: Yahoo Finance is faster and primary source
4. **Browser**: Chrome or Edge recommended for best compatibility

## 🆘 Support

If you encounter issues:
1. Run `TROUBLESHOOT.bat` first
2. Check `server.log` for error details
3. Ensure Python 3.8+ is installed
4. Try running as Administrator
5. Temporarily disable antivirus/firewall for testing

## 📊 Example Usage

After starting the server with `START.bat`:

1. Open http://localhost:8000
2. Enter "CBA" in the symbol field
3. Click "Fetch Data"
4. You should see:
   - Symbol: CBA.AX
   - Company: Commonwealth Bank of Australia
   - Current price in AUD
   - Price change percentage
   - Historical data points

## ✅ Verification

The server is working correctly when:
- `/api/status` returns `{"status": "running"}`
- You can fetch real stock prices (not $100.00)
- Australian stocks show .AX suffix
- Logs show successful Yahoo Finance connections

## 🎯 Key Improvements in This Package

1. **Fixed 404 Errors** - Proper Flask route configuration
2. **Windows 11 CORS** - Complete CORS headers for all browsers
3. **Better Error Handling** - Detailed error messages and logging
4. **Auto-Recovery** - Fallback to Alpha Vantage if Yahoo fails
5. **Diagnostic Tools** - Built-in troubleshooting capabilities

---

**Version**: 1.0.0  
**Date**: October 2025  
**Platform**: Windows 11 Optimized