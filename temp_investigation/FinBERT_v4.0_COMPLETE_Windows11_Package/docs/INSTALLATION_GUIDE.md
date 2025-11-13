# FinBERT v4.0 Enhanced - Installation Guide

## 🚀 Quick Installation (3 Steps)

### **Step 1: Extract Package**
Extract `FinBERT_v4.0_Windows11_ENHANCED.zip` to:
```
C:\FinBERT_v4\
```

### **Step 2: Run Installer**
```cmd
1. Navigate to: C:\FinBERT_v4\FinBERT_v4.0_Windows11_ENHANCED
2. Right-click: scripts\INSTALL_WINDOWS11.bat
3. Select: "Run as Administrator"
4. Choose: [1] FULL (recommended) or [2] MINIMAL
5. Wait: ~3-5 minutes for installation to complete
```

### **Step 3: Start Application**
```cmd
1. Double-click: START_FINBERT_V4.bat
2. Wait: ~10 seconds for server to start
3. Open browser: http://127.0.0.1:5001
4. Test: Enter "AAPL" and click "Analyze"
```

---

## 📋 System Requirements

### **Minimum**:
- Windows 11 or Windows 10 (with updates)
- Python 3.8 or higher
- 4GB RAM
- 2GB free disk space
- Internet connection

### **Recommended**:
- Windows 11 (latest)
- Python 3.12.x
- 8GB RAM
- 5GB free disk space
- Broadband internet

---

## 🔧 Installation Options

### **Option 1: FULL Installation** (Recommended)
Includes ALL features:
- ✅ LSTM Neural Networks (TensorFlow)
- ✅ FinBERT Sentiment (PyTorch + Transformers)
- ✅ Real News Scraping (Finviz + Yahoo Finance)
- ✅ Enhanced Technical Analysis
- ✅ 600px Charts with ECharts
- ✅ News Articles Display

**Time**: ~3-5 minutes  
**Size**: ~2GB

### **Option 2: MINIMAL Installation**
Basic features only:
- ✅ Stock Price Charts (ECharts)
- ✅ Volume Analysis
- ✅ Basic Technical Analysis
- ✅ Market Data
- ❌ No LSTM/FinBERT

**Time**: ~1-2 minutes  
**Size**: ~500MB

---

## 🌐 Accessing the Application

### **After Installation**:
1. **Run**: `START_FINBERT_V4.bat`
2. **Open Browser**: Navigate to **http://127.0.0.1:5001**
3. **Test**: Enter a stock symbol like "AAPL" and click "Analyze"

### **URLs**:
- **Main Application**: http://127.0.0.1:5001
- **API Health Check**: http://127.0.0.1:5001/api/health
- **API Stock Data**: http://127.0.0.1:5001/api/stock/AAPL

---

## ❗ Common Issues & Solutions

### **Issue 1: Python Not Found**
**Error**: `'python' is not recognized as an internal or external command`

**Solution**:
```cmd
1. Download Python from: https://www.python.org/downloads/
2. Run installer
3. ✅ CHECK: "Add Python to PATH" during installation
4. Restart Command Prompt
5. Verify: python --version
6. Re-run installation script
```

### **Issue 2: Port Already in Use**
**Error**: `Address already in use` or `Port 5001 is in use`

**Solution**:
```cmd
Option 1: Close existing FinBERT instance
1. Open Task Manager (Ctrl+Shift+Esc)
2. Find "python.exe" processes
3. End Task on FinBERT processes
4. Restart START_FINBERT_V4.bat

Option 2: Change port
1. Open: config_dev.py
2. Find: PORT = 5001
3. Change to: PORT = 5002 (or any free port)
4. Save and restart
```

### **Issue 3: Virtual Environment Not Created**
**Error**: `Virtual environment not found`

**Solution**:
```cmd
1. Open Command Prompt as Administrator
2. Navigate to installation folder:
   cd C:\FinBERT_v4\FinBERT_v4.0_Windows11_ENHANCED
3. Create venv manually:
   python -m venv venv
4. Activate:
   venv\Scripts\activate
5. Install dependencies:
   pip install -r requirements-full.txt
6. Run: START_FINBERT_V4.bat
```

### **Issue 4: TensorFlow Installation Failed**
**Error**: `Could not install TensorFlow`

**Solution**:
```cmd
Option 1: Use MINIMAL installation
1. Re-run: scripts\INSTALL_WINDOWS11.bat
2. Choose: [2] MINIMAL
3. This skips TensorFlow

Option 2: Install Visual C++ Redistributable
1. Download from Microsoft:
   https://aka.ms/vs/17/release/vc_redist.x64.exe
2. Install and restart
3. Re-run FULL installation

Option 3: Manual install
pip install tensorflow --no-cache-dir
```

### **Issue 5: Browser Shows "Can't Reach This Page"**
**Error**: `ERR_CONNECTION_REFUSED` or `localhost refused to connect`

**Solution**:
```cmd
1. Check if server is running:
   - Look for Flask server window
   - Should show: "Running on http://127.0.0.1:5001"

2. If not running:
   - Run: START_FINBERT_V4.bat
   - Wait for "Press CTRL+C to quit" message

3. If still not working:
   - Check firewall settings
   - Try: http://localhost:5001 instead

4. Verify installation:
   - Run: python app_finbert_v4_dev.py
   - Look for error messages
```

### **Issue 6: Charts Not Loading**
**Error**: Empty charts or "Loading..." forever

**Solution**:
```cmd
1. Check internet connection
2. Try different stock symbol (AAPL, TSLA, GOOGL)
3. Clear browser cache:
   - Chrome/Edge: Ctrl+Shift+Delete
   - Select "Cached images and files"
   - Clear data
4. Hard refresh: Ctrl+F5
5. Restart application
```

---

## 🧪 Testing the Installation

### **Step 1: Verify Server is Running**
```cmd
1. After running START_FINBERT_V4.bat
2. You should see:
   ✓ "Server starting on http://localhost:5001"
   ✓ "Running on http://127.0.0.1:5001"
   ✓ "Press CTRL+C to quit"
```

### **Step 2: Test API Health**
```cmd
Open browser: http://127.0.0.1:5001/api/health
Should return JSON with system status
```

### **Step 3: Test Stock Analysis**
```cmd
1. Open: http://127.0.0.1:5001
2. Enter: AAPL
3. Click: "Analyze"
4. Verify:
   ✅ Charts load (600px price, 200px volume)
   ✅ No overlapping candlesticks
   ✅ AI prediction shows (BUY/SELL/HOLD)
   ✅ Sentiment shows (Positive/Neutral/Negative)
   ✅ News articles section appears (scroll down)
   ✅ Market data is accurate
```

---

## 📦 Package Structure

```
FinBERT_v4.0_Windows11_ENHANCED/
├── scripts/
│   └── INSTALL_WINDOWS11.bat      ← Run this first (as Admin)
├── templates/
│   └── finbert_v4_enhanced_ui.html ← Enhanced UI with ECharts
├── models/
│   ├── finbert_sentiment.py
│   ├── news_sentiment_real.py
│   ├── lstm_predictor.py
│   └── train_lstm.py
├── docs/
│   ├── INSTALLATION_GUIDE.md      ← This file
│   └── (7 more documentation files)
├── app_finbert_v4_dev.py          ← Main application
├── config_dev.py                   ← Configuration (change port here)
├── START_FINBERT_V4.bat           ← Run this to start server
├── requirements-full.txt
└── requirements-minimal.txt
```

---

## 🔧 Advanced Configuration

### **Change Port**:
Edit `config_dev.py`:
```python
PORT = 5001  # Change to desired port (e.g., 5002, 8080)
```

### **Disable Debug Mode**:
Edit `config_dev.py`:
```python
DEBUG = False  # Set to False for production
```

### **Enable GPU (if NVIDIA GPU available)**:
Edit `config_dev.py`:
```python
USE_GPU = True  # Enable GPU acceleration
```

---

## 📞 Getting Help

### **Documentation**:
- `README.md` - Complete package guide
- `CHANGELOG.md` - Version history and improvements
- `USER_GUIDE.md` - Feature documentation
- `CANDLESTICK_FIX.md` - ECharts migration details
- `MARKET_DATA_FIX.md` - Accuracy improvements

### **Check Logs**:
```cmd
Look in terminal window running START_FINBERT_V4.bat
Error messages will appear there
```

---

## ✅ Installation Checklist

- [ ] Python 3.8+ installed with "Add to PATH" checked
- [ ] Extracted ZIP to `C:\FinBERT_v4\`
- [ ] Ran `scripts\INSTALL_WINDOWS11.bat` as Administrator
- [ ] Chose installation type (FULL or MINIMAL)
- [ ] Installation completed successfully
- [ ] Ran `START_FINBERT_V4.bat`
- [ ] Server started (shows "Running on http://127.0.0.1:5001")
- [ ] Opened browser to http://127.0.0.1:5001
- [ ] Tested with AAPL stock symbol
- [ ] Charts loaded correctly (600px tall, no overlapping)
- [ ] News articles section appeared
- [ ] Market data is accurate

---

## 🎉 Success!

If all checklist items are complete, your FinBERT v4.0 Enhanced installation is successful!

**Next**: See `USER_GUIDE.md` to learn about all the features.

---

**Version**: 4.0-Enhanced  
**Last Updated**: October 31, 2025
