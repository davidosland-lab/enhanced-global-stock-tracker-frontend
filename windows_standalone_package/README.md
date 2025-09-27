# GSMT Enhanced Stock Tracker - Windows 11 Standalone Package

## Version 3.0 - Phase 3 & 4 ML Models Integration

### 🚀 Features

This standalone Windows package includes:

- **Advanced ML Models**:
  - LSTM Neural Networks for time-series prediction
  - Graph Neural Networks (GNN) for market relationship analysis
  - Ensemble Methods (Random Forest, XGBoost, LightGBM)
  - Reinforcement Learning for trading signals
  
- **Comprehensive Analysis**:
  - Real-time stock tracking
  - Multi-model predictions with confidence scores
  - Technical indicators (RSI, MACD, Bollinger Bands, ATR)
  - Market regime detection
  - Performance monitoring
  - Strategy backtesting

- **Fixed Issues**:
  - ✅ Single stock tracker button now responds correctly
  - ✅ Unified prediction API errors resolved
  - ✅ Performance dashboard fully functional
  - ✅ All Phase 3 & 4 models integrated

### 📋 Requirements

- Windows 11 (also works on Windows 10)
- Python 3.8 or higher
- 4GB RAM minimum (8GB recommended)
- Internet connection for market data

### 🔧 Installation

1. **Install Python** (if not already installed):
   - Download from https://python.org
   - During installation, check "Add Python to PATH"

2. **Extract Package**:
   - Extract all files to a folder (e.g., `C:\GSMT`)

3. **Run Installation**:
   ```batch
   install.bat
   ```
   This will:
   - Create a virtual environment
   - Install all dependencies
   - Create convenient shortcuts

### 🚀 Quick Start

#### Option 1: Using Batch Files (Easiest)

1. Double-click `start_server.bat` to start the backend server
2. Wait for server to start (you'll see "Server starting on: http://localhost:8000")
3. Double-click `start_tracker.bat` to open the web interface

#### Option 2: Manual Start

1. Open Command Prompt in the package directory
2. Activate virtual environment:
   ```batch
   venv\Scripts\activate.bat
   ```
3. Start the server:
   ```batch
   python enhanced_ml_backend.py
   ```
4. Open browser and navigate to:
   - Dashboard: http://localhost:8000/
   - Stock Tracker: http://localhost:8000/single_stock_tracker.html

### 💻 Using the Application

#### Stock Tracker
1. Enter a stock symbol (e.g., AAPL, MSFT, GOOGL)
2. Select update interval
3. Click "Start Tracking" to begin real-time monitoring
4. Click "Generate Prediction" for ML analysis

#### ML Predictions
- View predictions from multiple models:
  - **LSTM**: Sequential pattern recognition
  - **GNN**: Market relationship analysis
  - **Ensemble**: Combined traditional ML models
  - **RL**: Reinforcement learning trading signals

#### Performance Monitoring
- Track model accuracy over time
- View recent prediction statistics
- Compare model performance

#### Backtesting
1. Select time period (1-6 months)
2. Choose strategy (Ensemble, LSTM, or GNN)
3. Click "Run Backtest" to analyze historical performance

### 🔍 API Endpoints

The backend provides these REST API endpoints:

- `GET /` - Integrated dashboard
- `GET /health` - Health check
- `GET /api/unified-prediction/{symbol}` - Get ML predictions
- `GET /api/backtest` - Run strategy backtest
- `GET /api/performance` - Get model performance metrics

### 📊 Technical Indicators

The system calculates and displays:
- **RSI** (Relative Strength Index)
- **MACD** (Moving Average Convergence Divergence)
- **Bollinger Bands**
- **Moving Averages** (5, 20, 50, 200-day)
- **ATR** (Average True Range)
- **Support/Resistance Levels**
- **Volume Profile**
- **Trend Strength**

### 🎯 Model Details

#### Phase 3 Models:
- **Multi-timeframe Analysis**: 1-day to 90-day predictions
- **Market Regime Detection**: Bull, Bear, Sideways, High/Low Volatility
- **Adaptive Weight Optimization**: Dynamic model weighting based on performance

#### Phase 4 Models:
- **Graph Neural Networks**: Analyzes relationships between stocks, sectors, and markets
- **Temporal Fusion**: Combines time-series patterns with market events
- **Reinforcement Learning**: Q-Learning based trading signals

### 🛠️ Troubleshooting

#### Server Won't Start
- Check Python is installed: `python --version`
- Ensure port 8000 is not in use
- Run as administrator if permission errors occur

#### No Data Displayed
- Check internet connection
- Verify stock symbol is valid
- Try common symbols like AAPL or MSFT

#### Performance Issues
- Close other applications to free memory
- Reduce update interval to reduce load
- Use Task Manager to check resource usage

### 📝 Configuration

Edit `enhanced_ml_backend.py` to modify:
- Port number (default: 8000)
- Model weights
- Prediction timeframes
- Technical indicator parameters

### 🔄 Updates

To update the package:
1. Download latest version from GitHub
2. Backup your current installation
3. Extract new files
4. Run `install.bat` again

### 📚 Additional Resources

- GitHub Repository: https://github.com/davidosland-lab/enhanced-global-stock-tracker-frontend
- API Documentation: http://localhost:8000/docs (when server is running)
- FastAPI: https://fastapi.tiangolo.com/
- yfinance: https://pypi.org/project/yfinance/

### 🤝 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the API documentation at `/docs`
3. Submit issues on GitHub

### 📜 License

MIT License - See LICENSE file for details

### 🎉 Changelog

#### Version 3.0 (Current)
- Integrated Phase 3 & 4 ML models
- Fixed tracker button responsiveness
- Resolved unified prediction errors
- Added performance dashboard
- Implemented strategy backtesting
- Enhanced technical indicators
- Added market regime detection

#### Version 2.0
- Added ensemble methods
- Implemented basic neural networks
- Technical indicator integration

#### Version 1.0
- Initial release
- Basic stock tracking
- Simple predictions

---

**Note**: This is a standalone package optimized for local Windows deployment. For cloud deployment, use the Render/Netlify configuration in the main repository.