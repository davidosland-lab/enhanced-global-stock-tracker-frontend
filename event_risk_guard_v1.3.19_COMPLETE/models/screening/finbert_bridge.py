"""
FinBERT Bridge Module
=====================
Adapter that connects Overnight Stock Screener to FinBERT v4.4.4 components.

**Architecture**: Adapter/Bridge Pattern
- NO modifications to FinBERT v4.4.4 code
- Read-only access to FinBERT modules
- Clean interface for screener integration
- Graceful fallback when components unavailable

**Provides Access To**:
1. Real LSTM neural network predictions
2. Real FinBERT transformer sentiment analysis
3. Real news scraping from Yahoo Finance and Finviz

**Usage**:
    from models.screening.finbert_bridge import get_finbert_bridge
    
    bridge = get_finbert_bridge()
    if bridge.is_available()['lstm_available']:
        lstm_result = bridge.get_lstm_prediction('AAPL', historical_data)
    
    if bridge.is_available()['sentiment_available']:
        sentiment_result = bridge.get_sentiment_analysis('AAPL')
"""

import sys
import os
from pathlib import Path
from typing import Dict, Optional, List
import logging
import pandas as pd
import numpy as np
from datetime import datetime

# Setup logging
logger = logging.getLogger(__name__)

# Calculate FinBERT path relative to this file
FINBERT_PATH = Path(__file__).parent.parent.parent / 'finbert_v4.4.4'
FINBERT_MODELS_PATH = FINBERT_PATH / 'models'

# Add FinBERT to Python path (read-only access)
if FINBERT_PATH.exists():
    sys.path.insert(0, str(FINBERT_PATH))
    sys.path.insert(0, str(FINBERT_MODELS_PATH))
    logger.info(f"✓ Added FinBERT path to sys.path: {FINBERT_PATH}")
else:
    logger.warning(f"⚠ FinBERT path not found: {FINBERT_PATH}")

# Import FinBERT modules (with error handling)
try:
    from lstm_predictor import StockLSTMPredictor
    LSTM_AVAILABLE = True
    logger.info("✓ LSTM predictor imported successfully")
except ImportError as e:
    LSTM_AVAILABLE = False
    logger.warning(f"⚠ LSTM predictor not available: {e}")
    StockLSTMPredictor = None

try:
    from finbert_sentiment import FinBERTSentimentAnalyzer
    SENTIMENT_ANALYZER_AVAILABLE = True
    logger.info("✓ FinBERT sentiment analyzer imported successfully")
except ImportError as e:
    SENTIMENT_ANALYZER_AVAILABLE = False
    logger.warning(f"⚠ FinBERT sentiment analyzer not available: {e}")
    FinBERTSentimentAnalyzer = None

try:
    from news_sentiment_real import get_sentiment_sync
    NEWS_SENTIMENT_AVAILABLE = True
    logger.info("✓ News sentiment module imported successfully")
except ImportError as e:
    NEWS_SENTIMENT_AVAILABLE = False
    logger.warning(f"⚠ News sentiment module not available: {e}")
    get_sentiment_sync = None


class FinBERTBridge:
    """
    Bridge class providing Overnight Screener access to FinBERT v4.4.4 components
    
    **Design Pattern**: Adapter/Bridge
    - Provides unified interface to FinBERT components
    - Handles component availability gracefully
    - NO modifications to FinBERT code
    - Translates between screener and FinBERT data formats
    
    **Components**:
    - LSTM Predictor: Real neural network predictions
    - Sentiment Analyzer: Real FinBERT transformer analysis
    - News Scraper: Real news from Yahoo Finance/Finviz
    """
    
    def __init__(self):
        """Initialize FinBERT bridge with component availability checking"""
        self.lstm_predictor = None
        self.sentiment_analyzer = None
        self._lstm_initialized = False
        self._sentiment_initialized = False
        
        # Initialize components
        self._init_lstm()
        self._init_sentiment()
        
        logger.info(f"FinBERT Bridge initialized: LSTM={self._lstm_initialized}, Sentiment={self._sentiment_initialized}")
    
    def _init_lstm(self):
        """Initialize LSTM predictor component"""
        if not LSTM_AVAILABLE or StockLSTMPredictor is None:
            logger.warning("LSTM predictor not available")
            return
        
        try:
            # Initialize LSTM predictor with 60-day sequence length
            self.lstm_predictor = StockLSTMPredictor(sequence_length=60)
            self._lstm_initialized = True
            logger.info("✓ LSTM predictor initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize LSTM predictor: {e}")
            self._lstm_initialized = False
    
    def _init_sentiment(self):
        """Initialize FinBERT sentiment analyzer component"""
        if not SENTIMENT_ANALYZER_AVAILABLE or FinBERTSentimentAnalyzer is None:
            logger.warning("FinBERT sentiment analyzer not available")
            return
        
        try:
            # Initialize FinBERT analyzer with default model
            self.sentiment_analyzer = FinBERTSentimentAnalyzer(model_name="ProsusAI/finbert")
            self._sentiment_initialized = True
            logger.info("✓ FinBERT sentiment analyzer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize sentiment analyzer: {e}")
            self._sentiment_initialized = False
    
    def is_available(self) -> Dict[str, bool]:
        """
        Check which FinBERT components are available
        
        Returns:
            Dict with availability status for each component:
            {
                'lstm_available': bool,
                'sentiment_available': bool,
                'news_available': bool
            }
        """
        return {
            'lstm_available': self._lstm_initialized and self.lstm_predictor is not None,
            'sentiment_available': self._sentiment_initialized and self.sentiment_analyzer is not None,
            'news_available': NEWS_SENTIMENT_AVAILABLE and get_sentiment_sync is not None
        }
    
    def get_lstm_prediction(self, symbol: str, historical_data: pd.DataFrame) -> Optional[Dict]:
        """
        Get REAL LSTM prediction from FinBERT's trained neural network model
        
        **Data Flow**:
        1. Screener provides historical price data
        2. Bridge passes to FinBERT LSTM predictor
        3. LSTM loads trained .h5 model for symbol
        4. Neural network generates prediction
        5. Bridge translates result to screener format
        
        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL', 'MSFT')
            historical_data: DataFrame with columns ['Close', 'Open', 'High', 'Low', 'Volume']
                            Minimum 60 days of data required for LSTM
        
        Returns:
            Dict with prediction results:
            {
                'direction': float,        # -1.0 to 1.0 (bearish to bullish)
                'confidence': float,       # 0.0 to 1.0
                'predicted_price': float,  # Next day predicted close price
                'model_trained': bool,     # True if model exists for symbol
                'data_sufficient': bool,   # True if enough data provided
                'prediction_date': str     # ISO format datetime
            }
            
            Returns None if:
            - LSTM component not available
            - Model not trained for symbol
            - Insufficient historical data
            - Prediction fails
        """
        if not self._lstm_initialized or self.lstm_predictor is None:
            logger.debug(f"LSTM not available for {symbol}")
            return None
        
        try:
            # Validate input data
            if historical_data is None or len(historical_data) < 60:
                logger.debug(f"Insufficient data for LSTM prediction: {symbol} ({len(historical_data) if historical_data is not None else 0} days)")
                return {
                    'direction': 0.0,
                    'confidence': 0.0,
                    'predicted_price': None,
                    'model_trained': False,
                    'data_sufficient': False,
                    'prediction_date': datetime.now().isoformat()
                }
            
            # Check if model exists for symbol
            model_path = FINBERT_PATH / 'models' / 'trained' / f'{symbol}_lstm.h5'
            if not model_path.exists():
                # Try .keras extension
                model_path = FINBERT_PATH / 'models' / 'trained' / f'{symbol}_lstm.keras'
                if not model_path.exists():
                    logger.debug(f"No trained LSTM model found for {symbol}")
                    return {
                        'direction': 0.0,
                        'confidence': 0.0,
                        'predicted_price': None,
                        'model_trained': False,
                        'data_sufficient': True,
                        'prediction_date': datetime.now().isoformat()
                    }
            
            # Call FinBERT LSTM predictor
            logger.debug(f"Calling LSTM predictor for {symbol}")
            prediction_result = self.lstm_predictor.predict(symbol, historical_data)
            
            if prediction_result is None:
                logger.debug(f"LSTM prediction returned None for {symbol}")
                return None
            
            # Extract and validate prediction components
            predicted_price = prediction_result.get('predicted_price')
            confidence = prediction_result.get('confidence', 0.5)
            
            # Calculate direction from predicted price
            current_price = historical_data['Close'].iloc[-1]
            if predicted_price is not None and current_price > 0:
                price_change = (predicted_price - current_price) / current_price
                direction = np.clip(price_change * 2, -1, 1)  # Scale to [-1, 1]
            else:
                direction = 0.0
            
            # Build screener-compatible result
            result = {
                'direction': float(direction),
                'confidence': float(confidence),
                'predicted_price': float(predicted_price) if predicted_price is not None else None,
                'model_trained': True,
                'data_sufficient': True,
                'prediction_date': datetime.now().isoformat()
            }
            
            logger.info(f"✓ LSTM prediction for {symbol}: direction={direction:.3f}, confidence={confidence:.3f}")
            return result
            
        except Exception as e:
            logger.error(f"LSTM prediction failed for {symbol}: {e}")
            return None
    
    def get_sentiment_analysis(self, symbol: str, use_cache: bool = True) -> Optional[Dict]:
        """
        Get REAL sentiment analysis using FinBERT transformer and news scraping
        
        **Data Flow**:
        1. Bridge calls FinBERT news scraper
        2. Scraper fetches REAL news from Yahoo Finance/Finviz
        3. FinBERT transformer analyzes each article
        4. Results aggregated and cached
        5. Bridge translates to screener format
        
        **NO Synthetic Data**:
        - News is scraped from real sources
        - FinBERT transformer performs real NLP
        - NO keyword matching or fake scores
        - Returns None if no news available
        
        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL', 'MSFT')
            use_cache: Whether to use cached results (default: True)
        
        Returns:
            Dict with sentiment analysis:
            {
                'sentiment': str,          # 'positive', 'neutral', 'negative'
                'confidence': float,       # 0.0 to 100.0 percentage
                'direction': float,        # -1.0 to 1.0 (bearish to bullish)
                'article_count': int,      # Number of articles analyzed
                'sources': List[str],      # News sources used
                'analysis_date': str,      # ISO format datetime
                'cached': bool             # Whether result was cached
            }
            
            Returns None if:
            - Sentiment component not available
            - No news articles found
            - Analysis fails
        """
        if not NEWS_SENTIMENT_AVAILABLE or get_sentiment_sync is None:
            logger.debug(f"News sentiment not available for {symbol}")
            return None
        
        try:
            # Call FinBERT news sentiment analyzer
            logger.debug(f"Calling news sentiment analyzer for {symbol}")
            sentiment_result = get_sentiment_sync(symbol, use_cache=use_cache)
            
            if sentiment_result is None:
                logger.debug(f"News sentiment returned None for {symbol}")
                return None
            
            # Extract sentiment components
            sentiment = sentiment_result.get('sentiment', 'neutral')
            confidence = sentiment_result.get('confidence', 0.0)
            article_count = sentiment_result.get('article_count', 0)
            
            # Convert sentiment to direction (-1 to 1)
            sentiment_map = {
                'positive': 1.0,
                'neutral': 0.0,
                'negative': -1.0
            }
            direction = sentiment_map.get(sentiment.lower(), 0.0)
            
            # Adjust direction by confidence
            direction = direction * (confidence / 100.0)
            
            # Build screener-compatible result
            result = {
                'sentiment': sentiment,
                'confidence': float(confidence),
                'direction': float(direction),
                'article_count': int(article_count),
                'sources': sentiment_result.get('sources', ['Yahoo Finance', 'Finviz']),
                'analysis_date': datetime.now().isoformat(),
                'cached': sentiment_result.get('cached', False)
            }
            
            logger.info(f"✓ Sentiment for {symbol}: {sentiment} ({confidence:.1f}%), {article_count} articles")
            return result
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed for {symbol}: {e}")
            return None
    
    def analyze_text_with_finbert(self, text: str) -> Optional[Dict]:
        """
        Analyze arbitrary text using FinBERT transformer
        
        **Use Case**: Analyze custom text (news, earnings reports, etc.)
        
        Args:
            text: Financial text to analyze
        
        Returns:
            Dict with sentiment scores:
            {
                'sentiment': str,       # 'positive', 'neutral', 'negative'
                'confidence': float,    # 0.0 to 100.0
                'scores': {             # Raw probabilities
                    'positive': float,
                    'neutral': float,
                    'negative': float
                }
            }
            
            Returns None if sentiment analyzer not available
        """
        if not self._sentiment_initialized or self.sentiment_analyzer is None:
            logger.debug("FinBERT sentiment analyzer not available for text analysis")
            return None
        
        try:
            # Analyze text with FinBERT
            result = self.sentiment_analyzer.analyze_text(text)
            
            if result is None:
                return None
            
            logger.debug(f"✓ Text analyzed: {result.get('sentiment', 'unknown')} ({result.get('confidence', 0):.1f}%)")
            return result
            
        except Exception as e:
            logger.error(f"Text analysis failed: {e}")
            return None
    
    def get_trained_models_count(self) -> int:
        """
        Get count of trained LSTM models available
        
        Returns:
            int: Number of trained .h5 model files found
        """
        if not self._lstm_initialized or self.lstm_predictor is None:
            return 0
        
        try:
            models_dir = FINBERT_PATH / 'models' / 'lstm_models'
            if not models_dir.exists():
                return 0
            
            # Count .h5 files
            model_files = list(models_dir.glob('*_lstm_model.h5'))
            count = len(model_files)
            logger.debug(f"Found {count} trained LSTM models")
            return count
            
        except Exception as e:
            logger.error(f"Failed to count trained models: {e}")
            return 0
    
    def get_component_info(self) -> Dict:
        """
        Get detailed information about FinBERT components
        
        Returns:
            Dict with component information:
            {
                'finbert_path': str,
                'lstm': {
                    'available': bool,
                    'sequence_length': int,
                    'model_path': str
                },
                'sentiment': {
                    'available': bool,
                    'model_name': str,
                    'is_loaded': bool
                },
                'news': {
                    'available': bool,
                    'sources': List[str]
                }
            }
        """
        info = {
            'finbert_path': str(FINBERT_PATH),
            'lstm': {
                'available': self._lstm_initialized,
                'sequence_length': 60 if self.lstm_predictor else None,
                'model_path': str(FINBERT_PATH / 'models' / 'trained') if self._lstm_initialized else None
            },
            'sentiment': {
                'available': self._sentiment_initialized,
                'model_name': 'ProsusAI/finbert' if self.sentiment_analyzer else None,
                'is_loaded': self.sentiment_analyzer.is_loaded if self.sentiment_analyzer else False
            },
            'news': {
                'available': NEWS_SENTIMENT_AVAILABLE,
                'sources': ['Yahoo Finance', 'Finviz'] if NEWS_SENTIMENT_AVAILABLE else []
            }
        }
        
        return info


# Global singleton instance
_bridge_instance = None

def get_finbert_bridge() -> FinBERTBridge:
    """
    Get global FinBERT bridge instance (singleton pattern)
    
    Returns:
        FinBERTBridge: Shared bridge instance
    """
    global _bridge_instance
    if _bridge_instance is None:
        _bridge_instance = FinBERTBridge()
    return _bridge_instance


def test_bridge():
    """
    Test FinBERT bridge functionality
    
    This function can be run to verify the bridge is working correctly
    """
    print("\n" + "="*60)
    print("FinBERT Bridge Test")
    print("="*60)
    
    bridge = get_finbert_bridge()
    
    # Check availability
    availability = bridge.is_available()
    print("\nComponent Availability:")
    print(f"  LSTM:      {'✓' if availability['lstm_available'] else '✗'}")
    print(f"  Sentiment: {'✓' if availability['sentiment_available'] else '✗'}")
    print(f"  News:      {'✓' if availability['news_available'] else '✗'}")
    
    # Get component info
    info = bridge.get_component_info()
    print("\nComponent Information:")
    print(f"  FinBERT Path: {info['finbert_path']}")
    print(f"  LSTM Model Path: {info['lstm']['model_path']}")
    print(f"  Sentiment Model: {info['sentiment']['model_name']}")
    print(f"  News Sources: {', '.join(info['news']['sources'])}")
    
    print("\n" + "="*60)
    print("Bridge test complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    # Run test when executed directly
    test_bridge()
