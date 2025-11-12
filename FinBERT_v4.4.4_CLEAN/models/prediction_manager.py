"""
Prediction Manager
Orchestrates prediction generation, caching, and validation
Supports multi-timezone markets (US, Australia, UK)
"""

import logging
from datetime import datetime, time, timedelta
from typing import Dict, Optional, List
import pytz
import yfinance as yf

# Import market timezone manager
try:
    from models.market_timezones import get_market_tz_manager
    MARKET_TZ_AVAILABLE = True
except ImportError:
    MARKET_TZ_AVAILABLE = False
    logger.warning("Market timezone manager not available, using default US timezone")

logger = logging.getLogger(__name__)


class PredictionManager:
    """Manages prediction lifecycle with caching and validation for multi-timezone markets"""
    
    def __init__(self, ml_predictor, prediction_db):
        """
        Initialize prediction manager
        
        Args:
            ml_predictor: ML predictor instance from app
            prediction_db: PredictionDatabase instance
        """
        self.ml_predictor = ml_predictor
        self.prediction_db = prediction_db
        self.eastern = pytz.timezone('US/Eastern')
        
        # Initialize market timezone manager
        if MARKET_TZ_AVAILABLE:
            self.market_tz = get_market_tz_manager()
            logger.info("PredictionManager initialized with multi-timezone support (US/AU/UK)")
        else:
            self.market_tz = None
            logger.info("PredictionManager initialized (default US timezone only)")
    
    def get_daily_eod_prediction(self, symbol: str, force_refresh: bool = False) -> Dict:
        """
        Get end-of-day prediction for symbol
        Uses cached prediction if available, generates new if needed
        
        IMPORTANT: Predictions are locked BEFORE market open to ensure consistency
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'BHP.AX', 'BP.L')
            force_refresh: Force regeneration even if cached exists
        
        Returns:
            Prediction dictionary with all details
        """
        # Detect market for this symbol
        if self.market_tz:
            market_code = self.market_tz.detect_market(symbol)
            market_info = self.market_tz.get_market_info(market_code)
            tz = market_info['tz']
            today = datetime.now(tz).strftime('%Y-%m-%d')
        else:
            today = datetime.now(self.eastern).strftime('%Y-%m-%d')
        
        # Check cache first
        if not force_refresh:
            cached = self.prediction_db.get_prediction(symbol, today, 'DAILY_EOD')
            if cached:
                if self.market_tz:
                    market_open = self.market_tz.get_market_open_time(symbol)
                    is_locked = datetime.now(tz) >= market_open
                    logger.info(f"✓ Using cached prediction for {symbol} "
                               f"({'LOCKED' if is_locked else 'pre-market'})")
                else:
                    logger.info(f"✓ Using cached prediction for {symbol}")
                
                cached['is_cached'] = True
                cached['is_locked'] = is_locked if self.market_tz else True
                return cached
        
        # Check if we can generate prediction (before market open)
        if self.market_tz and not force_refresh:
            can_generate, reason = self.market_tz.can_generate_prediction(symbol)
            
            if not can_generate and "Market is OPEN" in reason:
                logger.warning(f"⚠️  {symbol}: Cannot generate prediction - {reason}")
                logger.warning(f"   Predictions must be generated BEFORE market open")
                raise ValueError(f"Cannot generate prediction for {symbol} - {reason}. "
                               f"Predictions are locked once market opens.")
            
            if not can_generate:
                logger.warning(f"⚠️  {symbol}: {reason}")
        
        # Generate new prediction
        logger.info(f"⚙ Generating new daily prediction for {symbol}")
        try:
            prediction = self._generate_daily_prediction(symbol)
            
            # Store in database
            prediction_id = self.prediction_db.store_prediction(prediction)
            prediction['prediction_id'] = prediction_id
            prediction['is_cached'] = False
            prediction['is_locked'] = False  # Just generated, not locked yet
            
            if self.market_tz:
                market_open = self.market_tz.get_market_open_time(symbol)
                logger.info(f"✓ Generated prediction for {symbol} ({market_code}): "
                           f"{prediction['prediction']} @ ${prediction['predicted_price']:.2f}")
                logger.info(f"  Will be LOCKED at market open: {market_open.strftime('%Y-%m-%d %H:%M %Z')}")
            else:
                logger.info(f"✓ Generated and stored new prediction for {symbol}: "
                           f"{prediction['prediction']} @ ${prediction['predicted_price']:.2f}")
            
            return prediction
            
        except Exception as e:
            logger.error(f"✗ Error generating prediction for {symbol}: {e}")
            raise
    
    def _generate_daily_prediction(self, symbol: str) -> Dict:
        """
        Generate a new daily EOD prediction
        Uses 1-year of daily data for consistency
        
        Args:
            symbol: Stock symbol
        
        Returns:
            Prediction dictionary
        """
        # Fetch standardized data for prediction
        # Always use 1-year of daily data for consistency
        chart_data = self._fetch_chart_data(symbol, interval='1d', period='1y')
        
        if not chart_data or len(chart_data) == 0:
            raise ValueError(f"No chart data available for {symbol}")
        
        # Get current price
        current_price = chart_data[-1].get('close', chart_data[-1].get('Close', 0))
        
        if current_price == 0:
            raise ValueError(f"Invalid current price for {symbol}")
        
        # Get ML ensemble prediction
        ensemble_result = self.ml_predictor.get_ensemble_prediction(
            chart_data, 
            current_price, 
            symbol,
            include_sentiment=True
        )
        
        # Calculate target date (market close time for this symbol's exchange)
        if self.market_tz:
            # Use market-specific timezone and close time
            target_date = self.market_tz.get_market_close_time(symbol)
            now = datetime.now(target_date.tzinfo)
            
            # If market has already closed today, target is next trading day's close
            if now >= target_date:
                target_date = self.market_tz.get_market_close_time(
                    symbol, 
                    now + timedelta(days=1)
                )
        else:
            # Fallback to US Eastern time
            now = datetime.now(self.eastern)
            target_date = datetime.combine(now.date(), time(16, 0, 0))
            
            # If it's already past 4 PM, target is next trading day
            if now.hour >= 16:
                target_date = target_date + timedelta(days=1)
                # Skip weekends
                while target_date.weekday() >= 5:  # Saturday=5, Sunday=6
                    target_date = target_date + timedelta(days=1)
            
            target_date = self.eastern.localize(target_date)
        
        # Build prediction record
        prediction = {
            'symbol': symbol.upper(),
            'prediction_date': now.isoformat(),
            'target_date': target_date.isoformat(),
            'timeframe': 'DAILY_EOD',
            'current_price': current_price,
            'predicted_price': ensemble_result.get('predicted_price', current_price),
            'predicted_change_percent': (
                (ensemble_result.get('predicted_price', current_price) - current_price) 
                / current_price * 100
            ),
            'prediction': ensemble_result.get('prediction', 'HOLD'),
            'confidence': ensemble_result.get('confidence', 50.0),
            'chart_interval': '1d',
            'chart_period': '1y',
            'data_points_count': len(chart_data)
        }
        
        # Add model components if available
        if 'models_used' in ensemble_result:
            # Extract individual model predictions if available
            # This depends on how the ensemble result is structured
            prediction['lstm_prediction'] = 'BUY'  # Placeholder
            prediction['lstm_weight'] = 0.5
            prediction['trend_prediction'] = 'BUY'
            prediction['trend_weight'] = 0.3
            prediction['technical_prediction'] = 'HOLD'
            prediction['technical_weight'] = 0.2
        
        # Add sentiment if available
        if 'sentiment' in ensemble_result:
            sentiment = ensemble_result['sentiment']
            prediction['sentiment_label'] = sentiment.get('sentiment', 'NEUTRAL').upper()
            prediction['sentiment_score'] = sentiment.get('compound', 0)
            prediction['sentiment_confidence'] = sentiment.get('confidence', 0)
            prediction['article_count'] = sentiment.get('article_count', 0)
        
        return prediction
    
    def _fetch_chart_data(self, symbol: str, interval: str = '1d', 
                          period: str = '1y') -> List[Dict]:
        """
        Fetch chart data from Yahoo Finance
        
        Args:
            symbol: Stock symbol
            interval: Data interval (1d, 1h, etc.)
            period: Data period (1y, 6mo, etc.)
        
        Returns:
            List of candlestick dictionaries
        """
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period, interval=interval)
            
            if hist.empty:
                logger.warning(f"No historical data for {symbol}")
                return []
            
            # Convert to list of dictionaries
            chart_data = []
            for index, row in hist.iterrows():
                candle = {
                    'date': index.isoformat(),
                    'open': row['Open'],
                    'high': row['High'],
                    'low': row['Low'],
                    'close': row['Close'],
                    'Close': row['Close'],  # Compatibility
                    'volume': row['Volume']
                }
                chart_data.append(candle)
            
            logger.info(f"✓ Fetched {len(chart_data)} candles for {symbol} ({period}, {interval})")
            return chart_data
            
        except Exception as e:
            logger.error(f"Error fetching chart data for {symbol}: {e}")
            return []
    
    def get_closing_price(self, symbol: str, date) -> Optional[float]:
        """
        Get closing price for a specific date
        
        Args:
            symbol: Stock symbol
            date: Date object or string
        
        Returns:
            Closing price or None
        """
        try:
            if isinstance(date, str):
                date = datetime.fromisoformat(date).date()
            elif isinstance(date, datetime):
                date = date.date()
            
            # Fetch data for the specific date + 1 day buffer
            start_date = date - timedelta(days=1)
            end_date = date + timedelta(days=2)
            
            ticker = yf.Ticker(symbol)
            hist = ticker.history(start=start_date, end=end_date)
            
            if hist.empty:
                logger.warning(f"No closing price data for {symbol} on {date}")
                return None
            
            # Find the closest date
            for index, row in hist.iterrows():
                hist_date = index.date()
                if hist_date == date:
                    close_price = row['Close']
                    logger.info(f"✓ Got closing price for {symbol} on {date}: ${close_price:.2f}")
                    return close_price
            
            # If exact date not found, use closest
            if len(hist) > 0:
                close_price = hist.iloc[-1]['Close']
                logger.warning(f"Using approximate closing price for {symbol} on {date}: ${close_price:.2f}")
                return close_price
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting closing price for {symbol} on {date}: {e}")
            return None
    
    def validate_predictions(self) -> Dict:
        """
        Validate all active predictions that have passed their target date
        Called at end of trading day or manually
        
        Returns:
            Dictionary with validation results
        """
        active_predictions = self.prediction_db.get_active_predictions()
        validated_count = 0
        symbols_updated = set()
        errors = []
        
        now = datetime.now(self.eastern)
        
        logger.info(f"⚙ Validating {len(active_predictions)} active predictions...")
        
        for pred in active_predictions:
            try:
                target_date = datetime.fromisoformat(pred['target_date'])
                
                # Make target_date timezone-aware if it isn't
                if target_date.tzinfo is None:
                    target_date = self.eastern.localize(target_date)
                
                # Check if target date has passed
                if now >= target_date:
                    symbol = pred['symbol']
                    
                    # Fetch actual closing price
                    actual_price = self.get_closing_price(symbol, target_date)
                    
                    if actual_price:
                        # Calculate accuracy
                        predicted_price = pred['predicted_price']
                        error_percent = abs((actual_price - predicted_price) / predicted_price * 100)
                        
                        # Within 2% is considered correct
                        is_correct = error_percent <= 2.0
                        
                        # Update prediction record
                        success = self.prediction_db.update_prediction_outcome(
                            pred['prediction_id'],
                            actual_price,
                            is_correct
                        )
                        
                        if success:
                            validated_count += 1
                            symbols_updated.add(symbol)
                            logger.info(f"✓ Validated {symbol}: Predicted=${predicted_price:.2f}, "
                                       f"Actual=${actual_price:.2f}, Error={error_percent:.2f}%, "
                                       f"Correct={is_correct}")
                        else:
                            errors.append(f"Failed to update prediction {pred['prediction_id']}")
                    else:
                        errors.append(f"Could not get closing price for {symbol} on {target_date.date()}")
                        logger.warning(f"⚠ Could not validate {symbol}: No closing price data")
                        
            except Exception as e:
                errors.append(f"Error validating prediction {pred.get('prediction_id', 'unknown')}: {str(e)}")
                logger.error(f"✗ Error validating prediction: {e}")
        
        # Update accuracy statistics for updated symbols
        for symbol in symbols_updated:
            try:
                self.prediction_db.update_accuracy_stats(symbol)
                logger.info(f"✓ Updated accuracy stats for {symbol}")
            except Exception as e:
                logger.error(f"✗ Error updating stats for {symbol}: {e}")
        
        result = {
            'success': True,
            'validated_count': validated_count,
            'symbols_updated': list(symbols_updated),
            'active_remaining': len(active_predictions) - validated_count,
            'errors': errors
        }
        
        logger.info(f"✓ Validation complete: {validated_count} predictions validated, "
                   f"{len(symbols_updated)} symbols updated")
        
        return result
    
    def is_market_open(self) -> bool:
        """
        Check if US market is currently open
        
        Returns:
            True if market is open, False otherwise
        """
        now = datetime.now(self.eastern)
        
        # Market hours: 9:30 AM - 4:00 PM EST, Monday-Friday
        if now.weekday() >= 5:  # Weekend
            return False
        
        market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
        
        is_open = market_open <= now <= market_close
        
        return is_open
    
    def get_next_market_open(self) -> datetime:
        """
        Get next market open time
        
        Returns:
            Datetime of next market open
        """
        now = datetime.now(self.eastern)
        
        # Start with tomorrow
        next_open = now.replace(hour=9, minute=30, second=0, microsecond=0) + timedelta(days=1)
        
        # Skip weekends
        while next_open.weekday() >= 5:
            next_open = next_open + timedelta(days=1)
        
        return next_open


# Module-level singleton
_prediction_manager = None

def get_prediction_manager(ml_predictor, prediction_db):
    """Get or create singleton prediction manager instance"""
    global _prediction_manager
    if _prediction_manager is None:
        _prediction_manager = PredictionManager(ml_predictor, prediction_db)
    return _prediction_manager
