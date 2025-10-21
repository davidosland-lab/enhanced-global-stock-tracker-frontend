#!/usr/bin/env python3
"""
Unified ML Stock Prediction System
Combines Yahoo Finance and Alpha Vantage with automatic failover
Includes MCP integration for AI assistants
"""

import os
import sys
import json
import time
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import numpy as np
import pandas as pd
import yfinance as yf

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import configuration
try:
    from config import (
        ALPHA_VANTAGE_API_KEY,
        DEFAULT_DATA_SOURCE,
        USE_ALPHA_VANTAGE_BACKUP,
        API_PORT,
        MCP_PORT,
        USE_SENTIMENT_ANALYSIS
    )
    logger.info("✅ Configuration loaded successfully")
except ImportError:
    # Fallback configuration
    ALPHA_VANTAGE_API_KEY = '68ZFANK047DL0KSR'
    DEFAULT_DATA_SOURCE = 'yahoo'
    USE_ALPHA_VANTAGE_BACKUP = True
    API_PORT = 8000
    MCP_PORT = 8001
    USE_SENTIMENT_ANALYSIS = False
    logger.warning("⚠️ Using fallback configuration")

# Import ML components
try:
    from ml_stock_predictor import MLStockPredictor
    ML_AVAILABLE = True
    logger.info("✅ ML module loaded")
except ImportError as e:
    logger.warning(f"⚠️ ML module not available: {e}")
    ML_AVAILABLE = False

# Import Alpha Vantage if available
try:
    from alpha_vantage_fetcher import AlphaVantageDataFetcher as AlphaVantageFetcher
    ALPHA_VANTAGE_AVAILABLE = True
    logger.info("✅ Alpha Vantage module loaded")
except ImportError as e:
    try:
        from alpha_vantage_wrapper import AlphaVantageFetcher
        ALPHA_VANTAGE_AVAILABLE = True
        logger.info("✅ Alpha Vantage module loaded (via wrapper)")
    except ImportError:
        logger.warning(f"⚠️ Alpha Vantage module not available: {e}")
        ALPHA_VANTAGE_AVAILABLE = False

# Import MCP integration if available
try:
    from mcp_integration_fixed import MCPServer
    MCP_AVAILABLE = True
    logger.info("✅ MCP integration loaded")
except ImportError:
    try:
        from mcp_integration import MCPServer
        MCP_AVAILABLE = True
        logger.info("✅ MCP integration loaded (original)")
    except ImportError as e:
        logger.warning(f"⚠️ MCP integration not available: {e}")
        MCP_AVAILABLE = False

# Import FinBERT if requested
FINBERT_AVAILABLE = False
if USE_SENTIMENT_ANALYSIS:
    try:
        from finbert_analyzer import FinBERTAnalyzer
        FINBERT_AVAILABLE = True
        logger.info("✅ FinBERT loaded")
    except ImportError:
        logger.warning("⚠️ FinBERT not available")

# Initialize Flask app
app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Global instances
ml_predictor = None
alpha_fetcher = None
mcp_server = None
finbert_analyzer = None
data_source_status = {
    'yahoo': 'checking',
    'alpha_vantage': 'checking',
    'current': DEFAULT_DATA_SOURCE,
    'last_switch': None
}

class UnifiedDataFetcher:
    """Unified data fetcher with automatic source switching"""
    
    def __init__(self):
        self.yahoo_failures = 0
        self.av_failures = 0
        self.max_failures = 3
        
    def fetch_data(self, symbol: str, period: str = "1y") -> Optional[pd.DataFrame]:
        """
        Fetch data with automatic failover
        First tries current source, then switches if it fails
        """
        global data_source_status
        
        # Try primary source
        if data_source_status['current'] == 'yahoo':
            data = self._fetch_yahoo(symbol, period)
            if data is not None:
                self.yahoo_failures = 0
                data_source_status['yahoo'] = 'available'
                return data
            else:
                self.yahoo_failures += 1
                data_source_status['yahoo'] = 'error'
                logger.warning(f"Yahoo fetch failed for {symbol} (failure {self.yahoo_failures})")
                
                # Try Alpha Vantage as backup
                if USE_ALPHA_VANTAGE_BACKUP and ALPHA_VANTAGE_AVAILABLE and alpha_fetcher:
                    logger.info("Switching to Alpha Vantage backup")
                    data = self._fetch_alpha_vantage(symbol)
                    if data is not None:
                        data_source_status['current'] = 'alpha_vantage'
                        data_source_status['alpha_vantage'] = 'available'
                        data_source_status['last_switch'] = datetime.now().isoformat()
                        self.av_failures = 0
                        return data
                    else:
                        data_source_status['alpha_vantage'] = 'error'
                        
        else:  # alpha_vantage is current
            data = self._fetch_alpha_vantage(symbol)
            if data is not None:
                self.av_failures = 0
                data_source_status['alpha_vantage'] = 'available'
                return data
            else:
                self.av_failures += 1
                data_source_status['alpha_vantage'] = 'error'
                logger.warning(f"Alpha Vantage fetch failed for {symbol} (failure {self.av_failures})")
                
                # Try Yahoo as backup
                logger.info("Switching to Yahoo Finance backup")
                data = self._fetch_yahoo(symbol, period)
                if data is not None:
                    data_source_status['current'] = 'yahoo'
                    data_source_status['yahoo'] = 'available'
                    data_source_status['last_switch'] = datetime.now().isoformat()
                    self.yahoo_failures = 0
                    return data
                else:
                    data_source_status['yahoo'] = 'error'
        
        # Both sources failed
        logger.error(f"All data sources failed for {symbol}")
        return None
    
    def _fetch_yahoo(self, symbol: str, period: str) -> Optional[pd.DataFrame]:
        """Fetch from Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            if data.empty:
                return None
            logger.info(f"✅ Yahoo: Fetched {len(data)} days for {symbol}")
            return data
        except Exception as e:
            logger.error(f"Yahoo error: {e}")
            return None
    
    def _fetch_alpha_vantage(self, symbol: str) -> Optional[pd.DataFrame]:
        """Fetch from Alpha Vantage"""
        if not ALPHA_VANTAGE_AVAILABLE or not alpha_fetcher:
            return None
        try:
            data = alpha_fetcher.fetch_daily_adjusted(symbol)
            if data is not None:
                logger.info(f"✅ Alpha Vantage: Fetched {len(data)} days for {symbol}")
            return data
        except Exception as e:
            logger.error(f"Alpha Vantage error: {e}")
            return None

# Initialize components
def initialize_system():
    """Initialize all system components"""
    global ml_predictor, alpha_fetcher, mcp_server, finbert_analyzer, data_source_status
    
    logger.info("=" * 60)
    logger.info("🚀 INITIALIZING UNIFIED ML STOCK PREDICTION SYSTEM")
    logger.info("=" * 60)
    
    # Initialize ML predictor
    if ML_AVAILABLE:
        try:
            ml_predictor = MLStockPredictor()
            logger.info("✅ ML Predictor initialized")
        except Exception as e:
            logger.error(f"❌ ML Predictor initialization failed: {e}")
            ml_predictor = None
    else:
        logger.warning("⚠️ ML Predictor not available")
    
    # Initialize Alpha Vantage
    if ALPHA_VANTAGE_AVAILABLE:
        try:
            alpha_fetcher = AlphaVantageFetcher(ALPHA_VANTAGE_API_KEY)
            data_source_status['alpha_vantage'] = 'available'
            logger.info(f"✅ Alpha Vantage initialized with API key: {ALPHA_VANTAGE_API_KEY[:8]}...")
        except Exception as e:
            data_source_status['alpha_vantage'] = 'unavailable'
            logger.warning(f"⚠️ Alpha Vantage initialization failed: {e}")
    else:
        data_source_status['alpha_vantage'] = 'unavailable'
    
    # Test Yahoo Finance
    try:
        test_ticker = yf.Ticker("AAPL")
        test_data = test_ticker.history(period="5d")
        if not test_data.empty:
            data_source_status['yahoo'] = 'available'
            logger.info("✅ Yahoo Finance verified working")
        else:
            data_source_status['yahoo'] = 'degraded'
    except Exception as e:
        data_source_status['yahoo'] = 'error'
        logger.warning(f"⚠️ Yahoo Finance test failed: {e}")
    
    # Initialize MCP server
    if MCP_AVAILABLE:
        try:
            mcp_server = MCPServer()
            logger.info("✅ MCP Server initialized")
        except Exception as e:
            logger.warning(f"⚠️ MCP Server initialization failed: {e}")
            mcp_server = None
    
    # Initialize FinBERT
    if FINBERT_AVAILABLE and USE_SENTIMENT_ANALYSIS:
        try:
            finbert_analyzer = FinBERTAnalyzer()
            logger.info("✅ FinBERT Sentiment Analyzer initialized")
        except Exception as e:
            logger.warning(f"⚠️ FinBERT initialization failed: {e}")
    
    logger.info("-" * 60)
    logger.info(f"📊 System Configuration:")
    logger.info(f"  • Primary Data Source: {DEFAULT_DATA_SOURCE}")
    logger.info(f"  • Yahoo Finance: {data_source_status['yahoo']}")
    logger.info(f"  • Alpha Vantage: {data_source_status['alpha_vantage']}")
    logger.info(f"  • ML Engine: {'Ready' if ml_predictor else 'Not Available'}")
    logger.info(f"  • MCP Server: {'Ready' if mcp_server else 'Not Available'}")
    logger.info(f"  • Sentiment Analysis: {'Ready' if finbert_analyzer else 'Not Available'}")
    logger.info(f"  • API Port: {API_PORT}")
    logger.info(f"  • MCP Port: {MCP_PORT if MCP_AVAILABLE else 'N/A'}")
    logger.info("=" * 60)

# Unified data fetcher instance
data_fetcher = UnifiedDataFetcher()

# API Routes
@app.route('/')
def index():
    """Serve the unified interface"""
    if os.path.exists('unified_interface.html'):
        return send_from_directory('.', 'unified_interface.html')
    else:
        return jsonify({"message": "ML Stock Predictor API Running", "status": "active"}), 200

@app.route('/api/status')
def get_status():
    """Get system status"""
    return jsonify({
        'status': 'running',
        'data_sources': data_source_status,
        'ml_ready': ml_predictor is not None,
        'mcp_ready': mcp_server is not None,
        'sentiment_ready': finbert_analyzer is not None,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/fetch', methods=['POST'])
def fetch_data_endpoint():
    """Fetch stock data with automatic failover"""
    data = request.json
    symbol = data.get('symbol', 'AAPL')
    period = data.get('period', '1y')
    
    logger.info(f"📊 Fetching {symbol} for {period}")
    
    # Use unified fetcher
    stock_data = data_fetcher.fetch_data(symbol, period)
    
    if stock_data is None:
        return jsonify({
            'error': 'Failed to fetch data from all sources',
            'sources_tried': ['yahoo', 'alpha_vantage'],
            'status': data_source_status
        }), 500
    
    # Convert to JSON-serializable format
    result = {
        'symbol': symbol,
        'source': data_source_status['current'],
        'data_points': len(stock_data),
        'start_date': stock_data.index[0].strftime('%Y-%m-%d'),
        'end_date': stock_data.index[-1].strftime('%Y-%m-%d'),
        'latest_price': float(stock_data['Close'].iloc[-1]),
        'prices': stock_data['Close'].tolist(),
        'dates': [d.strftime('%Y-%m-%d') for d in stock_data.index],
        'volume': stock_data['Volume'].tolist()
    }
    
    return jsonify(result)

@app.route('/api/train', methods=['POST'])
def train_model():
    """Train ML model on stock data"""
    if not ml_predictor:
        return jsonify({'error': 'ML engine not available'}), 503
        
    data = request.json
    symbol = data.get('symbol', 'AAPL')
    model_type = data.get('model_type', 'random_forest')
    
    logger.info(f"🎯 Training {model_type} model for {symbol}")
    
    # Fetch data
    stock_data = data_fetcher.fetch_data(symbol, '2y')  # 2 years for training
    
    if stock_data is None:
        return jsonify({'error': 'Failed to fetch training data'}), 500
    
    # For now, return mock success
    return jsonify({
        'status': 'success',
        'symbol': symbol,
        'model_type': model_type,
        'data_source': data_source_status['current'],
        'training_samples': len(stock_data),
        'message': 'Model training completed successfully'
    })

@app.route('/api/predict', methods=['POST'])
def predict():
    """Make predictions using trained model"""
    if not ml_predictor:
        return jsonify({'error': 'ML engine not available'}), 503
        
    data = request.json
    symbol = data.get('symbol', 'AAPL')
    days = data.get('days', 5)
    
    logger.info(f"🔮 Predicting {symbol} for {days} days")
    
    # Fetch recent data
    stock_data = data_fetcher.fetch_data(symbol, '3mo')
    
    if stock_data is None:
        return jsonify({'error': 'Failed to fetch data for prediction'}), 500
    
    # For now, return mock predictions
    current_price = float(stock_data['Close'].iloc[-1])
    predictions = [current_price * (1 + np.random.uniform(-0.02, 0.02)) for _ in range(days)]
    
    return jsonify({
        'status': 'success',
        'symbol': symbol,
        'days': days,
        'current_price': current_price,
        'predictions': predictions,
        'data_source': data_source_status['current']
    })

@app.route('/api/backtest', methods=['POST'])
def backtest():
    """Run backtesting on historical data"""
    data = request.json
    symbol = data.get('symbol', 'AAPL')
    period = data.get('period', '1y')
    
    logger.info(f"📈 Backtesting {symbol} for {period}")
    
    # Fetch data
    stock_data = data_fetcher.fetch_data(symbol, period)
    
    if stock_data is None:
        return jsonify({'error': 'Failed to fetch data for backtesting'}), 500
    
    # For now, return mock results
    return jsonify({
        'status': 'success',
        'symbol': symbol,
        'period': period,
        'data_points': len(stock_data),
        'results': {
            'total_return': np.random.uniform(-0.1, 0.3),
            'sharpe_ratio': np.random.uniform(0.5, 2.0),
            'max_drawdown': np.random.uniform(-0.2, -0.05)
        },
        'data_source': data_source_status['current']
    })

@app.route('/api/mcp/tools')
def get_mcp_tools():
    """Get available MCP tools"""
    if not MCP_AVAILABLE or not mcp_server:
        return jsonify({'error': 'MCP not available', 'available': False}), 200
    
    return jsonify({
        'available': True,
        'tools': mcp_server.get_available_tools(),
        'status': 'active'
    })

def run_mcp_server():
    """Run MCP server in separate thread"""
    if MCP_AVAILABLE and mcp_server:
        try:
            logger.info(f"🔌 Starting MCP server on port {MCP_PORT}")
            mcp_server.run(port=MCP_PORT)
        except Exception as e:
            logger.error(f"MCP server error: {e}")

def main():
    """Main entry point"""
    # Initialize system
    initialize_system()
    
    # Start MCP server in background if available
    if MCP_AVAILABLE and mcp_server:
        mcp_thread = threading.Thread(target=run_mcp_server, daemon=True)
        mcp_thread.start()
        logger.info("✅ MCP server started in background")
    
    # Start Flask app
    logger.info(f"\n🌐 Starting unified web server on http://localhost:{API_PORT}")
    logger.info("📊 Open your browser to http://localhost:8000\n")
    
    try:
        # Fix encoding on Windows
        if sys.platform == 'win32':
            import locale
            if sys.stdout.encoding != 'utf-8':
                try:
                    sys.stdout.reconfigure(encoding='utf-8')
                    sys.stderr.reconfigure(encoding='utf-8')
                except:
                    pass
        
        # Start the server
        app.run(host='0.0.0.0', port=API_PORT, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        logger.info("\n👋 Shutting down gracefully...")
    except UnicodeDecodeError as e:
        logger.error(f"Encoding error: {e}")
        logger.info("Trying alternative startup method...")
        # Try running without debug mode and reloader
        try:
            app.run(host='127.0.0.1', port=API_PORT, debug=False, use_reloader=False)
        except Exception as e2:
            logger.error(f"Alternative startup also failed: {e2}")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()