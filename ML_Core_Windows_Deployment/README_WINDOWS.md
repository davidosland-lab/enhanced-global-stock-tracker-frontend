# ML Core Enhanced Production System
## Windows 11 Deployment Package

---

## 📋 System Requirements

- **Windows 11** (also works on Windows 10)
- **Python 3.9 or higher** ([Download Python](https://www.python.org/downloads/))
- **8GB RAM minimum** (16GB recommended)
- **2GB free disk space**
- **Internet connection** for package installation

---

## 🚀 Quick Installation

### Step 1: Extract Files
1. Extract the ZIP file to a location like `C:\MLCore\`
2. Navigate to the extracted folder

### Step 2: Install Python (if not installed)
1. Download Python from https://www.python.org/downloads/
2. **IMPORTANT**: Check "Add Python to PATH" during installation
3. Restart your computer after installation

### Step 3: Run Installation
1. Double-click `install_windows.bat`
2. Wait for installation to complete (5-10 minutes)
3. The script will create a virtual environment and install all dependencies

### Step 4: Start the System
1. Double-click `run_ml_core.bat`
2. Wait for the message "Uvicorn running on http://0.0.0.0:8000"
3. Open your browser to http://localhost:8000

---

## 📁 Package Contents

```
ML_Core_Windows_Deployment/
├── ml_core_enhanced_production.py    # Main ML system
├── ml_core_enhanced_interface.html   # Web interface
├── requirements.txt                  # Python dependencies
├── install_windows.bat               # Installation script
├── run_ml_core.bat                   # Start script
├── test_system.bat                   # Test script
├── test_ml_comprehensive.py          # Test suite
└── README_WINDOWS.md                 # This file
```

---

## 💻 Manual Installation (Advanced Users)

If the batch file doesn't work, you can install manually:

```powershell
# Open PowerShell or Command Prompt

# 1. Navigate to the extracted folder
cd C:\MLCore\ML_Core_Windows_Deployment

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
.\venv\Scripts\activate

# 4. Install requirements
pip install -r requirements.txt

# 5. Run the system
python ml_core_enhanced_production.py
```

---

## 🔧 Troubleshooting

### Python Not Found
- Ensure Python 3.9+ is installed
- Add Python to PATH (System Environment Variables)
- Restart Command Prompt after installation

### Package Installation Fails
- Check internet connection
- Try using administrator privileges
- Install packages one by one manually

### TA-Lib Installation (Optional)
TA-Lib requires special installation on Windows:
1. Download the appropriate wheel from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
2. Install using: `pip install TA_Lib-0.4.28-cp39-cp39-win_amd64.whl`
3. The system works without it using fallback calculations

### Port 8000 Already in Use
- Change the port in `ml_core_enhanced_production.py`
- Look for: `uvicorn.run(app, host="0.0.0.0", port=8000)`
- Change to: `uvicorn.run(app, host="0.0.0.0", port=8080)`

---

## 🎯 Features

### ML Models
- RandomForest (Primary)
- GradientBoosting
- Support Vector Machine (SVM)
- Neural Network
- XGBoost (if available)

### Ensemble Methods
- Voting Ensemble
- Stacking Ensemble

### Technical Indicators (35 total)
- Price-based indicators
- Momentum indicators
- Volatility indicators
- Volume indicators

### Performance
- SQLite caching (50x speed improvement)
- Training time: 3-17 seconds
- Real-time predictions
- Comprehensive backtesting

---

## 📊 Using the System

### Training a Model
```python
POST http://localhost:8000/api/train
{
    "symbol": "AAPL",
    "ensemble_type": "voting",
    "days": 480
}
```

### Running Backtest
```python
POST http://localhost:8000/api/backtest
{
    "symbol": "AAPL",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
}
```

### Getting Predictions
```python
POST http://localhost:8000/api/predict
{
    "symbol": "AAPL"
}
```

---

## 🔐 Security Notes

- The system runs locally on your machine
- No data is sent to external servers (except market data from Yahoo Finance)
- All models and predictions are stored locally
- Use firewall rules if exposing to network

---

## 📈 Performance Tips

1. **First Run**: Initial data fetch may take longer
2. **Cache**: System gets faster with use (SQLite caching)
3. **RAM**: Close other applications for better performance
4. **CPU**: Training uses multiple cores automatically

---

## 🆘 Support

### Common Issues & Solutions

**Issue**: "Python is not recognized"
**Solution**: Reinstall Python with "Add to PATH" checked

**Issue**: "Module not found" errors
**Solution**: Activate virtual environment first

**Issue**: System runs slowly
**Solution**: Increase available RAM, close other applications

**Issue**: Cannot connect to localhost:8000
**Solution**: Check Windows Firewall, ensure no other service uses port 8000

---

## 📝 Version Information

- **System Version**: 2.0
- **Python Required**: 3.9+
- **Last Updated**: October 2024
- **Models**: 5 ensemble models
- **Features**: 35 technical indicators

---

## ✅ Testing the Installation

After installation, run `test_system.bat` to verify:
- System status
- Model training
- Backtesting engine
- Cache performance
- API endpoints

---

## 🎉 Success Indicators

You'll know the system is working when:
1. Browser shows system status at http://localhost:8000
2. Training completes in 3-17 seconds
3. Backtesting returns metrics
4. Cache hit rate improves over time

---

**Enjoy using the ML Core Enhanced Production System!**

For updates, visit: https://github.com/davidosland-lab/enhanced-global-stock-tracker-frontend