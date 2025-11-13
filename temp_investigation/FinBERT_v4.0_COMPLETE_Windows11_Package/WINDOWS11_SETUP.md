# FinBERT v4.0 - Windows 11 Localhost Setup Guide

## 🖥️ **Configuration for Windows 11**

This package is **pre-configured** for Windows 11 localhost deployment.

### **Default Configuration**:
```
Host: 127.0.0.1 (localhost)
Port: 5001
Access URL: http://127.0.0.1:5001
```

---

## 📋 **Complete Setup Instructions**

### **Step 1: Prerequisites**

1. **Install Python 3.8 or higher**:
   - Download from: https://www.python.org/downloads/
   - During installation: ✅ **CHECK "Add Python to PATH"**
   - Verify: Open Command Prompt and type `python --version`

2. **Extract the Package**:
   - Extract `FinBERT_v4.0_Windows11_ENHANCED.zip` to:
   ```
   C:\FinBERT_v4\
   ```

---

### **Step 2: Run Configuration Check (Optional but Recommended)**

```cmd
1. Open: C:\FinBERT_v4\FinBERT_v4.0_Windows11_ENHANCED
2. Double-click: CHECK_CONFIG.bat
3. Review: All checks should pass
4. Fix: Any errors before proceeding
```

**What it checks**:
- ✅ Python installed
- ✅ Correct directory
- ✅ Virtual environment (after installation)
- ✅ Configuration settings
- ✅ Port 5001 availability

---

### **Step 3: Install Dependencies**

```cmd
1. Navigate to: C:\FinBERT_v4\FinBERT_v4.0_Windows11_ENHANCED
2. Right-click: scripts\INSTALL_WINDOWS11.bat
3. Select: "Run as Administrator"
4. Choose installation type:
   [1] FULL - All AI features (2GB, ~5 minutes)
   [2] MINIMAL - Basic features only (500MB, ~2 minutes)
5. Wait for installation to complete
```

**FULL Installation includes**:
- LSTM Neural Networks (TensorFlow)
- FinBERT Sentiment Analysis (PyTorch)
- Real News Scraping
- Enhanced Charts (ECharts, 600px)
- All Features

**MINIMAL Installation includes**:
- Basic Stock Charts (ECharts, 600px)
- Technical Analysis
- Market Data
- No AI/ML features

---

### **Step 4: Start the Server**

```cmd
1. Double-click: START_FINBERT_V4.bat
2. Wait for message: "Running on http://127.0.0.1:5001"
3. Keep the terminal window open (server is running)
```

**You should see**:
```
======================================================================
  FinBERT v4.0 Development Server
======================================================================

🚀 Server starting on http://localhost:5001
 * Running on http://127.0.0.1:5001
 * Press CTRL+C to quit
```

---

### **Step 5: Access the Application**

1. **Open your web browser** (Chrome, Edge, Firefox)
2. **Navigate to**: http://127.0.0.1:5001
3. **Alternative URL**: http://localhost:5001 (same thing)

**What you should see**:
- FinBERT v4.0 interface
- Search bar for stock symbols
- Chart type selector (Candlestick/Line)
- Period selectors (1D, 5D, 1M, etc.)

---

### **Step 6: Test with AAPL**

```
1. In the search bar, type: AAPL
2. Click: "Analyze" button
3. Wait: 2-5 seconds for data to load
```

**Expected Results**:
- ✅ Large price chart (600px tall)
- ✅ Clear candlesticks (no overlapping)
- ✅ Volume chart below (200px tall)
- ✅ AI Prediction panel (BUY/SELL/HOLD)
- ✅ Sentiment Analysis panel
- ✅ News Articles section (scroll down)
- ✅ Market Data with accurate change

---

## 🔧 **Troubleshooting**

### **Issue: "Can't Reach This Page" or "Connection Refused"**

**Symptoms**:
- Browser shows error when accessing http://127.0.0.1:5001
- "localhost refused to connect"
- "ERR_CONNECTION_REFUSED"

**Solutions**:

1. **Check if server is running**:
   ```
   - Look for the terminal window from START_FINBERT_V4.bat
   - Should show: "Running on http://127.0.0.1:5001"
   - If not visible, run START_FINBERT_V4.bat again
   ```

2. **Verify configuration**:
   ```cmd
   - Run: CHECK_CONFIG.bat
   - Verify: Host is 127.0.0.1
   - Verify: Port 5001 is available
   ```

3. **Check Windows Firewall**:
   ```
   - Open: Windows Security
   - Go to: Firewall & network protection
   - Allow: Python through firewall
   - Or: Temporarily disable firewall to test
   ```

4. **Try different browsers**:
   ```
   - Chrome: http://127.0.0.1:5001
   - Edge: http://127.0.0.1:5001
   - Firefox: http://127.0.0.1:5001
   ```

---

### **Issue: Port Already in Use**

**Symptoms**:
- Server won't start
- Error: "Address already in use"
- CHECK_CONFIG.bat shows "Port 5001: IN USE"

**Solution 1: Find and close the application using port 5001**:
```cmd
1. Open Command Prompt as Administrator
2. Run: netstat -ano | findstr :5001
3. Note the PID (Process ID) number
4. Run: taskkill /PID <PID> /F
5. Restart START_FINBERT_V4.bat
```

**Solution 2: Change the port**:
```cmd
1. Open: config_dev.py in Notepad
2. Find line: PORT = 5001
3. Change to: PORT = 5002 (or any free port)
4. Save file
5. Restart START_FINBERT_V4.bat
6. Access: http://127.0.0.1:5002 (new port)
```

---

### **Issue: Configuration Shows HOST = '0.0.0.0'**

**Problem**: 
- Server binds to 0.0.0.0 instead of 127.0.0.1
- May cause issues on Windows 11

**Solution**:
```cmd
1. Open: config_dev.py
2. Find line: HOST = '0.0.0.0'
3. Change to: HOST = '127.0.0.1'
4. Save file
5. Restart server
```

---

### **Issue: Python Not Found**

**Symptoms**:
- "python is not recognized as an internal or external command"
- Installation script fails immediately

**Solution**:
```cmd
1. Download Python: https://www.python.org/downloads/
2. Run installer
3. ✅ CHECK: "Add Python to PATH" (very important!)
4. Complete installation
5. Restart Command Prompt
6. Verify: python --version
7. Try installation again
```

---

## 📊 **What You Should See**

### **Main Dashboard**:
```
┌─────────────────────────────────────────────┐
│ FinBERT v4.0 - Professional Trading System  │
├─────────────────────────────────────────────┤
│ [Search: AAPL] [Analyze]                    │
├──────────────────────┬──────────────────────┤
│                      │ 🤖 AI Prediction     │
│ 📈 Price Chart       │ BUY / $175.43       │
│ (600px - HUGE!)      │ Confidence: 74%     │
│                      │                     │
│ Perfect Candles:     │ 🧠 Sentiment        │
│ ┃ ▌ ┃ ▌ ┃ ▌ ┃       │ Positive (87%)      │
│ (NO OVERLAP!)        │ Articles: 9         │
│                      │                     │
│ 📊 Volume (200px)    │ 📊 Market Data      │
│                      │ Change: +$2.31 ✓    │
└──────────────────────┴──────────────────────┘
│ 📰 News & Sentiment Analysis               │
├─────────────────────────────────────────────┤
│ [🟢 89%] Apple Reports Record Earnings     │
│ [🟢 78%] iPhone Sales Exceed Targets       │
│ [⚪ 45%] Apple Updates macOS               │
└─────────────────────────────────────────────┘
```

---

## ⚙️ **Advanced Configuration**

### **Change Port**:
Edit `config_dev.py`:
```python
# Line 18
PORT = 5002  # Change from 5001 to any free port
```

### **Change Host** (if needed):
Edit `config_dev.py`:
```python
# Line 17
HOST = '127.0.0.1'  # Keep as localhost for Windows 11
# Don't change to '0.0.0.0' unless deploying to network
```

### **Disable Debug Mode**:
Edit `config_dev.py`:
```python
# Line 12
DEBUG = False  # Set to False for production use
```

---

## ✅ **Verification Checklist**

Use this checklist to verify your setup:

- [ ] Python 3.8+ installed with PATH configured
- [ ] Package extracted to C:\FinBERT_v4\
- [ ] CHECK_CONFIG.bat shows all green checks
- [ ] Installation completed (FULL or MINIMAL)
- [ ] Virtual environment created (venv folder exists)
- [ ] config_dev.py shows HOST = '127.0.0.1'
- [ ] config_dev.py shows PORT = 5001
- [ ] Port 5001 is available (not in use)
- [ ] START_FINBERT_V4.bat runs without errors
- [ ] Terminal shows "Running on http://127.0.0.1:5001"
- [ ] Browser can access http://127.0.0.1:5001
- [ ] Dashboard loads correctly
- [ ] AAPL test analysis works
- [ ] Charts display (600px tall)
- [ ] No overlapping candlesticks
- [ ] News articles section appears

---

## 🎯 **Quick Reference**

### **URLs**:
- **Main App**: http://127.0.0.1:5001
- **Alternative**: http://localhost:5001
- **API Health**: http://127.0.0.1:5001/api/health
- **API Stock**: http://127.0.0.1:5001/api/stock/AAPL

### **Files**:
- **Config**: `config_dev.py` (change port/host here)
- **Start**: `START_FINBERT_V4.bat` (launch server)
- **Install**: `scripts\INSTALL_WINDOWS11.bat` (initial setup)
- **Check**: `CHECK_CONFIG.bat` (verify setup)

### **Commands**:
- **Check Python**: `python --version`
- **Check Port**: `netstat -ano | findstr :5001`
- **Kill Process**: `taskkill /PID <PID> /F`
- **Install Packages**: `pip install -r requirements-full.txt`

---

## 🎉 **Success!**

If your checklist is complete, you now have a fully functional FinBERT v4.0 Enhanced system running locally on Windows 11!

**Features Available**:
- ✅ 600px charts (50% larger)
- ✅ Perfect candlesticks (ECharts, no overlap)
- ✅ AI predictions (LSTM + Technical + Trend)
- ✅ Real sentiment analysis (FinBERT)
- ✅ News articles display (full transparency)
- ✅ Accurate market data
- ✅ Professional trading interface

**Next**: See `USER_GUIDE.md` to learn about all features!

---

**Version**: 4.0-Enhanced (Windows 11 Localhost)  
**Last Updated**: October 31, 2025  
**Configuration**: 127.0.0.1:5001
