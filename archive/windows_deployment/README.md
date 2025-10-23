# Enhanced Stock Tracker ML System - Windows 11 Standalone

## Overview
This is a complete standalone installation package for the Enhanced Stock Tracker with integrated Phase 3 & 4 ML models. It runs entirely on your local Windows 11 machine without requiring any cloud services.

## Features
- **9 Advanced ML Models**:
  - LSTM Neural Network
  - GRU Neural Network
  - Transformer Model
  - CNN-LSTM Hybrid
  - Graph Neural Networks (GNN)
  - Random Forest
  - XGBoost
  - LightGBM
  - Reinforcement Learning (Q-Learning)

- **Technical Analysis**:
  - RSI, MACD, Bollinger Bands
  - Moving Averages (5, 20, 50, 200)
  - ATR, Volume Analysis
  - Support/Resistance Levels

- **Prediction Capabilities**:
  - Multi-timeframe predictions (1d, 5d, 30d, 90d)
  - Ensemble predictions combining all models
  - Confidence scoring
  - Trend analysis

## System Requirements
- Windows 11 (or Windows 10)
- Python 3.8 or higher
- 4GB RAM minimum (8GB recommended)
- Internet connection (for real-time stock data)
- 500MB free disk space

## Installation

### Step 1: Install Python
If you don't have Python installed:
1. Download Python from https://www.python.org/downloads/
2. During installation, **CHECK** "Add Python to PATH"
3. Complete the installation

### Step 2: Run Setup
1. Double-click `setup.bat`
2. Wait for all packages to install (this may take 5-10 minutes)
3. The setup will create a virtual environment and install all dependencies

## Usage

### Quick Start
1. Double-click `run_all.bat`
2. The backend server will start
3. The dashboard will open in your browser automatically
4. Enter a stock symbol (e.g., AAPL, MSFT, GOOGL)
5. Select timeframe
6. Click "Get Prediction"

### Manual Start
If you prefer to start components manually:

1. **Start Backend Server**:
   - Open Command Prompt
   - Navigate to this directory
   - Run: `venv\Scripts\activate`
   - Run: `python backend_server.py`

2. **Open Dashboard**:
   - Open browser
   - Navigate to: http://localhost:8000/dashboard

## API Endpoints

The system provides several API endpoints:

- `GET /` - Main page
- `GET /dashboard` - Interactive dashboard
- `GET /health` - System health check
- `GET /api/predict/{symbol}?timeframe={1d|5d|30d|90d}` - Get prediction
- `GET /api/performance` - Model performance metrics

## Troubleshooting

### Server won't start
- Ensure Python is installed and in PATH
- Run `python --version` to check
- Make sure port 8000 is not in use
- Check firewall settings

### No predictions appearing
- Check internet connection (needed for stock data)
- Verify the stock symbol is valid
- Check server console for errors

### Installation fails
- Run Command Prompt as Administrator
- Ensure you have internet connection
- Try running `pip install --upgrade pip` first
- Check available disk space

## Model Details

### Neural Networks
- **LSTM**: Long Short-Term Memory for sequential patterns
- **GRU**: Gated Recurrent Unit for time series
- **Transformer**: Attention-based architecture
- **CNN-LSTM**: Convolutional features + sequential processing

### Ensemble Methods
- **Random Forest**: Multiple decision trees
- **XGBoost**: Gradient boosting
- **LightGBM**: Fast gradient boosting

### Advanced Models
- **GNN**: Graph Neural Networks for market relationships
- **RL**: Q-Learning for trading signals

## Performance Notes
- Predictions typically take 2-5 seconds
- First prediction may be slower (model initialization)
- System caches data for faster subsequent predictions
- All processing happens locally on your machine

## Data Sources
- Real-time stock data from Yahoo Finance
- No data is sent to external servers
- All ML processing is done locally

## Security & Privacy
- Runs entirely on your local machine
- No cloud dependencies for predictions
- Stock data fetched directly from Yahoo Finance
- No user data collection or tracking

## Support
For issues or questions:
1. Check the troubleshooting section
2. Review server console for error messages
3. Ensure all requirements are met
4. Restart the system if needed

## Version
Version 3.0.0 - Phase 3 & 4 ML Models Integrated

## License
MIT License - Free for personal and commercial use

---

**Note**: This is a demonstration/educational system. Always do your own research before making investment decisions. Past performance does not guarantee future results.