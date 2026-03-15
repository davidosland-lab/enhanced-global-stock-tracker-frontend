# FinBERT v4.0 Enhanced - Windows 11 Deployment Guide

**Complete Installation and Setup Instructions for Local Windows 11 Machine**

---

## 📋 System Requirements

### Minimum Requirements
- **OS**: Windows 11 (64-bit)
- **Python**: 3.8 or higher
- **RAM**: 4 GB minimum, 8 GB recommended
- **Disk Space**: 2 GB (5 GB with TensorFlow)
- **Internet**: Required for fetching market data

### Recommended Specifications
- **OS**: Windows 11 (latest updates)
- **Python**: 3.10 or 3.11
- **RAM**: 16 GB
- **Disk Space**: 10 GB free
- **Processor**: Intel i5/AMD Ryzen 5 or better
- **Internet**: Broadband connection

---

## 🚀 Quick Installation (3 Steps)

### Step 1: Install Python
1. Download Python from: https://www.python.org/downloads/
2. Run installer
3. **IMPORTANT**: Check "Add Python to PATH"
4. Click "Install Now"
5. Verify installation:
   ```cmd
   python --version
   ```

### Step 2: Extract Package
1. Extract the ZIP file to your desired location
   - Example: `C:\Users\YourName\Documents\FinBERT_v4.0_Enhanced\`
2. Avoid paths with spaces if possible

### Step 3: Run Installation Script
1. Navigate to the extracted folder
2. Double-click: `INSTALL_WINDOWS11_ENHANCED.bat`
3. Follow the prompts
4. Choose whether to install TensorFlow (optional)
5. Wait for installation to complete (5-10 minutes)

---

## 📦 What Gets Installed

### Core Packages (Required)
```
Flask 3.0.0             - Web framework
Flask-CORS 4.0.0        - Cross-origin support
NumPy 1.24.3            - Numerical computing
Pandas 2.0.3            - Data manipulation
scikit-learn 1.3.0      - Machine learning features
```

### Optional Packages
```
TensorFlow 2.15.0       - Deep learning (LSTM training)
                         Size: ~600MB
                         Benefits: Full LSTM training capabilities
                         Without it: Fallback prediction methods work
```

### Virtual Environment
- Created in: `venv\` folder
- Isolates packages from system Python
- Prevents version conflicts

---

## 🎯 Starting the System

### Method 1: Quick Start (Recommended)
```cmd
Double-click: START_V4_ENHANCED.bat
```
- Server starts automatically
- Opens on http://localhost:5001
- Press Ctrl+C to stop

### Method 2: Manual Start
```cmd
# Open Command Prompt in project folder
venv\Scripts\activate
python app_finbert_v4_dev.py
```

### Method 3: Background Service (Advanced)
```cmd
# Install PM2 for Node.js or create Windows Service
# See Advanced Configuration section below
```

---

## 🌐 Accessing the System

### Local Access
```
URL: http://localhost:5001
```

### Network Access (Optional)
```
URL: http://YOUR_IP_ADDRESS:5001
```
- Enable Windows Firewall exception for port 5001
- Find your IP: `ipconfig` in Command Prompt
- Look for IPv4 Address

---

## 📊 Features Overview

### 1. Candlestick Charts
- **Access**: Click "Candlestick" button in UI
- **Shows**: Open, High, Low, Close (OHLC) prices
- **Colors**: Green (up days), Red (down days)
- **Interaction**: Zoom with scroll, pan with drag

### 2. Volume Chart
- **Location**: Below main chart
- **Shows**: Trading volume per period
- **Colors**: Green (price up), Red (price down)
- **Format**: M (millions), K (thousands)

### 3. Training Interface
- **Access**: Click "Train Model" button
- **Inputs**: Symbol, Epochs (10-200)
- **Progress**: Real-time progress bar
- **Result**: Model auto-reloads when done

### 4. Extended Timeframes
- **Options**: 1D, 5D, 1M, 3M, 6M, 1Y, 2Y
- **Intraday**: 1D and 5D (5-minute intervals)
- **Daily**: 1M through 2Y
- **Data Source**: Yahoo Finance API

### 5. Market Support
- **US Stocks**: NASDAQ, NYSE symbols
- **Australian Stocks**: ASX symbols with .AX suffix
- **Examples**: AAPL, MSFT, CBA.AX, BHP.AX

---

## 🎓 Training Models

### From UI (Easiest)
1. Click "Train Model" button (top-right)
2. Enter symbol (e.g., AAPL or CBA.AX)
3. Set epochs (recommended: 50)
4. Click "Start Training"
5. Watch progress bar
6. Model reloads automatically

### From Command Line
1. Double-click: `TRAIN_MODEL.bat`
2. Enter symbol when prompted
3. Enter epochs (default: 50)
4. Confirm and wait
5. Restart server to load new model

### From Python Script
```cmd
venv\Scripts\activate
python models/train_lstm.py --symbol AAPL --epochs 50 --sequence_length 30
```

### Training Recommendations
```
Quick Test:     20-30 epochs (2-3 minutes)
Recommended:    50 epochs (5-10 minutes)
Better Accuracy: 100 epochs (10-15 minutes)
Best Accuracy:  200 epochs (15-20 minutes)
```

### Best Stocks to Train
- Large-cap stocks (AAPL, MSFT, GOOGL, AMZN)
- High-volume stocks
- Stocks you trade frequently
- Australian: CBA.AX, BHP.AX, WBC.AX

---

## 🔧 Configuration

### Port Configuration
Edit `config_dev.py`:
```python
PORT = 5001  # Change to your preferred port
```

### Debug Mode
Edit `config_dev.py`:
```python
DEBUG = True   # Development mode (auto-reload)
DEBUG = False  # Production mode (better performance)
```

### CORS Origins (Network Access)
Edit `config_dev.py`:
```python
CORS_ORIGINS = ['http://localhost:5001', 'http://YOUR_IP:5001']
```

### Features Toggle
Edit `config_dev.py`:
```python
FEATURES = {
    'USE_LSTM': True,        # Enable LSTM predictions
    'USE_XGBOOST': False,    # Additional models (future)
    'ENABLE_WEBSOCKET': False,
    'ENABLE_DATABASE': False
}
```

---

## 🛠️ Advanced Configuration

### Run as Windows Service

#### Using NSSM (Non-Sucking Service Manager)
1. Download NSSM: https://nssm.cc/download
2. Extract to folder (e.g., `C:\nssm\`)
3. Open Command Prompt as Administrator
4. Navigate to NSSM folder
5. Run:
   ```cmd
   nssm install FinBERT_v4
   ```
6. Configure:
   - Path: `C:\Path\To\venv\Scripts\python.exe`
   - Startup directory: `C:\Path\To\FinBERT_v4.0_Development\`
   - Arguments: `app_finbert_v4_dev.py`
7. Start service:
   ```cmd
   nssm start FinBERT_v4
   ```

### Auto-Start on Boot
1. Create shortcut to `START_V4_ENHANCED.bat`
2. Press `Win + R`
3. Type: `shell:startup`
4. Copy shortcut to Startup folder

### Network Firewall Configuration
```cmd
# Open Command Prompt as Administrator
netsh advfirewall firewall add rule name="FinBERT v4.0" dir=in action=allow protocol=TCP localport=5001
```

---

## 📁 File Structure

```
FinBERT_v4.0_Development/
│
├── app_finbert_v4_dev.py              # Main Flask server
├── finbert_v4_enhanced_ui.html        # Enhanced UI
├── config_dev.py                      # Configuration
│
├── models/
│   ├── train_lstm.py                  # Training script
│   ├── lstm_predictor.py              # Prediction module
│   └── lstm_*_metadata.json           # Trained models
│
├── venv/                              # Virtual environment
│
├── INSTALL_WINDOWS11_ENHANCED.bat     # Installation script
├── START_V4_ENHANCED.bat              # Startup script
├── TRAIN_MODEL.bat                    # Training script
├── STOP_SYSTEM.bat                    # Stop script
│
├── requirements-windows.txt           # Dependencies
├── WINDOWS11_QUICK_START.txt          # Quick guide
├── WINDOWS11_DEPLOYMENT_GUIDE.md      # This file
│
└── Documentation/
    ├── README_V4_COMPLETE.md          # Full manual
    ├── QUICK_ACCESS_GUIDE.md          # Usage guide
    └── CBA_AX_TRAINING_COMPLETE.md    # Training examples
```

---

## 🚨 Troubleshooting

### Installation Issues

#### "Python is not recognized"
**Cause**: Python not in PATH
**Solution**:
1. Reinstall Python with "Add to PATH" checked
2. Or add manually:
   - Right-click "This PC" → Properties
   - Advanced system settings → Environment Variables
   - Add Python path to System PATH

#### "Unable to create virtual environment"
**Cause**: Permissions or disk space
**Solution**:
1. Run Command Prompt as Administrator
2. Check disk space (need 2-5 GB)
3. Disable antivirus temporarily

#### "pip install fails"
**Cause**: Network issues or outdated pip
**Solution**:
```cmd
python -m pip install --upgrade pip
pip install --no-cache-dir -r requirements-windows.txt
```

### Runtime Issues

#### "Port 5001 already in use"
**Solution**:
1. Find process using port:
   ```cmd
   netstat -ano | findstr :5001
   ```
2. Kill process:
   ```cmd
   taskkill /PID <process_id> /F
   ```
3. Or change port in `config_dev.py`

#### "ModuleNotFoundError"
**Solution**:
```cmd
venv\Scripts\activate
pip install -r requirements-windows.txt
```

#### Charts not loading
**Solution**:
1. Check internet connection
2. Try different stock symbol
3. Clear browser cache (Ctrl+Shift+Del)
4. Try different time period (1M first)

#### Training fails
**Solution**:
1. Check symbol is correct (AAPL not Apple)
2. For ASX stocks, add .AX (CBA.AX)
3. Ensure internet connection
4. Try lower epochs (20-30)
5. Check TensorFlow installation

### Performance Issues

#### Server slow or unresponsive
**Solution**:
1. Close other applications
2. Increase system RAM
3. Set DEBUG=False in config_dev.py
4. Use production WSGI server (see below)

#### High CPU usage
**Solution**:
1. Reduce number of training epochs
2. Close unnecessary browser tabs
3. Check for infinite loops in logs

---

## 🔒 Security Considerations

### Local Development
- Default: Accessible only from localhost
- Safe for personal use

### Network Access
If enabling network access:
1. Use strong authentication (not included by default)
2. Enable HTTPS (requires SSL certificate)
3. Restrict firewall to trusted IPs only
4. Keep system updated

### API Keys
- System uses Yahoo Finance (no API key required)
- No sensitive data stored locally
- Models saved as JSON (no personal info)

---

## 📈 Performance Optimization

### For Better Speed
1. Use production WSGI server:
   ```cmd
   pip install waitress
   waitress-serve --port=5001 app_finbert_v4_dev:app
   ```

2. Disable debug mode:
   ```python
   # In config_dev.py
   DEBUG = False
   ```

3. Use TensorFlow CPU-only (if no GPU):
   ```cmd
   pip install tensorflow-cpu==2.15.0
   ```

### For Lower Resource Usage
1. Reduce epochs during training
2. Use lightweight models (without TensorFlow)
3. Close unused browser tabs
4. Limit concurrent analyses

---

## 🔄 Updating the System

### Update Code
1. Download new version
2. Extract to same location (overwrite files)
3. Keep `venv\` folder (don't delete)
4. Run: `INSTALL_WINDOWS11_ENHANCED.bat` again

### Update Packages
```cmd
venv\Scripts\activate
pip install --upgrade Flask Flask-CORS numpy pandas scikit-learn
```

### Update Python
1. Download new Python version
2. Uninstall old version
3. Install new version with PATH
4. Recreate virtual environment:
   ```cmd
   rmdir /s /q venv
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements-windows.txt
   ```

---

## 💾 Backup and Restore

### Backup Trained Models
```cmd
# Copy models folder
xcopy models models_backup\ /E /I /Y
```

### Backup Configuration
```cmd
# Copy config file
copy config_dev.py config_dev_backup.py
```

### Restore
```cmd
# Restore models
xcopy models_backup\ models\ /E /I /Y

# Restore config
copy config_dev_backup.py config_dev.py
```

---

## 📞 Support Resources

### Documentation
- `WINDOWS11_QUICK_START.txt` - Quick reference
- `README_V4_COMPLETE.md` - Comprehensive manual
- `QUICK_ACCESS_GUIDE.md` - Feature guide
- `TROUBLESHOOTING.txt` - Common issues

### GitHub
- Repository: davidosland-lab/enhanced-global-stock-tracker-frontend
- Pull Request #7 - Latest features
- Issues: Report bugs or request features

### Logs
- Server logs: Check Command Prompt output
- Error logs: `logs/` folder (if enabled)
- Training logs: Console output during training

---

## ✅ Post-Installation Checklist

- [ ] Python 3.8+ installed with PATH
- [ ] Virtual environment created (`venv\` folder exists)
- [ ] All packages installed successfully
- [ ] TensorFlow installed (optional)
- [ ] Server starts without errors
- [ ] Can access http://localhost:5001
- [ ] Can analyze at least one stock
- [ ] Candlestick charts display correctly
- [ ] Volume chart shows below main chart
- [ ] Training modal opens
- [ ] Can switch between chart types

---

## 🎉 You're Ready!

Your FinBERT v4.0 Enhanced system is now fully deployed on Windows 11.

**Next Steps**:
1. Double-click `START_V4_ENHANCED.bat`
2. Open http://localhost:5001
3. Start analyzing stocks!

**Happy Trading!** 📈

---

**Version**: 4.0-dev Enhanced  
**Platform**: Windows 11  
**Date**: October 30, 2025  
**Status**: Production Ready
