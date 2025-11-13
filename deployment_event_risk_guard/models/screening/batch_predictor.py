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
from yahooquery import Ticker

try:
    from .alpha_vantage_fetcher import AlphaVantageDataFetcher
except ImportError:
    from alpha_vantage_fetcher import AlphaVantageDataFetcher

# Import FinBERT Bridge for real LSTM and sentiment
try:
    from .finbert_bridge import get_finbert_bridge
    FINBERT_BRIDGE_AVAILABLE = True
except ImportError:
    try:
        from finbert_bridge import get_finbert_bridge
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
        self.screening_config = self.config['screening']
        self.ensemble_weights = self.screening_config['ensemble_weights']
        
        # Performance settings
        self.max_workers = self.config['performance']['max_workers']
        self.batch_size = self.config['performance']['batch_size']
        
        # Prediction cache
        self.prediction_cache = {}
        
        # Initialize Alpha Vantage fetcher as backup only (kept for legacy compatibility)
        # Primary data source is now yahooquery
        try:
            self.data_fetcher = AlphaVantageDataFetcher(cache_ttl_minutes=240)
        except:
            self.data_fetcher = None
        
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
        
        # Check cache
        cache_key = f"{symbol}_{datetime.now().date()}"
        if cache_key in self.prediction_cache:
            return self.prediction_cache[cache_key]
        
        # Fetch data using yahooquery (primary) or Alpha Vantage (backup)
        try:
            # Try yahooquery first (most reliable for ASX stocks)
            hist = None
            try:
                ticker = Ticker(symbol)
                hist = ticker.history(period="1y")  # 1 year of data for better analysis
                
                if isinstance(hist, pd.DataFrame) and not hist.empty:
                    # Normalize column names
                    hist.columns = [col.capitalize() for col in hist.columns]
                    logger.debug(f"✓ {symbol}: Data fetched from yahooquery ({len(hist)} days)")
            except Exception as yq_error:
                logger.debug(f"yahooquery failed for {symbol}: {yq_error}")
                hist = None
            
            # Fallback to Alpha Vantage if yahooquery fails
            if (hist is None or hist.empty) and self.data_fetcher:
                try:
                    hist = self.data_fetcher.fetch_daily_data(symbol, outputsize="full")
                    if hist is not None and not hist.empty:
                        logger.debug(f"✓ {symbol}: Data fetched from Alpha Vantage (backup)")
                except Exception as av_error:
                    logger.debug(f"Alpha Vantage failed for {symbol}: {av_error}")
                    hist = None
            
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
            
            # Cache result
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
        if self.lstm_available:
            lstm_pred = self._lstm_prediction(symbol, hist)
            predictions['lstm'] = lstm_pred['direction']
            confidences['lstm'] = lstm_pred['confidence']
        else:
            # Use trend as fallback
            predictions['lstm'] = 0
            confidences['lstm'] = 0
        
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
        
        # Calculate weighted ensemble prediction
        ensemble_direction = 0
        ensemble_confidence = 0
        total_weight = 0
        
        for model, weight in self.ensemble_weights.items():
            if model in predictions:
                ensemble_direction += predictions[model] * weight * confidences[model]
                ensemble_confidence += confidences[model] * weight
                total_weight += weight
        
        if total_weight > 0:
            ensemble_direction /= total_weight
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
        
        # MA slope (momentum)
        if len(hist) >= 25:
            ma_20_prev = hist['Close'].iloc[-25:-5].mean()
            if ma_20 > ma_20_prev:
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
        
        # Volatility signal (prefer low volatility)
        if volatility < 0.02:
            vol_signal = 0.5
        elif volatility < 0.04:
            vol_signal = 0.2
        else:
            vol_signal = -0.2
        
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
        
        # Fallback: SPI gap prediction (only if FinBERT unavailable or no news)
        logger.debug(f"Using fallback SPI sentiment for {symbol}")
        direction = 0
        confidence = 0.5
        
        if spi_sentiment:
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
