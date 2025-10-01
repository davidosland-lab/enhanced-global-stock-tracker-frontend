# Global Stock Market Tracker - Windows 11 Installation Guide

## 🚀 Quick Start

### Prerequisites
- Windows 10/11
- Python 3.8 or higher ([Download Python](https://www.python.org/downloads/))
- Internet connection for real-time data

### Installation Steps

1. **Extract the Package**
   - Extract `GSMT_Windows_Package.zip` to a location like `C:\GSMT`
   - Ensure all files are extracted properly

2. **Install Python** (if not already installed)
   - Download from https://www.python.org/downloads/
   - **IMPORTANT**: Check "Add Python to PATH" during installation

3. **Run the Application**
   - Double-click `START_GSMT_WINDOWS.bat`
   - The script will:
     - Install required dependencies (first run only)
     - Start the backend server
     - Start the frontend server
     - Open your browser to the dashboard

## 📊 Accessing the Application

Once started, you can access:
- **Main Dashboard**: http://localhost:8080/simple_working_dashboard.html
- **Backend API**: http://localhost:8002

## 🎯 Available Modules

All 6 modules are fully functional:

1. **Global Indices Tracker** - Real-time market indices
   - Shows All Ordinaries at correct -0.14% change
   - Asia, Europe, Americas markets

2. **Single Stock Tracker** - Search any stock symbol
   - Real-time prices
   - Comprehensive stock data

3. **CBA Analysis** - Commonwealth Bank focused analysis
   - Big 4 banks comparison
   - Investment metrics

4. **Technical Analysis** - Stock technical indicators
   - RSI, Moving Averages
   - Buy/Sell signals

5. **ML Predictions** - AI-powered forecasting
   - 1 day to 3 months predictions
   - Confidence scoring

6. **Document Center** - Trading resources
   - Guides and documentation
   - Templates and tools

## 🛠️ File Structure

```
GSMT/
├── backend_fixed.py           # Backend server (port 8002)
├── simple_working_dashboard.html  # Main dashboard
├── modules/                   # All 6 module files
│   ├── global_indices_tracker.html
│   ├── single_stock_tracker.html
│   ├── cba_analysis.html
│   ├── technical_analysis.html
│   ├── ml_predictions.html
│   └── document_center.html
├── START_GSMT_WINDOWS.bat    # Start application
├── STOP_GSMT_WINDOWS.bat     # Stop application
├── requirements.txt          # Python dependencies
└── README_WINDOWS.md         # This file
```

## ⚙️ Manual Installation (if automatic fails)

If the automatic installation doesn't work:

1. Open Command Prompt as Administrator
2. Navigate to the GSMT directory:
   ```cmd
   cd C:\GSMT
   ```
3. Install dependencies manually:
   ```cmd
   pip install -r requirements.txt
   ```
4. Start the backend:
   ```cmd
   python backend_fixed.py
   ```
5. In a new Command Prompt, start the frontend:
   ```cmd
   python -m http.server 8080
   ```
6. Open browser to: http://localhost:8080/simple_working_dashboard.html

## 🔧 Troubleshooting

### Python not found
- Ensure Python is installed and added to PATH
- Try running `python --version` in Command Prompt

### Port already in use
- Run `STOP_GSMT_WINDOWS.bat` to stop existing services
- Or manually change ports in the files

### Dependencies installation fails
- Try running Command Prompt as Administrator
- Update pip: `python -m pip install --upgrade pip`

### Module not loading
- Check browser console for errors (F12)
- Ensure backend is running on port 8002
- Try refreshing the page

## 🛡️ Security Notes

- This application runs locally on your machine
- No data is sent to external servers (except Yahoo Finance API)
- All processing happens on your local computer

## 📈 Data Source

- All market data from Yahoo Finance API
- Real-time updates (when markets are open)
- No synthetic or demo data

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify all prerequisites are installed
3. Ensure firewall isn't blocking ports 8002 and 8080

## ✅ Verification

The system is working correctly when:
- All Ordinaries shows ~9,135 points with -0.14% change
- All 6 modules are accessible from dashboard
- Real-time data updates are visible

## 📝 Version

- Version: 1.0
- Date: September 30, 2025
- Status: All 6 modules complete and tested

---

**Note**: This is the basic version with essential functionality. Advanced features like real-time charts will be added in future versions.