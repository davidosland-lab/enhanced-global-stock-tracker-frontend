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
import asyncio
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
except ImportError:
    # Fallback configuration
    ALPHA_VANTAGE_API_KEY = '68ZFANK047DL0KSR'
    DEFAULT_DATA_SOURCE = 'yahoo'
    USE_ALPHA_VANTAGE_BACKUP = True
    API_PORT = 8000
    MCP_PORT = 8001
    USE_SENTIMENT_ANALYSIS = False

# Import ML components
try:
    from ml_stock_predictor import MLStockPredictor
except ImportError:
    logger.warning("ML module not found, creating minimal version")
    from ml_stock_multi_source import MLStockPredictor

# Import Alpha Vantage if available
try:
    from alpha_vantage_fetcher import AlphaVantageFetcher
    ALPHA_VANTAGE_AVAILABLE = True
except ImportError:
    logger.warning("Alpha Vantage module not available")
    ALPHA_VANTAGE_AVAILABLE = False

# Import MCP integration if available
try:
    from mcp_integration import MCPServer
    MCP_AVAILABLE = True
except ImportError:
    logger.warning("MCP integration not available")
    MCP_AVAILABLE = False

# Import FinBERT if requested
if USE_SENTIMENT_ANALYSIS:
    try:
        from finbert_analyzer import FinBERTAnalyzer
        FINBERT_AVAILABLE = True
    except ImportError:
        logger.warning("FinBERT not available")
        FINBERT_AVAILABLE = False
else:
    FINBERT_AVAILABLE = False

# Initialize Flask app
app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Global instances
ml_predictor = None
alpha_fetcher = None
mcp_server = None
finbert_analyzer = None
data_source_status = {
    'yahoo': 'available',
    'alpha_vantage': 'available' if ALPHA_VANTAGE_AVAILABLE else 'unavailable',
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
                return data
            else:
                self.yahoo_failures += 1
                logger.warning(f"Yahoo fetch failed for {symbol} (failure {self.yahoo_failures})")
                
                # Try Alpha Vantage as backup
                if USE_ALPHA_VANTAGE_BACKUP and ALPHA_VANTAGE_AVAILABLE:
                    logger.info("Switching to Alpha Vantage backup")
                    data = self._fetch_alpha_vantage(symbol)
                    if data is not None:
                        data_source_status['current'] = 'alpha_vantage'
                        data_source_status['last_switch'] = datetime.now().isoformat()
                        self.av_failures = 0
                        return data
                        
        else:  # alpha_vantage is current
            data = self._fetch_alpha_vantage(symbol)
            if data is not None:
                self.av_failures = 0
                return data
            else:
                self.av_failures += 1
                logger.warning(f"Alpha Vantage fetch failed for {symbol} (failure {self.av_failures})")
                
                # Try Yahoo as backup
                logger.info("Switching to Yahoo Finance backup")
                data = self._fetch_yahoo(symbol, period)
                if data is not None:
                    data_source_status['current'] = 'yahoo'
                    data_source_status['last_switch'] = datetime.now().isoformat()
                    self.yahoo_failures = 0
                    return data
        
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
    global ml_predictor, alpha_fetcher, mcp_server, finbert_analyzer
    
    logger.info("=" * 60)
    logger.info("🚀 INITIALIZING UNIFIED ML STOCK PREDICTION SYSTEM")
    logger.info("=" * 60)
    
    # Initialize ML predictor
    try:
        ml_predictor = MLStockPredictor()
        logger.info("✅ ML Predictor initialized")
    except Exception as e:
        logger.error(f"❌ ML Predictor initialization failed: {e}")
        sys.exit(1)
    
    # Initialize Alpha Vantage
    if ALPHA_VANTAGE_AVAILABLE:
        try:
            alpha_fetcher = AlphaVantageFetcher(ALPHA_VANTAGE_API_KEY)
            logger.info(f"✅ Alpha Vantage initialized with API key: {ALPHA_VANTAGE_API_KEY[:8]}...")
        except Exception as e:
            logger.warning(f"⚠️ Alpha Vantage initialization failed: {e}")
    
    # Initialize MCP server
    if MCP_AVAILABLE:
        try:
            mcp_server = MCPServer(ml_predictor)
            logger.info("✅ MCP Server initialized")
        except Exception as e:
            logger.warning(f"⚠️ MCP Server initialization failed: {e}")
    
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
    logger.info(f"  • Alpha Vantage Backup: {USE_ALPHA_VANTAGE_BACKUP}")
    logger.info(f"  • MCP Integration: {MCP_AVAILABLE}")
    logger.info(f"  • Sentiment Analysis: {FINBERT_AVAILABLE and USE_SENTIMENT_ANALYSIS}")
    logger.info(f"  • API Port: {API_PORT}")
    logger.info(f"  • MCP Port: {MCP_PORT if MCP_AVAILABLE else 'N/A'}")
    logger.info("=" * 60)

# Unified data fetcher instance
data_fetcher = UnifiedDataFetcher()

# API Routes
@app.route('/')
def index():
    """Serve the unified interface"""
    return send_from_directory('.', 'unified_interface.html')

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
            'sources_tried': ['yahoo', 'alpha_vantage']
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
    data = request.json
    symbol = data.get('symbol', 'AAPL')
    model_type = data.get('model_type', 'random_forest')
    
    logger.info(f"🎯 Training {model_type} model for {symbol}")
    
    # Fetch data
    stock_data = data_fetcher.fetch_data(symbol, '2y')  # 2 years for training
    
    if stock_data is None:
        return jsonify({'error': 'Failed to fetch training data'}), 500
    
    # Prepare features
    try:
        features = ml_predictor.prepare_features(stock_data)
        
        # Train model
        metrics = ml_predictor.train_model(features, model_type=model_type)
        
        # Save model
        ml_predictor.save_model(f"{symbol}_{model_type}.pkl")
        
        return jsonify({
            'status': 'success',
            'symbol': symbol,
            'model_type': model_type,
            'data_source': data_source_status['current'],
            'training_samples': len(features),
            'metrics': metrics
        })
    except Exception as e:
        logger.error(f"Training failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/predict', methods=['POST'])
def predict():
    """Make predictions using trained model"""
    data = request.json
    symbol = data.get('symbol', 'AAPL')
    days = data.get('days', 5)
    
    logger.info(f"🔮 Predicting {symbol} for {days} days")
    
    # Fetch recent data
    stock_data = data_fetcher.fetch_data(symbol, '3mo')
    
    if stock_data is None:
        return jsonify({'error': 'Failed to fetch data for prediction'}), 500
    
    try:
        # Make prediction
        predictions = ml_predictor.predict(stock_data, days=days)
        
        return jsonify({
            'status': 'success',
            'symbol': symbol,
            'days': days,
            'current_price': float(stock_data['Close'].iloc[-1]),
            'predictions': predictions,
            'data_source': data_source_status['current']
        })
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        return jsonify({'error': str(e)}), 500

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
    
    try:
        # Run backtest
        results = ml_predictor.backtest(stock_data)
        
        return jsonify({
            'status': 'success',
            'symbol': symbol,
            'period': period,
            'results': results,
            'data_source': data_source_status['current']
        })
    except Exception as e:
        logger.error(f"Backtesting failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sentiment', methods=['POST'])
def analyze_sentiment():
    """Analyze sentiment (if available)"""
    if not FINBERT_AVAILABLE or not finbert_analyzer:
        return jsonify({'error': 'Sentiment analysis not available'}), 503
    
    data = request.json
    text = data.get('text', '')
    
    try:
        sentiment = finbert_analyzer.analyze(text)
        return jsonify(sentiment)
    except Exception as e:
        logger.error(f"Sentiment analysis failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/mcp/tools')
def get_mcp_tools():
    """Get available MCP tools"""
    if not MCP_AVAILABLE or not mcp_server:
        return jsonify({'error': 'MCP not available'}), 503
    
    return jsonify({
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
        app.run(host='0.0.0.0', port=API_PORT, debug=False)
    except KeyboardInterrupt:
        logger.info("\n👋 Shutting down gracefully...")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()