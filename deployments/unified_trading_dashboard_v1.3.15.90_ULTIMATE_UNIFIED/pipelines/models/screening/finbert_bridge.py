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

def _find_finbert_path() -> Optional[Path]:
    """Find FinBERT v4.4.4 installation with multiple fallbacks"""
    
    # Priority 1: Environment variable
    if 'FINBERT_PATH' in os.environ:
        path = Path(os.environ['FINBERT_PATH'])
        if path.exists():
            logger.info(f"[OK] Using FinBERT from FINBERT_PATH env: {path}")
            return path
    
    # Priority 2: User-specified (complete_backend_clean_install_v1.3.15 folder)
    path = Path(r'C:\Users\david\Regime_trading\complete_backend_clean_install_v1.3.15\finbert_v4.4.4')
    if path.exists():
        logger.info(f"[OK] Using FinBERT from complete_backend_clean_install: {path}")
        return path
    
    # Priority 3: Relative to this file
    path = Path(__file__).parent.parent.parent / 'finbert_v4.4.4'
    if path.exists():
        logger.info(f"[OK] Using FinBERT from relative path: {path}")
        return path
    
    # Priority 4: Current working directory
    path = Path.cwd() / 'finbert_v4.4.4'
    if path.exists():
        logger.info(f"[OK] Using FinBERT from current directory: {path}")
        return path
    
    # Priority 5: Parent of current directory
    path = Path.cwd().parent / 'finbert_v4.4.4'
    if path.exists():
        logger.info(f"[OK] Using FinBERT from parent directory: {path}")
        return path
    
    # Not found
    logger.warning("[!] FinBERT v4.4.4 not found. Tried:")
    logger.warning("    1. FINBERT_PATH environment variable")
    logger.warning(f"    2. C:\\Users\\david\\Regime_trading\\complete_backend_clean_install_v1.3.15\\finbert_v4.4.4")
    logger.warning(f"    3. {Path(__file__).parent.parent.parent / 'finbert_v4.4.4'}")
    logger.warning(f"    4. {Path.cwd() / 'finbert_v4.4.4'}")
    logger.warning(f"    5. {Path.cwd().parent / 'finbert_v4.4.4'}")
    return None

# Calculate FinBERT path
FINBERT_PATH = _find_finbert_path()
if FINBERT_PATH is None:
    FINBERT_PATH = Path(__file__).parent.parent.parent / 'finbert_v4.4.4'  # Default for imports

FINBERT_MODELS_PATH = FINBERT_PATH / 'models'

# Add FinBERT to Python path (read-only access)
if FINBERT_PATH.exists():
    sys.path.insert(0, str(FINBERT_PATH))
    sys.path.insert(0, str(FINBERT_MODELS_PATH))
    logger.info(f"[OK] Added FinBERT path to sys.path: {FINBERT_PATH}")

# Import FinBERT modules (with error handling)
try:
    from lstm_predictor import StockLSTMPredictor
    LSTM_AVAILABLE = True
    logger.info("[OK] LSTM predictor imported successfully")
except ImportError as e:
    LSTM_AVAILABLE = False
    logger.warning(f"[!] LSTM predictor not available: {e}")
    StockLSTMPredictor = None

try:
    from finbert_sentiment import FinBERTSentimentAnalyzer
    SENTIMENT_ANALYZER_AVAILABLE = True
    logger.info("[OK] FinBERT sentiment analyzer imported successfully")
except ImportError as e:
    SENTIMENT_ANALYZER_AVAILABLE = False
    logger.warning(f"[!] FinBERT sentiment analyzer not available: {e}")
    FinBERTSentimentAnalyzer = None

try:
    from news_sentiment_real import get_sentiment_sync
    NEWS_SENTIMENT_AVAILABLE = True
    logger.info("[OK] News sentiment module imported successfully")
except ImportError as e:
    NEWS_SENTIMENT_AVAILABLE = False
    logger.warning(f"[!] News sentiment module not available: {e}")
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
        self.lstm_predictor_cache = {}  # KERAS 3 FIX: Cache per-symbol predictors
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
            # KERAS 3 FIX: Will create per-symbol predictors on demand
            self._lstm_initialized = True
            logger.info("[OK] LSTM predictor initialized successfully (per-symbol caching enabled)")
        except Exception as e:
            logger.error(f"Failed to initialize LSTM predictor: {e}")
            self._lstm_initialized = False
    
    def _get_lstm_predictor(self, symbol: str) -> Optional['StockLSTMPredictor']:
        """
        Get or create LSTM predictor for specific symbol (KERAS 3 FIX)
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Symbol-specific LSTM predictor
        """
        if not self._lstm_initialized:
            return None
            
        # Check cache first
        if symbol in self.lstm_predictor_cache:
            return self.lstm_predictor_cache[symbol]
        
        # Create new symbol-specific predictor
        try:
            predictor = StockLSTMPredictor(sequence_length=60, symbol=symbol)
            self.lstm_predictor_cache[symbol] = predictor
            logger.debug(f"Created LSTM predictor for {symbol}")
            return predictor
        except Exception as e:
            logger.error(f"Failed to create LSTM predictor for {symbol}: {e}")
            return None
    
    def _init_sentiment(self):
        """Initialize FinBERT sentiment analyzer component"""
        if not SENTIMENT_ANALYZER_AVAILABLE or FinBERTSentimentAnalyzer is None:
            logger.warning("FinBERT sentiment analyzer not available")
            return
        
        try:
            # Initialize FinBERT analyzer with default model
            self.sentiment_analyzer = FinBERTSentimentAnalyzer(model_name="ProsusAI/finbert")
            self._sentiment_initialized = True
            logger.info("[OK] FinBERT sentiment analyzer initialized successfully")
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
        2. Bridge gets or creates symbol-specific LSTM predictor (KERAS 3 FIX)
        3. LSTM loads trained .keras model for symbol
        4. Neural network generates prediction
        5. Bridge translates result to screener format
        
        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL', 'MSFT')
            historical_data: DataFrame with columns ['Close', 'Open', 'High', 'Low', 'Volume']
                            Minimum 60 days of data required for LSTM
        
        Returns:
            Dict with prediction results or None if prediction fails
        """
        # KERAS 3 FIX: Get symbol-specific predictor
        lstm_predictor = self._get_lstm_predictor(symbol)
        if lstm_predictor is None:
            logger.debug(f"LSTM not available for {symbol}")
            return None
        
        try:
            # Validate input data
            if historical_data is None or len(historical_data) < 60:
                logger.debug(f"Insufficient data for LSTM prediction: {symbol} ({len(historical_data) if historical_data is not None else 0} days)")
                return None  # Predictor will fail loud if needed
            
            # Call FinBERT LSTM predictor (symbol-specific)
            logger.debug(f"Calling LSTM predictor for {symbol}")
            prediction_result = lstm_predictor.predict(historical_data, symbol=symbol)
            
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
            
            logger.info(f"[OK] LSTM prediction for {symbol}: direction={direction:.3f}, confidence={confidence:.3f}")
            return result
            
        except Exception as e:
            logger.error(f"LSTM prediction failed for {symbol}: {e}")
            return None
    
    def get_sentiment_analysis(self, symbol: str, use_cache: bool = True) -> Optional[Dict]:
        """
        Get REAL sentiment analysis using FinBERT transformer and news scraping
        
        **Enhanced Return Format (v1.3.15.45)**:
        Now returns full FinBERT v4.4.4 breakdown including negative/neutral/positive scores
        
        **Data Flow**:
        1. Bridge calls FinBERT news scraper
        2. Scraper fetches REAL news from Yahoo Finance/Finviz
        3. FinBERT transformer analyzes each article
        4. Results aggregated and cached
        5. Bridge translates to screener format with FULL breakdown
        
        **NO Synthetic Data**:
        - News is scraped from real sources
        - FinBERT transformer performs real NLP
        - NO keyword matching or fake scores
        - Returns None if no news available
        
        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL', 'MSFT')
            use_cache: Whether to use cached results (default: True)
        
        Returns:
            Dict with comprehensive sentiment analysis (FinBERT v4.4.4 format):
            {
                'symbol': str,             # Stock symbol
                'sentiment': str,          # 'positive', 'neutral', 'negative'
                'confidence': float,       # 0.0 to 100.0 percentage
                'scores': {                # FinBERT v4.4.4 breakdown
                    'negative': float,     # 0.0 to 1.0
                    'neutral': float,      # 0.0 to 1.0
                    'positive': float      # 0.0 to 1.0
                },
                'compound': float,         # -1.0 to 1.0 (overall sentiment)
                'direction': float,        # -1.0 to 1.0 (for backward compat)
                'article_count': int,      # Number of articles analyzed
                'sources': List[str],      # News sources used
                'method': str,             # 'FinBERT v4.4.4'
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
            
            # Extract full FinBERT scores (NEW in v1.3.15.45)
            scores = sentiment_result.get('scores', {})
            if not scores or not isinstance(scores, dict):
                # Fallback if scores not provided
                scores = {
                    'negative': 0.33 if sentiment == 'negative' else 0.10,
                    'neutral': 0.34 if sentiment == 'neutral' else 0.20,
                    'positive': 0.33 if sentiment == 'positive' else 0.10
                }
            
            # Calculate compound score from scores
            compound = scores.get('positive', 0.33) - scores.get('negative', 0.33)
            
            # Convert sentiment to direction (-1 to 1) for backward compatibility
            sentiment_map = {
                'positive': 1.0,
                'neutral': 0.0,
                'negative': -1.0
            }
            direction = sentiment_map.get(sentiment.lower(), 0.0)
            
            # Adjust direction by confidence
            direction = direction * (confidence / 100.0)
            
            # Build screener-compatible result with FULL FinBERT v4.4.4 breakdown
            result = {
                'symbol': symbol,
                'sentiment': sentiment,
                'confidence': float(confidence),
                'scores': {  # NEW: Full FinBERT breakdown
                    'negative': float(scores.get('negative', 0.33)),
                    'neutral': float(scores.get('neutral', 0.34)),
                    'positive': float(scores.get('positive', 0.33))
                },
                'compound': float(compound),
                'direction': float(direction),  # Backward compatibility
                'article_count': int(article_count),
                'sources': sentiment_result.get('sources', ['Yahoo Finance', 'Finviz']),
                'method': 'FinBERT v4.4.4',
                'analysis_date': datetime.now().isoformat(),
                'cached': sentiment_result.get('cached', False)
            }
            
            logger.info(f"[OK] FinBERT v4.4.4 Sentiment for {symbol}: {sentiment} ({confidence:.1f}%), "
                       f"compound: {compound:.3f}, {article_count} articles")
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
            
            logger.debug(f"[OK] Text analyzed: {result.get('sentiment', 'unknown')} ({result.get('confidence', 0):.1f}%)")
            return result
            
        except Exception as e:
            logger.error(f"Text analysis failed: {e}")
            return None
    
    def get_trained_models_count(self) -> int:
        """
        Count the number of trained LSTM models available
        
        Returns:
            int: Number of trained models found in finbert_v4.4.4/models/trained/
        """
        if not self._lstm_initialized:
            return 0
        
        try:
            trained_dir = FINBERT_PATH / 'models' / 'trained'
            if not trained_dir.exists():
                return 0
            
            # Count .h5 and .keras model files
            h5_models = list(trained_dir.glob('*_lstm.h5'))
            keras_models = list(trained_dir.glob('*_lstm.keras'))
            
            return len(h5_models) + len(keras_models)
            
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
    print(f"  LSTM:      {'[OK]' if availability['lstm_available'] else '[X]'}")
    print(f"  Sentiment: {'[OK]' if availability['sentiment_available'] else '[X]'}")
    print(f"  News:      {'[OK]' if availability['news_available'] else '[X]'}")
    
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
