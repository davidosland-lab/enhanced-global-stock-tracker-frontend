"""
Swing Trading Backtest Engine - 5-Day Hold Period
==================================================

Advanced swing trading strategy with REAL sentiment analysis.

Key Features:
- 5-day position holding period (no early exits except stop loss)
- Real historical news sentiment using FinBERT
- Combines: Price Action + Technical + Sentiment + Volume
- Walk-forward validation (no look-ahead bias)
- Multiple entry/exit strategies

Author: FinBERT v4.4.4 Enhanced
Date: December 2025
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import warnings

# Try to import TensorFlow/Keras for LSTM
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    from sklearn.preprocessing import MinMaxScaler
    LSTM_AVAILABLE = True
except ImportError:
    LSTM_AVAILABLE = False
    logger.warning("TensorFlow not available - LSTM predictions will use fallback method")

warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)


class SwingTraderEngine:
    """
    5-Day Swing Trading Engine with Real Sentiment
    
    Strategy:
    1. Hold positions for EXACTLY 5 trading days
    2. Use sentiment from NEWS in past 3 days before entry
    3. Combine technical + sentiment + volume for entry
    4. Exit after 5 days OR if stop loss hit
    5. No early profit-taking (let winners run full 5 days)
    """
    
    def __init__(
        self,
        initial_capital: float = 100000.0,
        holding_period_days: int = 5,
        stop_loss_percent: float = 3.0,
        sentiment_weight: float = 0.25,
        lstm_weight: float = 0.25,
        technical_weight: float = 0.25,
        momentum_weight: float = 0.15,
        volume_weight: float = 0.10,
        confidence_threshold: float = 0.52,
        max_position_size: float = 0.25,
        use_real_sentiment: bool = True,
        use_lstm: bool = True,
        sentiment_lookback_days: int = 3,
        lstm_sequence_length: int = 60,
        lstm_epochs: int = 50,
        # Phase 1 & 2 improvements
        use_trailing_stop: bool = True,
        trailing_stop_percent: float = 50.0,
        use_profit_targets: bool = True,
        quick_profit_target: float = 8.0,
        max_profit_target: float = 12.0,
        max_concurrent_positions: int = 3,
        use_adaptive_holding: bool = True,
        use_regime_detection: bool = True,
        use_dynamic_weights: bool = True
    ):
        """
        Initialize 5-day swing trader with LSTM
        
        Args:
            initial_capital: Starting capital
            holding_period_days: Position hold period (default 5 days)
            stop_loss_percent: Stop loss (default 3%)
            sentiment_weight: Weight for sentiment signals (25%)
            lstm_weight: Weight for LSTM neural network (25%)
            technical_weight: Weight for technical signals (25%)
            momentum_weight: Weight for momentum signals (15%)
            volume_weight: Weight for volume signals (10%)
            confidence_threshold: Minimum confidence for entry (52% - lowered for more trades)
            max_position_size: Max position as % of capital (25%)
            use_real_sentiment: Use real news sentiment (True) or skip (False)
            use_lstm: Use LSTM neural network (True) or fallback (False)
            sentiment_lookback_days: Days of news to analyze (3 days)
            lstm_sequence_length: LSTM input sequence length (60 days)
            lstm_epochs: LSTM training epochs (50)
        """
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.holding_period_days = holding_period_days
        self.stop_loss_percent = stop_loss_percent
        self.confidence_threshold = confidence_threshold
        self.max_position_size = max_position_size
        self.use_real_sentiment = use_real_sentiment
        self.use_lstm = use_lstm and LSTM_AVAILABLE
        self.sentiment_lookback_days = sentiment_lookback_days
        self.lstm_sequence_length = lstm_sequence_length
        self.lstm_epochs = lstm_epochs
        
        # Phase 1 & 2: Enhanced features
        self.use_trailing_stop = use_trailing_stop
        self.trailing_stop_percent = trailing_stop_percent
        self.use_profit_targets = use_profit_targets
        self.quick_profit_target = quick_profit_target
        self.max_profit_target = max_profit_target
        self.max_concurrent_positions = max_concurrent_positions
        self.use_adaptive_holding = use_adaptive_holding
        self.use_regime_detection = use_regime_detection
        self.use_dynamic_weights = use_dynamic_weights
        
        # Model weights (can be dynamically adjusted)
        self.base_sentiment_weight = sentiment_weight
        self.base_lstm_weight = lstm_weight
        self.base_technical_weight = technical_weight
        self.base_momentum_weight = momentum_weight
        self.base_volume_weight = volume_weight
        
        self.sentiment_weight = sentiment_weight
        self.lstm_weight = lstm_weight
        self.technical_weight = technical_weight
        self.momentum_weight = momentum_weight
        self.volume_weight = volume_weight
        
        # Market regime state
        self.current_regime = "UNKNOWN"
        
        # Validate weights sum to 1.0
        total_weight = sentiment_weight + lstm_weight + technical_weight + momentum_weight + volume_weight
        if abs(total_weight - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {total_weight}")
        
        # LSTM model cache
        self.lstm_model = None
        self.lstm_scaler = None
        self.lstm_trained = False
        
        # Trading state
        self.positions = []
        self.closed_trades = []
        self.pending_orders = []
        
        # Performance tracking
        self.equity_curve = []
        self.daily_returns = []
        
        logger.info(
            f"Swing trader initialized: {holding_period_days}-day hold (adaptive={use_adaptive_holding}), "
            f"sentiment={use_real_sentiment}, LSTM={self.use_lstm}, threshold={confidence_threshold}"
        )
        logger.info(
            f"Phase 1&2 features: trailing_stop={use_trailing_stop}, "
            f"profit_targets={use_profit_targets}, max_positions={max_concurrent_positions}, "
            f"regime_detection={use_regime_detection}"
        )
    
    def run_backtest(
        self,
        symbol: str,
        price_data: pd.DataFrame,
        start_date: str,
        end_date: str,
        news_data: Optional[pd.DataFrame] = None
    ) -> Dict:
        """
        Run complete swing trading backtest with Phase 1 & 2 enhancements
        
        Args:
            symbol: Stock ticker
            price_data: Historical OHLCV data (daily)
            start_date: Backtest start date
            end_date: Backtest end date
            news_data: Historical news with sentiment scores (optional)
        
        Returns:
            Dictionary with backtest results and metrics
        """
        logger.info(f"Starting {self.holding_period_days}-day swing backtest for {symbol}")
        logger.info(f"Phase 1&2 active: trailing_stop={self.use_trailing_stop}, profit_targets={self.use_profit_targets}, max_pos={self.max_concurrent_positions}")
        
        # Filter data to backtest period
        mask = (price_data.index >= start_date) & (price_data.index <= end_date)
        backtest_data = price_data[mask].copy()
        
        if len(backtest_data) < 20:
            return {
                'error': f'Insufficient data: {len(backtest_data)} days (need at least 20)',
                'symbol': symbol
            }
        
        # Reset state
        self.capital = self.initial_capital
        self.positions = []
        self.closed_trades = []
        self.equity_curve = []
        
        # Iterate through each trading day
        for current_date in backtest_data.index:
            # Get data available up to current date (no look-ahead bias)
            available_data = price_data[price_data.index <= current_date]
            
            if len(available_data) < 60:
                continue  # Need at least 60 days for indicators
            
            current_price = backtest_data.loc[current_date, 'Close']
            current_high = backtest_data.loc[current_date, 'High']
            
            # PHASE 2: Detect market regime
            if self.use_regime_detection and len(available_data) >= 200:
                self.current_regime = self._detect_market_regime(available_data, current_date)
                
                # Adjust weights dynamically based on regime
                news_count = len(news_data) if news_data is not None else 0
                self._adjust_weights_for_regime(self.current_regime, news_count)
            
            # Step 1: Check existing positions for exits (with trailing stop & profit targets)
            self._check_position_exits(current_date, current_price, current_high, backtest_data)
            
            # Step 2: PHASE 1 - Allow multiple concurrent positions (up to max)
            if len(self.positions) < self.max_concurrent_positions:
                signal = self._generate_swing_signal(
                    symbol=symbol,
                    current_date=current_date,
                    available_data=available_data,
                    news_data=news_data
                )
                
                # Step 3: Enter position if signal is strong
                if signal['prediction'] == 'BUY' and signal['confidence'] >= self.confidence_threshold:
                    self._enter_position(
                        date=current_date,
                        price=current_price,
                        signal=signal,
                        price_data=available_data
                    )
            
            # Step 4: Track equity
            position_value = sum(p['shares'] * current_price for p in self.positions)
            total_equity = self.capital + position_value
            self.equity_curve.append({
                'date': current_date,
                'equity': total_equity,
                'cash': self.capital,
                'position_value': position_value,
                'num_positions': len(self.positions),
                'regime': self.current_regime
            })
        
        # Close any remaining positions at end
        if self.positions:
            final_price = backtest_data.iloc[-1]['Close']
            final_date = backtest_data.index[-1]
            for pos in self.positions[:]:
                self._exit_position(pos, final_date, final_price, 'END_OF_BACKTEST')
        
        # Calculate metrics
        metrics = self._calculate_metrics(symbol, start_date, end_date)
        
        return metrics
    
    def _generate_swing_signal(
        self,
        symbol: str,
        current_date: datetime,
        available_data: pd.DataFrame,
        news_data: Optional[pd.DataFrame] = None
    ) -> Dict:
        """
        Generate swing trading signal combining all components
        
        Args:
            symbol: Stock ticker
            current_date: Current date for prediction
            available_data: Historical data up to current date
            news_data: Historical news data
        
        Returns:
            Signal dictionary with prediction, confidence, and component scores
        """
        # Get last 60 days for analysis
        training_window = available_data.tail(60)
        current_price = training_window['Close'].iloc[-1]
        
        # Component 1: Sentiment Analysis (25%)
        sentiment_score = self._analyze_sentiment(
            symbol=symbol,
            current_date=current_date,
            news_data=news_data
        )
        
        # Component 2: LSTM Neural Network (25%)
        lstm_score = self._analyze_lstm(training_window, available_data)
        
        # Component 3: Technical Analysis (25%)
        technical_score = self._analyze_technical(training_window, current_price)
        
        # Component 4: Momentum Analysis (15%)
        momentum_score = self._analyze_momentum(training_window, current_price)
        
        # Component 5: Volume Analysis (10%)
        volume_score = self._analyze_volume(training_window)
        
        # Combine with weights
        combined_score = (
            sentiment_score * self.sentiment_weight +
            lstm_score * self.lstm_weight +
            technical_score * self.technical_weight +
            momentum_score * self.momentum_weight +
            volume_score * self.volume_weight
        )
        
        # DEBUG LOGGING - See what scores are being generated
        logger.info(
            f"Signal for {symbol} on {current_date.date()}: "
            f"Combined={combined_score:.3f} | "
            f"Sentiment={sentiment_score:.3f} | "
            f"LSTM={lstm_score:.3f} | "
            f"Technical={technical_score:.3f} | "
            f"Momentum={momentum_score:.3f} | "
            f"Volume={volume_score:.3f}"
        )
        
        # Generate prediction - LOWERED THRESHOLDS for more trades
        if combined_score > 0.05:  # Was 0.15 - TOO HIGH!
            prediction = 'BUY'
            confidence = min(0.50 + combined_score * 0.5, 0.95)
        elif combined_score < -0.05:  # Was -0.15 - TOO HIGH!
            prediction = 'SELL'
            confidence = min(0.50 + abs(combined_score) * 0.5, 0.95)
        else:
            prediction = 'HOLD'
            confidence = 0.50
        
        return {
            'prediction': prediction,
            'confidence': confidence,
            'combined_score': combined_score,
            'sentiment_score': sentiment_score,
            'lstm_score': lstm_score,
            'technical_score': technical_score,
            'momentum_score': momentum_score,
            'volume_score': volume_score,
            'timestamp': current_date
        }
    
    def _train_lstm_model(self, price_data: pd.DataFrame):
        """
        Train LSTM model on historical price data
        
        Args:
            price_data: Historical OHLCV DataFrame
        """
        if not self.use_lstm or not LSTM_AVAILABLE:
            logger.info("LSTM not available or disabled")
            return
        
        try:
            logger.info("Training LSTM model...")
            
            # Prepare data
            prices = price_data['Close'].values.reshape(-1, 1)
            
            # Normalize data
            self.lstm_scaler = MinMaxScaler(feature_range=(0, 1))
            scaled_prices = self.lstm_scaler.fit_transform(prices)
            
            # Create sequences
            X, y = [], []
            for i in range(self.lstm_sequence_length, len(scaled_prices) - 5):
                X.append(scaled_prices[i-self.lstm_sequence_length:i, 0])
                # Predict 5-day forward return (for 5-day swing)
                future_price = scaled_prices[i+5, 0]
                current_price = scaled_prices[i, 0]
                y.append(1 if future_price > current_price else 0)  # Binary: up or down
            
            if len(X) < 100:
                logger.warning(f"Insufficient data for LSTM training: {len(X)} samples")
                return
            
            X, y = np.array(X), np.array(y)
            X = X.reshape((X.shape[0], X.shape[1], 1))
            
            # Split train/val
            split = int(0.8 * len(X))
            X_train, X_val = X[:split], X[split:]
            y_train, y_val = y[:split], y[split:]
            
            # Build LSTM model
            model = Sequential([
                LSTM(50, return_sequences=True, input_shape=(self.lstm_sequence_length, 1)),
                Dropout(0.2),
                LSTM(50, return_sequences=False),
                Dropout(0.2),
                Dense(25, activation='relu'),
                Dense(1, activation='sigmoid')  # Binary classification
            ])
            
            model.compile(
                optimizer='adam',
                loss='binary_crossentropy',
                metrics=['accuracy']
            )
            
            # Train
            history = model.fit(
                X_train, y_train,
                validation_data=(X_val, y_val),
                epochs=self.lstm_epochs,
                batch_size=32,
                verbose=0
            )
            
            self.lstm_model = model
            self.lstm_trained = True
            
            # Get final accuracy
            val_accuracy = history.history['val_accuracy'][-1]
            logger.info(f"LSTM trained: {len(X_train)} samples, val_accuracy={val_accuracy:.3f}")
            
        except Exception as e:
            logger.error(f"LSTM training failed: {e}")
            self.lstm_trained = False
    
    def _analyze_lstm(self, training_window: pd.DataFrame, available_data: pd.DataFrame) -> float:
        """
        LSTM-based price pattern prediction (-1 to +1)
        
        Args:
            training_window: Recent 60-day window
            available_data: All historical data up to current date
        
        Returns:
            LSTM score: -1.0 (strong sell) to +1.0 (strong buy)
        """
        if not self.use_lstm or not LSTM_AVAILABLE:
            # Fallback: simple momentum
            try:
                prices = training_window['Close'].values
                returns = (prices[-1] / prices[-10] - 1) if len(prices) >= 10 else 0
                return np.clip(returns * 5, -1.0, 1.0)
            except:
                return 0.0
        
        try:
            # Train model once if not trained
            if not self.lstm_trained and len(available_data) >= 200:
                self._train_lstm_model(available_data)
            
            if not self.lstm_trained or self.lstm_model is None:
                # Not enough data - use fallback
                prices = training_window['Close'].values
                returns = (prices[-1] / prices[-10] - 1) if len(prices) >= 10 else 0
                return np.clip(returns * 5, -1.0, 1.0)
            
            # Get last N days
            prices = available_data['Close'].tail(self.lstm_sequence_length).values.reshape(-1, 1)
            
            if len(prices) < self.lstm_sequence_length:
                return 0.0
            
            # Normalize
            scaled_prices = self.lstm_scaler.transform(prices)
            X = scaled_prices.reshape((1, self.lstm_sequence_length, 1))
            
            # Predict
            prediction = self.lstm_model.predict(X, verbose=0)[0][0]
            
            # Convert probability to score
            # prediction = 0.5 means neutral, > 0.5 bullish, < 0.5 bearish
            lstm_score = (prediction - 0.5) * 2.0  # Scale to [-1, 1]
            
            # Add confidence weighting
            confidence = abs(prediction - 0.5) * 2.0  # How far from neutral
            lstm_score = lstm_score * confidence  # Reduce score if low confidence
            
            logger.debug(f"LSTM prediction: {prediction:.3f}, score: {lstm_score:.3f}")
            
            return np.clip(lstm_score, -1.0, 1.0)
            
        except Exception as e:
            logger.error(f"LSTM prediction error: {e}")
            return 0.0
    
    def _analyze_sentiment(
        self,
        symbol: str,
        current_date: datetime,
        news_data: Optional[pd.DataFrame] = None
    ) -> float:
        """
        Analyze news sentiment for past N days
        
        Args:
            symbol: Stock ticker
            current_date: Current date
            news_data: Historical news DataFrame with columns:
                       ['date', 'headline', 'sentiment_score', 'sentiment_label']
        
        Returns:
            Sentiment score: -1.0 (very bearish) to +1.0 (very bullish)
        """
        if not self.use_real_sentiment or news_data is None or news_data.empty:
            # Fallback: No sentiment data available - don't penalize, use technical/momentum instead
            logger.debug(f"No sentiment data for {symbol} on {current_date} - using neutral")
            # Return 0.0 but LOG that sentiment is missing so other components drive decisions
            return 0.0  # Neutral - other components will drive signal
        
        try:
            # Get news from past N days (no look-ahead bias)
            lookback_start = current_date - timedelta(days=self.sentiment_lookback_days)
            
            # Filter news to lookback period (before current_date)
            mask = (news_data['date'] >= lookback_start) & (news_data['date'] < current_date)
            recent_news = news_data[mask]
            
            if len(recent_news) == 0:
                logger.debug(f"No news found for {symbol} in past {self.sentiment_lookback_days} days")
                # No news doesn't mean neutral - use default bullish bias for swing trading
                return 0.05  # Slight bullish bias when no news (swing = buy dips)
            
            # Calculate weighted average sentiment (more recent = higher weight)
            sentiments = []
            weights = []
            
            for idx, row in recent_news.iterrows():
                days_ago = (current_date - row['date']).days
                # Weight: more recent news gets higher weight
                weight = 1.0 / (1.0 + days_ago * 0.3)
                
                # Get sentiment score (-1 to +1)
                if 'sentiment_score' in row:
                    sentiment = row['sentiment_score']
                elif 'sentiment_label' in row:
                    # Convert label to score
                    label = str(row['sentiment_label']).lower()
                    if label == 'positive':
                        sentiment = 0.7
                    elif label == 'negative':
                        sentiment = -0.7
                    else:
                        sentiment = 0.0
                else:
                    sentiment = 0.0
                
                sentiments.append(sentiment)
                weights.append(weight)
            
            # Weighted average
            if sum(weights) > 0:
                weighted_sentiment = np.average(sentiments, weights=weights)
            else:
                weighted_sentiment = 0.0
            
            # Log sentiment for debugging
            logger.info(
                f"Sentiment for {symbol} on {current_date}: "
                f"{weighted_sentiment:.3f} (from {len(recent_news)} articles)"
            )
            
            # Clip to [-1, 1]
            return np.clip(weighted_sentiment, -1.0, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating sentiment: {e}")
            return 0.0
    
    def _analyze_technical(self, data: pd.DataFrame, current_price: float) -> float:
        """Technical analysis score (-1 to +1)"""
        try:
            prices = data['Close'].values
            
            # RSI
            delta = pd.Series(prices).diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1] if len(rsi) > 0 else 50
            
            # RSI signal
            if current_rsi < 30:
                rsi_signal = 0.5  # Oversold - bullish
            elif current_rsi > 70:
                rsi_signal = -0.5  # Overbought - bearish
            else:
                rsi_signal = (50 - current_rsi) / 100.0  # Scaled
            
            # Moving averages
            sma_20 = prices[-20:].mean() if len(prices) >= 20 else prices.mean()
            sma_50 = prices[-50:].mean() if len(prices) >= 50 else prices.mean()
            
            # Price vs MA signal
            ma_signal = 0
            if current_price > sma_20 and sma_20 > sma_50:
                ma_signal = 0.4  # Strong uptrend
            elif current_price < sma_20 and sma_20 < sma_50:
                ma_signal = -0.4  # Strong downtrend
            elif current_price > sma_20:
                ma_signal = 0.2  # Weak uptrend
            else:
                ma_signal = -0.2  # Weak downtrend
            
            # Bollinger Bands
            bb_sma = prices[-20:].mean() if len(prices) >= 20 else prices.mean()
            bb_std = pd.Series(prices[-20:]).std() if len(prices) >= 20 else pd.Series(prices).std()
            upper_band = bb_sma + (bb_std * 2)
            lower_band = bb_sma - (bb_std * 2)
            
            bb_signal = 0
            if current_price < lower_band:
                bb_signal = 0.3  # Below lower band - bullish
            elif current_price > upper_band:
                bb_signal = -0.3  # Above upper band - bearish
            
            # Combined technical score
            technical_score = (rsi_signal * 0.4 + ma_signal * 0.4 + bb_signal * 0.2)
            
            return np.clip(technical_score, -1.0, 1.0)
            
        except Exception as e:
            logger.error(f"Error in technical analysis: {e}")
            return 0.0
    
    def _analyze_momentum(self, data: pd.DataFrame, current_price: float) -> float:
        """Momentum analysis score (-1 to +1)"""
        try:
            prices = data['Close'].values
            returns = np.diff(prices) / prices[:-1]
            
            # Recent momentum (5-day)
            recent_return = (prices[-1] / prices[-6] - 1) if len(prices) >= 6 else 0
            
            # Medium momentum (20-day)
            medium_return = (prices[-1] / prices[-21] - 1) if len(prices) >= 21 else 0
            
            # Acceleration
            recent_momentum = returns[-5:].mean() if len(returns) >= 5 else 0
            medium_momentum = returns[-20:].mean() if len(returns) >= 20 else 0
            acceleration = recent_momentum - medium_momentum
            
            # Momentum score
            momentum_score = (
                recent_return * 0.4 +
                medium_return * 0.3 +
                acceleration * 10.0 * 0.3  # Scale acceleration
            )
            
            return np.clip(momentum_score, -1.0, 1.0)
            
        except Exception as e:
            logger.error(f"Error in momentum analysis: {e}")
            return 0.0
    
    def _analyze_volume(self, data: pd.DataFrame) -> float:
        """Volume analysis score (-1 to +1)"""
        try:
            if 'Volume' not in data.columns:
                return 0.0
            
            volumes = data['Volume'].values
            prices = data['Close'].values
            
            # Average volume
            avg_volume = volumes[-20:].mean() if len(volumes) >= 20 else volumes.mean()
            current_volume = volumes[-1]
            
            # Volume ratio
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
            
            # Price change
            price_change = (prices[-1] / prices[-2] - 1) if len(prices) >= 2 else 0
            
            # Volume + price confirmation
            if volume_ratio > 1.5 and price_change > 0.01:
                volume_score = 0.5  # High volume up move - bullish
            elif volume_ratio > 1.5 and price_change < -0.01:
                volume_score = -0.5  # High volume down move - bearish
            elif volume_ratio < 0.5:
                volume_score = 0.0  # Low volume - neutral
            else:
                volume_score = price_change * 10.0  # Proportional to price change
            
            return np.clip(volume_score, -1.0, 1.0)
            
        except Exception as e:
            logger.error(f"Error in volume analysis: {e}")
            return 0.0
    
    # ========================================================================
    # PHASE 1 & 2: ENHANCED TRADING LOGIC
    # ========================================================================
    
    def _detect_market_regime(self, price_data: pd.DataFrame, current_date: datetime) -> str:
        """
        Phase 2: Detect current market regime
        
        Returns:
            'STRONG_UPTREND', 'MILD_UPTREND', 'RANGING', or 'DOWNTREND'
        """
        try:
            if len(price_data) < 200:
                return "UNKNOWN"
            
            # Calculate moving averages
            ma_50 = price_data['Close'].rolling(50).mean()
            ma_200 = price_data['Close'].rolling(200).mean()
            
            if current_date not in ma_50.index or current_date not in ma_200.index:
                return "UNKNOWN"
            
            current_ma50 = ma_50.loc[current_date]
            current_ma200 = ma_200.loc[current_date]
            current_price = price_data.loc[current_date, 'Close']
            
            # Check for missing data
            if pd.isna(current_ma50) or pd.isna(current_ma200):
                return "UNKNOWN"
            
            # Classify regime
            if current_price > current_ma50 > current_ma200:
                # Uptrend - check strength
                distance_from_ma50 = (current_price / current_ma50 - 1)
                if distance_from_ma50 > 0.05:  # 5%+ above MA50
                    return "STRONG_UPTREND"
                else:
                    return "MILD_UPTREND"
            elif abs(current_price / current_ma50 - 1) < 0.03:  # Within 3% of MA
                return "RANGING"
            else:
                return "DOWNTREND"
        
        except Exception as e:
            logger.error(f"Error detecting regime: {e}")
            return "UNKNOWN"
    
    def _calculate_trend_strength(self, price_data: pd.DataFrame, current_date: datetime) -> float:
        """
        Phase 2: Calculate trend strength (0.0 to 1.0)
        Used for adaptive holding period
        """
        try:
            if len(price_data) < 50:
                return 0.5  # Default medium strength
            
            # ADX-like calculation
            closes = price_data['Close'].values[-50:]
            highs = price_data['High'].values[-50:]
            lows = price_data['Low'].values[-50:]
            
            # Calculate directional movement
            up_move = highs[1:] - highs[:-1]
            down_move = lows[:-1] - lows[1:]
            
            avg_up = np.mean(np.maximum(up_move, 0))
            avg_down = np.mean(np.maximum(down_move, 0))
            
            # Trend strength
            if avg_up + avg_down == 0:
                return 0.5
            
            trend_strength = abs(avg_up - avg_down) / (avg_up + avg_down)
            return np.clip(trend_strength, 0.0, 1.0)
        
        except Exception as e:
            logger.error(f"Error calculating trend strength: {e}")
            return 0.5
    
    def _calculate_adaptive_holding_period(self, regime: str, trend_strength: float) -> int:
        """
        Phase 2: Calculate adaptive holding period based on market regime
        
        Strong uptrend: 10-15 days
        Mild uptrend: 5-8 days
        Ranging: 3-5 days
        Downtrend: 3-5 days
        """
        if not self.use_adaptive_holding:
            return self.holding_period_days
        
        if regime == "STRONG_UPTREND":
            return 12  # Let winners run
        elif regime == "MILD_UPTREND":
            if trend_strength > 0.6:
                return 8
            else:
                return 5
        elif regime == "RANGING":
            return 4  # Quick in/out
        elif regime == "DOWNTREND":
            return 3  # Exit fast
        else:
            return self.holding_period_days
    
    def _adjust_weights_for_regime(self, regime: str, news_count: int = 0):
        """
        Phase 2: Dynamically adjust component weights based on market regime
        """
        if not self.use_dynamic_weights:
            return
        
        if regime == "STRONG_UPTREND":
            # In strong trends, momentum and technical matter more
            self.sentiment_weight = 0.15
            self.lstm_weight = 0.20
            self.technical_weight = 0.30
            self.momentum_weight = 0.25
            self.volume_weight = 0.10
        elif regime == "RANGING":
            # In ranging markets, sentiment and technical signals shine
            if news_count > 10:
                self.sentiment_weight = 0.35  # Lots of news
                self.technical_weight = 0.30
            else:
                self.sentiment_weight = 0.20
                self.technical_weight = 0.35
            self.lstm_weight = 0.20
            self.momentum_weight = 0.10
            self.volume_weight = 0.10
        elif regime == "DOWNTREND":
            # In downtrends, be more cautious
            self.sentiment_weight = 0.30  # Pay attention to news
            self.lstm_weight = 0.25
            self.technical_weight = 0.25
            self.momentum_weight = 0.10
            self.volume_weight = 0.10
        else:
            # Default weights
            self.sentiment_weight = self.base_sentiment_weight
            self.lstm_weight = self.base_lstm_weight
            self.technical_weight = self.base_technical_weight
            self.momentum_weight = self.base_momentum_weight
            self.volume_weight = self.base_volume_weight
    
    def _calculate_dynamic_position_size(self) -> float:
        """
        Phase 1: Dynamic position sizing based on active positions
        
        Position 1: 25% of capital
        Position 2: 20% of capital  
        Position 3: 15% of capital
        Total max: 60% deployed, 40% in reserve
        """
        active_positions = len(self.positions)
        
        if active_positions == 0:
            return 0.25
        elif active_positions == 1:
            return 0.20
        elif active_positions == 2:
            return 0.15
        else:
            return 0.0  # No more capacity
    
    def _enter_position(self, date: datetime, price: float, signal: Dict, price_data: pd.DataFrame = None):
        """Enter a new swing trading position with Phase 1 & 2 enhancements"""
        # PHASE 1: Dynamic position sizing based on number of active positions
        dynamic_position_size = self._calculate_dynamic_position_size()
        position_value = self.capital * dynamic_position_size
        shares = int(position_value / price)
        
        # DEBUG LOGGING
        logger.info(f"POSITION SIZING (Phase 1 - Dynamic):")
        logger.info(f"  Current Capital: ${self.capital:,.2f}")
        logger.info(f"  Active Positions: {len(self.positions)}")
        logger.info(f"  Dynamic Position Size: {dynamic_position_size:.4f} ({dynamic_position_size * 100:.2f}%)")
        logger.info(f"  Position Value: ${position_value:,.2f}")
        logger.info(f"  Stock Price: ${price:.2f}")
        logger.info(f"  Calculated Shares: {shares}")
        
        if shares == 0:
            logger.warning(f"Cannot enter position: insufficient capital (capital=${self.capital:.2f}, position_value=${position_value:.2f})")
            return
        
        actual_cost = shares * price
        commission = actual_cost * 0.001  # 0.1% commission
        total_cost = actual_cost + commission
        
        if total_cost > self.capital:
            # Reduce shares to fit capital
            shares = int((self.capital * 0.999) / price)
            actual_cost = shares * price
            commission = actual_cost * 0.001
            total_cost = actual_cost + commission
        
        # Calculate stop loss price
        stop_loss_price = price * (1 - self.stop_loss_percent / 100.0)
        
        # PHASE 2: Adaptive holding period based on market regime
        if self.use_adaptive_holding and price_data is not None:
            trend_strength = self._calculate_trend_strength(price_data, date)
            adaptive_holding_days = self._calculate_adaptive_holding_period(self.current_regime, trend_strength)
        else:
            adaptive_holding_days = self.holding_period_days
        
        target_exit_date = date + timedelta(days=adaptive_holding_days)
        
        # PHASE 1: Profit targets
        quick_profit_price = price * (1 + self.quick_profit_target / 100.0) if self.use_profit_targets else None
        max_profit_price = price * (1 + self.max_profit_target / 100.0) if self.use_profit_targets else None
        
        # Create position
        position = {
            'entry_date': date,
            'entry_price': price,
            'shares': shares,
            'cost_basis': actual_cost,
            'commission_paid': commission,
            'stop_loss_price': stop_loss_price,
            'target_exit_date': target_exit_date,
            'adaptive_holding_days': adaptive_holding_days,
            'signal': signal,
            'days_held': 0,
            # Phase 1: Trailing stop tracking
            'highest_price': price,
            'trailing_stop_price': stop_loss_price,
            # Phase 1: Profit targets
            'quick_profit_price': quick_profit_price,
            'max_profit_price': max_profit_price,
            # Phase 2: Regime context
            'entry_regime': self.current_regime
        }
        
        # Update capital
        self.capital -= total_cost
        self.positions.append(position)
        
        logger.info(
            f"ENTER: {shares} shares @ ${price:.2f} on {date.date()}, "
            f"stop=${stop_loss_price:.2f}, holding={adaptive_holding_days}d, exit_target={target_exit_date.date()}, "
            f"confidence={signal['confidence']:.2%}, regime={self.current_regime}"
        )
        if self.use_profit_targets:
            logger.info(f"  Profit targets: Quick=${quick_profit_price:.2f} (+{self.quick_profit_target}%), Max=${max_profit_price:.2f} (+{self.max_profit_target}%)")
    
    def _check_position_exits(self, current_date: datetime, current_price: float, current_high: float, price_data: pd.DataFrame):
        """Check if positions should be exited with Phase 1 & 2 enhancements"""
        for position in self.positions[:]:  # Copy list to modify during iteration
            position['days_held'] += 1
            
            # Get intraday low for stop loss check
            if current_date in price_data.index:
                intraday_low = price_data.loc[current_date, 'Low']
            else:
                intraday_low = current_price
            
            # PHASE 1: Update trailing stop if price moved higher
            if self.use_trailing_stop:
                # Track highest price since entry
                position['highest_price'] = max(position['highest_price'], current_high)
                
                # Calculate trailing stop (50% of profit)
                profit_from_entry = position['highest_price'] - position['entry_price']
                trailing_distance = profit_from_entry * (self.trailing_stop_percent / 100.0)
                new_trailing_stop = position['highest_price'] - trailing_distance
                
                # Only raise the trailing stop, never lower it
                if new_trailing_stop > position['trailing_stop_price']:
                    old_stop = position['trailing_stop_price']
                    position['trailing_stop_price'] = new_trailing_stop
                    logger.debug(
                        f"Trailing stop updated: ${old_stop:.2f} -> ${new_trailing_stop:.2f} "
                        f"(high=${position['highest_price']:.2f}, profit=${profit_from_entry:.2f})"
                    )
            
            # Exit reason
            exit_reason = None
            exit_price = current_price
            
            # PHASE 1: Check profit targets FIRST (most profitable)
            if self.use_profit_targets:
                if position['max_profit_price'] and current_high >= position['max_profit_price']:
                    exit_reason = f'MAX_PROFIT_TARGET_{self.max_profit_target}%'
                    exit_price = position['max_profit_price']
                elif position['quick_profit_price'] and current_high >= position['quick_profit_price']:
                    # Only take quick profit if held at least 2 days
                    if position['days_held'] >= 2:
                        exit_reason = f'QUICK_PROFIT_TARGET_{self.quick_profit_target}%'
                        exit_price = position['quick_profit_price']
            
            # Check 1: Trailing stop hit (Phase 1)
            if not exit_reason and self.use_trailing_stop:
                if intraday_low <= position['trailing_stop_price']:
                    exit_reason = 'TRAILING_STOP'
                    exit_price = position['trailing_stop_price']
            
            # Check 2: Regular stop loss hit
            if not exit_reason and intraday_low <= position['stop_loss_price']:
                exit_reason = 'STOP_LOSS'
                exit_price = position['stop_loss_price']
            
            # Check 3: Adaptive holding period complete (Phase 2)
            if not exit_reason and current_date >= position['target_exit_date']:
                exit_reason = f'TARGET_EXIT_{position["adaptive_holding_days"]}D'
                exit_price = current_price
            
            # Exit if triggered
            if exit_reason:
                self._exit_position(position, current_date, exit_price, exit_reason)
    
    def _exit_position(self, position: Dict, exit_date: datetime, exit_price: float, exit_reason: str):
        """Exit a position and record trade"""
        # Calculate proceeds
        gross_proceeds = position['shares'] * exit_price
        commission = gross_proceeds * 0.001  # 0.1% commission
        net_proceeds = gross_proceeds - commission
        
        # Calculate P&L
        total_cost = position['cost_basis'] + position['commission_paid']
        pnl = net_proceeds - total_cost
        pnl_percent = (pnl / total_cost) * 100.0
        
        # Update capital
        self.capital += net_proceeds
        
        # Record trade
        trade = {
            'entry_date': position['entry_date'],
            'exit_date': exit_date,
            'days_held': position['days_held'],
            'entry_price': position['entry_price'],
            'exit_price': exit_price,
            'shares': position['shares'],
            'cost_basis': position['cost_basis'],
            'proceeds': net_proceeds,
            'pnl': pnl,
            'pnl_percent': pnl_percent,
            'exit_reason': exit_reason,
            'commission_total': position['commission_paid'] + commission,
            'signal_confidence': position['signal']['confidence'],
            'sentiment_score': position['signal'].get('sentiment_score', 0.0)
        }
        
        self.closed_trades.append(trade)
        self.positions.remove(position)
        
        logger.info(
            f"EXIT: {position['shares']} shares @ ${exit_price:.2f} on {exit_date.date()}, "
            f"P&L=${pnl:.2f} ({pnl_percent:+.2f}%), reason={exit_reason}, "
            f"held={position['days_held']} days"
        )
    
    def _calculate_metrics(self, symbol: str, start_date: str, end_date: str) -> Dict:
        """Calculate comprehensive performance metrics"""
        if not self.closed_trades:
            # Return valid results with 0 trades instead of error
            return {
                'symbol': symbol,
                'start_date': start_date,
                'end_date': end_date,
                'initial_capital': self.initial_capital,
                'final_value': self.capital,
                'total_return': 0.0,
                'total_return_pct': 0.0,
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0.0,
                'profit_factor': 0.0,
                'sharpe_ratio': 0.0,
                'max_drawdown': 0.0,
                'avg_hold_time': 0.0,
                'trades': [],
                'equity_curve': [],
                'message': 'No trades executed - strategy did not find any opportunities that met the criteria'
            }
        
        # Convert to DataFrame for easier analysis
        trades_df = pd.DataFrame(self.closed_trades)
        
        # Basic metrics
        total_trades = len(trades_df)
        winning_trades = len(trades_df[trades_df['pnl'] > 0])
        losing_trades = len(trades_df[trades_df['pnl'] <= 0])
        win_rate = (winning_trades / total_trades) * 100.0
        
        # P&L metrics
        total_pnl = trades_df['pnl'].sum()
        avg_win = trades_df[trades_df['pnl'] > 0]['pnl'].mean() if winning_trades > 0 else 0
        avg_loss = trades_df[trades_df['pnl'] <= 0]['pnl'].mean() if losing_trades > 0 else 0
        largest_win = trades_df['pnl'].max()
        largest_loss = trades_df['pnl'].min()
        
        # Return metrics
        final_capital = self.capital + sum(p['shares'] * trades_df.iloc[-1]['exit_price'] for p in self.positions)
        total_return_pct = ((final_capital / self.initial_capital) - 1) * 100.0
        
        # Profit factor
        gross_profit = trades_df[trades_df['pnl'] > 0]['pnl'].sum() if winning_trades > 0 else 0
        gross_loss = abs(trades_df[trades_df['pnl'] <= 0]['pnl'].sum()) if losing_trades > 0 else 0.01
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        # Equity curve analysis
        equity_df = pd.DataFrame(self.equity_curve)
        equity_df['returns'] = equity_df['equity'].pct_change()
        
        # Sharpe ratio (handle NaN/inf)
        if len(equity_df) > 1 and equity_df['returns'].std() > 0:
            sharpe_ratio = (equity_df['returns'].mean() / equity_df['returns'].std()) * np.sqrt(252)
            if np.isnan(sharpe_ratio) or np.isinf(sharpe_ratio):
                sharpe_ratio = 0.0
        else:
            sharpe_ratio = 0.0
        
        # Drawdown (handle NaN)
        equity_df['cummax'] = equity_df['equity'].cummax()
        equity_df['drawdown'] = (equity_df['equity'] - equity_df['cummax']) / equity_df['cummax'] * 100
        max_drawdown = equity_df['drawdown'].min()
        if np.isnan(max_drawdown):
            max_drawdown = 0.0
        
        # Exit reason breakdown
        exit_reasons = trades_df['exit_reason'].value_counts().to_dict()
        
        # Sentiment correlation (handle NaN)
        if 'sentiment_score' in trades_df.columns and 'pnl_percent' in trades_df.columns:
            sentiment_corr = trades_df[['sentiment_score', 'pnl_percent']].corr().iloc[0, 1]
            if np.isnan(sentiment_corr):
                sentiment_corr = 0.0
        else:
            sentiment_corr = 0.0
        
        # Avg days held (handle NaN)
        avg_days_held = trades_df['days_held'].mean()
        if np.isnan(avg_days_held):
            avg_days_held = 0.0
        
        return {
            'symbol': symbol,
            'start_date': start_date,
            'end_date': end_date,
            'strategy': f'{self.holding_period_days}-Day Swing Trading',
            'initial_capital': self.initial_capital,
            'final_capital': final_capital,
            'total_return_pct': total_return_pct,
            'total_pnl': total_pnl,
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'largest_win': largest_win,
            'largest_loss': largest_loss,
            'profit_factor': profit_factor,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'exit_reasons': exit_reasons,
            'sentiment_correlation': sentiment_corr,
            'avg_days_held': avg_days_held,
            'trades': self._clean_dict_for_json(trades_df.to_dict('records')),
            'equity_curve': self._clean_dict_for_json(equity_df.to_dict('records'))
        }
    
    def _clean_dict_for_json(self, data):
        """Replace NaN/Inf values with None for JSON serialization"""
        import math
        
        if isinstance(data, list):
            return [self._clean_dict_for_json(item) for item in data]
        elif isinstance(data, dict):
            return {k: self._clean_dict_for_json(v) for k, v in data.items()}
        elif isinstance(data, float):
            if math.isnan(data) or math.isinf(data):
                return 0.0
            return data
        else:
            return data


# Helper function for easy integration
def run_swing_backtest(
    symbol: str,
    price_data: pd.DataFrame,
    start_date: str,
    end_date: str,
    news_data: Optional[pd.DataFrame] = None,
    **kwargs
) -> Dict:
    """
    Convenience function to run 5-day swing trading backtest
    
    Args:
        symbol: Stock ticker
        price_data: Historical OHLCV data
        start_date: Start date
        end_date: End date
        news_data: Optional news DataFrame with sentiment
        **kwargs: Additional parameters for SwingTraderEngine
    
    Returns:
        Backtest results dictionary
    """
    engine = SwingTraderEngine(**kwargs)
    return engine.run_backtest(symbol, price_data, start_date, end_date, news_data)
