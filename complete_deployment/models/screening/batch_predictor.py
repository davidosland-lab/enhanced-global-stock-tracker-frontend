"""
Batch Predictor Module

Mass prediction engine for overnight stock screening.
Uses ensemble prediction system to analyze multiple stocks efficiently.

Features:
- Parallel batch prediction processing
- Integration with LSTM models (when available)
- Ensemble prediction (LSTM 45%, Trend 25%, Technical 15%, Sentiment 15%)
- Caching and performance optimization
- Progress tracking and error handling
"""

import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import numpy as np
import pandas as pd
import yfinance as yf
import threading
import hashlib
import time

# Fix 1: Relative import fallback for script/package mode
try:
    from .alpha_vantage_fetcher import AlphaVantageDataFetcher
except ImportError:
    from alpha_vantage_fetcher import AlphaVantageDataFetcher

# Fix 2: Thread-safe Alpha Vantage rate limiting
_av_gate = threading.Semaphore(value=1)  # 1 concurrent call
_AV_DELAY_S = 12  # ~5 req/min safety

# Import FinBERT Bridge for real LSTM and sentiment
try:
    from .finbert_bridge import get_finbert_bridge
    FINBERT_BRIDGE_AVAILABLE = True
except ImportError:
    try:
        from models.screening.finbert_bridge import get_finbert_bridge
        FINBERT_BRIDGE_AVAILABLE = True
    except ImportError:
        FINBERT_BRIDGE_AVAILABLE = False
        get_finbert_bridge = None

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BatchPredictor:
    """
    Batch prediction engine for mass stock analysis.
    Integrates with existing ensemble prediction system.
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize Batch Predictor
        
        Args:
            config_path: Path to screening_config.json
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "screening_config.json"
        
        self.config = self._load_config(config_path)
        
        # Fix 4: Safe config access with defaults
        self.screening_config = self.config.get('screening', {})
        self.ensemble_weights = self.screening_config.get(
            'ensemble_weights',
            {'lstm': 0.45, 'trend': 0.25, 'technical': 0.15, 'sentiment': 0.15}
        )
        
        # Performance settings with safe access
        perf = self.config.get('performance', {})
        raw_workers = int(perf.get('max_workers', 2))
        # Fix 9: Cap max_workers for API rate limiting
        self.max_workers = max(1, min(raw_workers, 3))
        self.batch_size = int(perf.get('batch_size', 16))
        
        # Fix 3: Thread-safe prediction cache
        self.prediction_cache = {}
        self._cache_lock = threading.Lock()
        
        # Initialize Alpha Vantage fetcher for data retrieval
        self.data_fetcher = AlphaVantageDataFetcher(cache_ttl_minutes=240)
        
        # Initialize FinBERT Bridge for real LSTM and sentiment
        self.finbert_bridge = None
        self.finbert_components = {'lstm_available': False, 'sentiment_available': False, 'news_available': False}
        if FINBERT_BRIDGE_AVAILABLE:
            try:
                self.finbert_bridge = get_finbert_bridge()
                self.finbert_components = self.finbert_bridge.is_available()
                logger.info("✓ FinBERT Bridge initialized successfully")
            except Exception as e:
                logger.warning(f"FinBERT Bridge initialization failed: {e}")
        
        # Legacy LSTM check (kept for backward compatibility)
        self.lstm_available = self._check_lstm_availability() or self.finbert_components['lstm_available']
        
        logger.info(f"Batch Predictor initialized")
        logger.info(f"  FinBERT LSTM Available: {self.finbert_components['lstm_available']}")
        logger.info(f"  FinBERT Sentiment Available: {self.finbert_components['sentiment_available']}")
        logger.info(f"  FinBERT News Available: {self.finbert_components['news_available']}")
        logger.info(f"  Legacy LSTM Available: {self._check_lstm_availability()}")
        logger.info(f"  Ensemble Weights: {self.ensemble_weights}")
        logger.info(f"  Max Workers: {self.max_workers}")
    
    def _load_config(self, config_path: str) -> Dict:
        """Load screening configuration"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise
    
    def _cache_key(self, symbol: str, spi_sentiment: Dict) -> str:
        """
        Fix 3: Generate thread-safe cache key that includes SPI sentiment.
        Cache invalidates when SPI data changes.
        
        Args:
            symbol: Stock ticker
            spi_sentiment: Market sentiment data
            
        Returns:
            Cache key string
        """
        spi_sig = hashlib.md5(
            json.dumps(spi_sentiment or {}, sort_keys=True).encode()
        ).hexdigest()[:8]
        return f"{symbol}_{datetime.now().date()}_{spi_sig}"
    
    def _fetch_daily_safe(self, symbol: str, size: str = "compact") -> pd.DataFrame:
        """
        Fix 2: Thread-safe Alpha Vantage fetch with rate limiting.
        Fix 5: Normalize OHLCV column names.
        
        Args:
            symbol: Stock ticker
            size: 'compact' or 'full'
            
        Returns:
            Normalized DataFrame with OHLCV data
        """
        with _av_gate:
            df = self.data_fetcher.fetch_daily_data(symbol, outputsize=size)
            time.sleep(_AV_DELAY_S)  # Rate limiting
            return self._normalize_ohlcv(df)
    
    def _normalize_ohlcv(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Fix 5: Normalize column names to standard capitalization.
        Handles both lowercase and capitalized column names.
        
        Args:
            df: Raw DataFrame
            
        Returns:
            DataFrame with normalized columns
        """
        if df is None or df.empty:
            return pd.DataFrame()
        
        lower = {c.lower(): c for c in df.columns}
        mapping = {
            lower[k]: k.capitalize()
            for k in ('open', 'high', 'low', 'close', 'volume')
            if k in lower
        }
        return df.rename(columns=mapping)
    
    def _check_lstm_availability(self) -> bool:
        """Check if LSTM models are available"""
        try:
            # Check for LSTM model files
            lstm_dir = Path(__file__).parent.parent.parent / 'lstm_models'
            if lstm_dir.exists():
                models = list(lstm_dir.glob('*.h5')) + list(lstm_dir.glob('*.keras'))
                if models:
                    logger.info(f"Found {len(models)} LSTM models")
                    return True
            return False
        except Exception as e:
            logger.warning(f"LSTM check failed: {e}")
            return False
    
    def predict_batch(
        self,
        stocks: List[Dict],
        spi_sentiment: Dict = None
    ) -> List[Dict]:
        """
        Generate predictions for a batch of stocks
        
        Args:
            stocks: List of stock dictionaries from StockScanner
            spi_sentiment: Optional SPI market sentiment data
            
        Returns:
            List of stocks with prediction data added
        """
        logger.info(f"Starting batch prediction for {len(stocks)} stocks...")
        
        results = []
        
        # Process in parallel batches
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit prediction tasks
            future_to_stock = {
                executor.submit(
                    self._predict_single_stock,
                    stock,
                    spi_sentiment
                ): stock for stock in stocks
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_stock):
                stock = future_to_stock[future]
                try:
                    prediction_data = future.result()
                    
                    # Merge prediction with stock data
                    stock_with_prediction = {**stock, **prediction_data}
                    results.append(stock_with_prediction)
                    
                except Exception as e:
                    logger.error(f"Prediction failed for {stock['symbol']}: {e}")
                    # Add stock without prediction
                    stock['prediction_error'] = str(e)
                    results.append(stock)
        
        logger.info(f"Batch prediction complete: {len(results)} results")
        return results
    
    def _predict_single_stock(
        self,
        stock: Dict,
        spi_sentiment: Dict = None
    ) -> Dict:
        """
        Generate prediction for a single stock using ensemble
        
        Args:
            stock: Stock dictionary with technical data
            spi_sentiment: Market sentiment data
            
        Returns:
            Dictionary with prediction results
        """
        symbol = stock['symbol']
        
        # Fix 3: Thread-safe cache check with SPI-aware key
        cache_key = self._cache_key(symbol, spi_sentiment)
        with self._cache_lock:
            if cache_key in self.prediction_cache:
                return self.prediction_cache[cache_key]
        
        # Use cached Alpha Vantage data for predictions
        try:
            # Fix 2: Use thread-safe rate-limited fetch
            # Fix 5: Get normalized OHLCV data
            hist = self._fetch_daily_safe(symbol, size="compact")  # Use compact for speed
            
            if hist is None or hist.empty or len(hist) < 50:
                return {
                    'prediction': None,
                    'confidence': 0,
                    'error': 'Insufficient data'
                }
            
            # Calculate ensemble prediction
            prediction_data = self._calculate_ensemble_prediction(
                symbol=symbol,
                hist=hist,
                stock_data=stock,
                spi_sentiment=spi_sentiment
            )
            
            # Fix 3: Thread-safe cache write
            with self._cache_lock:
                self.prediction_cache[cache_key] = prediction_data
            
            return prediction_data
            
        except Exception as e:
            logger.error(f"Prediction error for {symbol}: {e}")
            return {
                'prediction': None,
                'confidence': 0,
                'error': str(e)
            }
    
    def _calculate_ensemble_prediction(
        self,
        symbol: str,
        hist: pd.DataFrame,
        stock_data: Dict,
        spi_sentiment: Dict = None
    ) -> Dict:
        """
        Calculate ensemble prediction from multiple models
        
        Ensemble components:
        - LSTM (45%): Neural network prediction (if available)
        - Trend (25%): Moving average and momentum
        - Technical (15%): RSI, MACD, volatility
        - Sentiment (15%): Market sentiment and SPI alignment
        
        Args:
            symbol: Stock ticker
            hist: Historical price data
            stock_data: Stock information and technical indicators
            spi_sentiment: Market sentiment data
            
        Returns:
            Dictionary with prediction results
        """
        # Component predictions
        predictions = {}
        confidences = {}
        
        # 1. LSTM Prediction (45%)
        # Fix 11: Graceful component absence - set both direction AND confidence to 0
        if self.lstm_available:
            try:
                lstm_pred = self._lstm_prediction(symbol, hist)
                predictions['lstm'] = lstm_pred.get('direction', 0.0)
                confidences['lstm'] = lstm_pred.get('confidence', 0.0)
            except Exception as e:
                logger.debug(f"LSTM prediction failed for {symbol}: {e}")
                predictions['lstm'] = 0.0
                confidences['lstm'] = 0.0
        else:
            # Component not available - set both to 0 for stable weighting
            predictions['lstm'] = 0.0
            confidences['lstm'] = 0.0
        
        # 2. Trend Analysis (25%)
        trend_pred = self._trend_prediction(hist, stock_data)
        predictions['trend'] = trend_pred['direction']
        confidences['trend'] = trend_pred['confidence']
        
        # 3. Technical Analysis (15%)
        technical_pred = self._technical_prediction(hist, stock_data)
        predictions['technical'] = technical_pred['direction']
        confidences['technical'] = technical_pred['confidence']
        
        # 4. Sentiment Analysis (15%)
        sentiment_pred = self._sentiment_prediction(stock_data, spi_sentiment)
        predictions['sentiment'] = sentiment_pred['direction']
        confidences['sentiment'] = sentiment_pred['confidence']
        
        # Fix 6: Calculate weighted ensemble with consistent normalization
        # Direction weighted by confidence, normalized by sum of (weight * confidence)
        num = 0.0
        den = 0.0
        
        for model, weight in self.ensemble_weights.items():
            if model in predictions:
                direction = predictions.get(model, 0.0)
                confidence = confidences.get(model, 0.0)  # 0..1 scale
                num += direction * weight * confidence
                den += weight * confidence
        
        # Calculate final values
        ensemble_direction = (num / den) if den > 0 else 0.0
        
        # Confidence as weighted average of confidences
        ensemble_confidence = 0.0
        total_weight = sum(self.ensemble_weights.values())
        if total_weight > 0:
            for model in self.ensemble_weights:
                weight = self.ensemble_weights[model]
                conf = confidences.get(model, 0.0)
                ensemble_confidence += conf * weight
            ensemble_confidence /= total_weight
        
        # Determine prediction label
        if ensemble_direction > 0.3:
            prediction_label = 'BUY'
        elif ensemble_direction < -0.3:
            prediction_label = 'SELL'
        else:
            prediction_label = 'HOLD'
        
        return {
            'prediction': prediction_label,
            'confidence': float(ensemble_confidence * 100),  # Convert to percentage
            'expected_return': float(ensemble_direction * 10),  # Scale to expected %
            'components': {
                'lstm': {
                    'direction': float(predictions.get('lstm', 0)),
                    'confidence': float(confidences.get('lstm', 0))
                },
                'trend': {
                    'direction': float(predictions['trend']),
                    'confidence': float(confidences['trend'])
                },
                'technical': {
                    'direction': float(predictions['technical']),
                    'confidence': float(confidences['technical'])
                },
                'sentiment': {
                    'direction': float(predictions['sentiment']),
                    'confidence': float(confidences['sentiment'])
                }
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def _lstm_prediction(self, symbol: str, hist: pd.DataFrame) -> Dict:
        """
        LSTM model prediction - NOW USES REAL FINBERT LSTM NEURAL NETWORK
        
        **Integration**: Uses FinBERT Bridge to access real trained LSTM models
        **NO Placeholder**: Real TensorFlow/Keras predictions with trained weights
        **Fallback**: Uses trend-based prediction only if FinBERT unavailable
        """
        # Try FinBERT Bridge first (REAL LSTM)
        if self.finbert_bridge and self.finbert_components['lstm_available']:
            try:
                lstm_result = self.finbert_bridge.get_lstm_prediction(symbol, hist)
                if lstm_result is not None and lstm_result.get('model_trained', False):
                    logger.debug(f"✓ Using REAL FinBERT LSTM for {symbol}: direction={lstm_result['direction']:.3f}")
                    return {
                        'direction': lstm_result['direction'],
                        'confidence': lstm_result['confidence']
                    }
                else:
                    logger.debug(f"No trained LSTM model for {symbol}, using fallback")
            except Exception as e:
                logger.warning(f"FinBERT LSTM failed for {symbol}: {e}, using fallback")
        
        # Fallback: Trend-based prediction (only if FinBERT unavailable)
        logger.debug(f"Using fallback trend prediction for {symbol}")
        if len(hist) < 5:
            return {'direction': 0.0, 'confidence': 0.3}
        
        recent_change = (hist['Close'].iloc[-1] - hist['Close'].iloc[-5]) / hist['Close'].iloc[-5]
        return {
            'direction': np.clip(recent_change * 2, -1, 1),
            'confidence': 0.4  # Lower confidence for fallback method
        }
    
    def _trend_prediction(self, hist: pd.DataFrame, stock_data: Dict) -> Dict:
        """
        Trend-based prediction using moving averages
        
        Signals:
        - Price above MA20 and MA50 = Bullish
        - MA20 above MA50 (golden cross) = Bullish
        - Rising MA20 = Bullish momentum
        """
        technical = stock_data['technical']
        price = stock_data['price']
        ma_20 = technical['ma_20']
        ma_50 = technical['ma_50']
        
        # Calculate trend signals
        signals = []
        
        # Price vs MAs
        if price > ma_20:
            signals.append(1)
        else:
            signals.append(-1)
        
        if price > ma_50:
            signals.append(1)
        else:
            signals.append(-1)
        
        # MA crossover
        if ma_20 > ma_50:
            signals.append(1)
        else:
            signals.append(-1)
        
        # Fix 7: MA slope (momentum) - use actual MA20 5 days ago
        if len(hist) >= 25:
            ma20_series = hist['Close'].rolling(20).mean()
            # Compare current MA20 vs MA20 5 days ago
            if not ma20_series.empty and len(ma20_series) >= 6:
                ma_20_5d_ago = ma20_series.iloc[-6]
                if ma_20 > ma_20_5d_ago:
                    signals.append(1)
                else:
                    signals.append(-1)
        
        # Average signal
        direction = np.mean(signals)
        confidence = abs(direction)  # Stronger if unanimous
        
        return {
            'direction': direction,
            'confidence': min(confidence, 1.0)
        }
    
    def _technical_prediction(self, hist: pd.DataFrame, stock_data: Dict) -> Dict:
        """
        Technical indicator prediction (RSI, volatility)
        
        Signals:
        - RSI < 30 = Oversold (Buy)
        - RSI > 70 = Overbought (Sell)
        - Low volatility = Stable (positive)
        """
        technical = stock_data['technical']
        rsi = technical['rsi']
        volatility = technical['volatility']
        
        # RSI signal
        if rsi < 30:
            rsi_signal = 1.0  # Strong buy
        elif rsi < 40:
            rsi_signal = 0.5  # Moderate buy
        elif rsi > 70:
            rsi_signal = -1.0  # Strong sell
        elif rsi > 60:
            rsi_signal = -0.5  # Moderate sell
        else:
            rsi_signal = 0  # Neutral
        
        # Fix 8: Volatility signal - ensure sufficient data (30+ days)
        if len(hist) >= 30:
            # Volatility signal (prefer low volatility)
            if volatility < 0.02:
                vol_signal = 0.5
            elif volatility < 0.04:
                vol_signal = 0.2
            else:
                vol_signal = -0.2
        else:
            vol_signal = 0.0  # Not enough data for reliable volatility
        
        direction = (rsi_signal * 0.7 + vol_signal * 0.3)
        confidence = 0.7  # Moderate confidence in technicals
        
        return {
            'direction': direction,
            'confidence': confidence
        }
    
    def _sentiment_prediction(
        self,
        stock_data: Dict,
        spi_sentiment: Dict = None
    ) -> Dict:
        """
        Sentiment-based prediction - NOW USES REAL FINBERT SENTIMENT ANALYSIS
        
        **Integration**: Uses FinBERT Bridge to access real news + transformer sentiment
        **NO Mock Data**: Real news scraping from Yahoo Finance and Finviz
        **Real NLP**: FinBERT transformer analyzes actual financial text
        **Fallback**: Uses SPI gap prediction only if FinBERT unavailable
        
        Factors:
        - Real news sentiment from FinBERT (PRIORITY)
        - SPI gap prediction alignment (fallback)
        - Overall market sentiment
        """
        # Try FinBERT Bridge first (REAL SENTIMENT)
        symbol = stock_data.get('symbol', '')
        if self.finbert_bridge and self.finbert_components['sentiment_available'] and symbol:
            try:
                sentiment_result = self.finbert_bridge.get_sentiment_analysis(symbol, use_cache=True)
                if sentiment_result is not None and sentiment_result.get('article_count', 0) > 0:
                    logger.debug(f"✓ Using REAL FinBERT sentiment for {symbol}: {sentiment_result['sentiment']} ({sentiment_result['confidence']:.1f}%), {sentiment_result['article_count']} articles")
                    return {
                        'direction': sentiment_result['direction'],
                        'confidence': sentiment_result['confidence'] / 100.0  # Convert to 0-1 scale
                    }
                else:
                    logger.debug(f"No news articles for {symbol}, using SPI fallback")
            except Exception as e:
                logger.warning(f"FinBERT sentiment failed for {symbol}: {e}, using fallback")
        
        # Fix 8: Fallback - SPI gap prediction (only if FinBERT unavailable or no news)
        logger.debug(f"Using fallback SPI sentiment for {symbol}")
        direction = 0
        confidence = 0.5
        
        # Guard when spi_sentiment is missing
        if spi_sentiment and isinstance(spi_sentiment, dict):
            # Use SPI gap prediction
            gap_prediction = spi_sentiment.get('gap_prediction', {})
            predicted_gap = gap_prediction.get('predicted_gap_pct', 0)
            spi_confidence = gap_prediction.get('confidence', 50) / 100
            
            # Scale gap to direction (-1 to 1)
            direction = np.clip(predicted_gap / 2.0, -1, 1)
            confidence = spi_confidence * 0.8  # Lower confidence for fallback
        
        return {
            'direction': direction,
            'confidence': confidence
        }
    
    def get_prediction_summary(self, predictions: List[Dict]) -> Dict:
        """
        Generate summary statistics for batch predictions
        
        Args:
            predictions: List of stocks with prediction data
            
        Returns:
            Dictionary with summary statistics
        """
        if not predictions:
            return {'total': 0}
        
        buy_signals = [p for p in predictions if p.get('prediction') == 'BUY']
        sell_signals = [p for p in predictions if p.get('prediction') == 'SELL']
        hold_signals = [p for p in predictions if p.get('prediction') == 'HOLD']
        
        confidences = [p.get('confidence', 0) for p in predictions if p.get('confidence')]
        
        return {
            'total': len(predictions),
            'buy_count': len(buy_signals),
            'sell_count': len(sell_signals),
            'hold_count': len(hold_signals),
            'avg_confidence': np.mean(confidences) if confidences else 0,
            'high_confidence_count': len([c for c in confidences if c >= 70]),
            'top_buy_opportunities': sorted(
                buy_signals,
                key=lambda x: x.get('confidence', 0),
                reverse=True
            )[:10]
        }


# ============================================================================
# TEST HARNESS
# ============================================================================

def test_batch_predictor():
    """Test the batch predictor"""
    print("\n" + "="*80)
    print("BATCH PREDICTOR TEST")
    print("="*80 + "\n")
    
    # Initialize predictor
    predictor = BatchPredictor()
    
    # Create sample stocks
    sample_stocks = [
        {
            'symbol': 'CBA.AX',
            'name': 'Commonwealth Bank',
            'price': 105.50,
            'market_cap': 180000000000,
            'volume': 5000000,
            'beta': 1.1,
            'technical': {
                'ma_20': 104.0,
                'ma_50': 102.5,
                'rsi': 55.0,
                'volatility': 0.025
            },
            'score': 85.0
        },
        {
            'symbol': 'BHP.AX',
            'name': 'BHP Group',
            'price': 45.20,
            'market_cap': 230000000000,
            'volume': 8000000,
            'beta': 1.3,
            'technical': {
                'ma_20': 44.5,
                'ma_50': 43.0,
                'rsi': 62.0,
                'volatility': 0.03
            },
            'score': 82.0
        }
    ]
    
    # Sample SPI sentiment
    spi_sentiment = {
        'sentiment_score': 65,
        'gap_prediction': {
            'predicted_gap_pct': 0.5,
            'confidence': 75,
            'direction': 'bullish'
        }
    }
    
    print("Processing batch predictions...\n")
    
    # Run predictions
    results = predictor.predict_batch(sample_stocks, spi_sentiment)
    
    # Display results
    print("-"*80)
    print("PREDICTION RESULTS")
    print("-"*80)
    
    for stock in results:
        print(f"\n{stock['symbol']} - {stock['name']}")
        print(f"  Price: ${stock['price']:.2f}")
        print(f"  Prediction: {stock.get('prediction', 'N/A')}")
        print(f"  Confidence: {stock.get('confidence', 0):.1f}%")
        print(f"  Expected Return: {stock.get('expected_return', 0):+.2f}%")
        
        if 'components' in stock:
            print(f"  Components:")
            for comp_name, comp_data in stock['components'].items():
                print(f"    {comp_name:10s}: {comp_data['direction']:+.2f} (conf: {comp_data['confidence']:.2f})")
    
    # Summary
    summary = predictor.get_prediction_summary(results)
    print("\n" + "-"*80)
    print("SUMMARY")
    print("-"*80)
    print(f"Total Predictions: {summary['total']}")
    print(f"BUY Signals: {summary['buy_count']}")
    print(f"SELL Signals: {summary['sell_count']}")
    print(f"HOLD Signals: {summary['hold_count']}")
    print(f"Average Confidence: {summary['avg_confidence']:.1f}%")
    print(f"High Confidence (>=70%): {summary['high_confidence_count']}")


if __name__ == "__main__":
    test_batch_predictor()
