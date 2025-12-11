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
        confidence_threshold: float = 0.52,  # Lowered from 0.65 - was too conservative!
        max_position_size: float = 0.25,
        use_real_sentiment: bool = True,
        use_lstm: bool = True,
        sentiment_lookback_days: int = 3,
        lstm_sequence_length: int = 60,
        lstm_epochs: int = 50
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
        
        # Model weights
        self.sentiment_weight = sentiment_weight
        self.lstm_weight = lstm_weight
        self.technical_weight = technical_weight
        self.momentum_weight = momentum_weight
        self.volume_weight = volume_weight
        
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
            f"Swing trader initialized: {holding_period_days}-day hold, "
            f"sentiment={use_real_sentiment}, LSTM={self.use_lstm}, threshold={confidence_threshold}"
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
        Run complete swing trading backtest
        
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
            
            # Step 1: Check existing positions for exits
            self._check_position_exits(current_date, current_price, backtest_data)
            
            # Step 2: Generate entry signal if no position
            if len(self.positions) == 0:
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
                        signal=signal
                    )
            
            # Step 4: Track equity
            position_value = sum(p['shares'] * current_price for p in self.positions)
            total_equity = self.capital + position_value
            self.equity_curve.append({
                'date': current_date,
                'equity': total_equity,
                'cash': self.capital,
                'position_value': position_value
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
    
    def _enter_position(self, date: datetime, price: float, signal: Dict):
        """Enter a new swing trading position"""
        # Calculate position size
        position_value = self.capital * self.max_position_size
        shares = int(position_value / price)
        
        if shares == 0:
            logger.warning(f"Cannot enter position: insufficient capital")
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
        
        # Calculate target exit date (N days later)
        target_exit_date = date + timedelta(days=self.holding_period_days)
        
        # Create position
        position = {
            'entry_date': date,
            'entry_price': price,
            'shares': shares,
            'cost_basis': actual_cost,
            'commission_paid': commission,
            'stop_loss_price': stop_loss_price,
            'target_exit_date': target_exit_date,
            'signal': signal,
            'days_held': 0
        }
        
        # Update capital
        self.capital -= total_cost
        self.positions.append(position)
        
        logger.info(
            f"ENTER: {shares} shares @ ${price:.2f} on {date.date()}, "
            f"stop=${stop_loss_price:.2f}, exit_target={target_exit_date.date()}, "
            f"confidence={signal['confidence']:.2%}"
        )
    
    def _check_position_exits(self, current_date: datetime, current_price: float, price_data: pd.DataFrame):
        """Check if positions should be exited"""
        for position in self.positions[:]:  # Copy list to modify during iteration
            position['days_held'] += 1
            
            # Get intraday low for stop loss check
            if current_date in price_data.index:
                intraday_low = price_data.loc[current_date, 'Low']
            else:
                intraday_low = current_price
            
            # Exit reason
            exit_reason = None
            exit_price = current_price
            
            # Check 1: Stop loss hit
            if intraday_low <= position['stop_loss_price']:
                exit_reason = 'STOP_LOSS'
                exit_price = position['stop_loss_price']
            
            # Check 2: Holding period complete
            elif current_date >= position['target_exit_date']:
                exit_reason = 'TARGET_EXIT'
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
