"""
Backtesting Prediction Engine
==============================

Generates predictions using walk-forward validation with NO look-ahead bias.

Key Features:
- Three prediction methods: LSTM, Technical, Ensemble
- Walk-forward validation (no future data leakage)
- Confidence scoring
- Configurable lookback periods
- Prediction frequency control (daily, weekly, monthly)

CRITICAL: All predictions use ONLY data available BEFORE the prediction timestamp.

Author: FinBERT v4.0
Date: November 2025
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)


class BacktestPredictionEngine:
    """
    Generates predictions for backtesting with walk-forward validation
    
    CRITICAL: This engine ensures NO LOOK-AHEAD BIAS by only using
    historical data available at the time of each prediction.
    """
    
    def __init__(
        self,
        model_type: str = 'ensemble',
        confidence_threshold: float = 0.6
    ):
        """
        Initialize prediction engine
        
        Args:
            model_type: 'lstm', 'technical', or 'ensemble'
            confidence_threshold: Minimum confidence for signals (0-1)
        """
        self.model_type = model_type.lower()
        self.confidence_threshold = confidence_threshold
        
        logger.info(
            f"Prediction engine initialized (model={model_type}, "
            f"threshold={confidence_threshold})"
        )
    
    def predict_at_timestamp(
        self,
        timestamp: datetime,
        historical_data: pd.DataFrame,
        lookback_days: int = 60
    ) -> Dict:
        """
        Generate prediction using only data available up to timestamp
        
        CRITICAL: This method ensures no look-ahead bias by only using
        data that existed BEFORE the prediction timestamp.
        
        Args:
            timestamp: Prediction timestamp
            historical_data: Complete historical data (will be sliced)
            lookback_days: Number of days to use for training
        
        Returns:
            Dictionary with prediction, confidence, and metadata
        """
        try:
            # CRITICAL: Only use data BEFORE timestamp (no look-ahead bias)
            available_data = historical_data[historical_data.index < timestamp]
            
            if len(available_data) < lookback_days:
                logger.warning(
                    f"Insufficient data at {timestamp}: {len(available_data)} days "
                    f"(need {lookback_days})"
                )
                return {
                    'timestamp': timestamp,
                    'prediction': 'HOLD',
                    'confidence': 0.0,
                    'reason': 'Insufficient historical data',
                    'data_points_used': len(available_data)
                }
            
            # Get training window (last lookback_days)
            training_window = available_data.tail(lookback_days)
            
            # Current price (last available price before prediction)
            current_price = training_window['Close'].iloc[-1]
            
            # Generate prediction based on model type
            if self.model_type == 'lstm':
                prediction = self._predict_lstm(training_window, current_price)
            elif self.model_type == 'technical':
                prediction = self._predict_technical(training_window, current_price)
            elif self.model_type == 'momentum':
                prediction = self._predict_momentum(training_window, current_price)
            else:  # ensemble
                prediction = self._predict_ensemble(training_window, current_price)
            
            # Add metadata
            prediction['timestamp'] = timestamp
            prediction['current_price'] = current_price
            prediction['data_points_used'] = len(training_window)
            prediction['model_type'] = self.model_type
            
            # Apply confidence threshold
            if prediction['confidence'] < self.confidence_threshold:
                prediction['original_prediction'] = prediction['prediction']
                prediction['prediction'] = 'HOLD'
                prediction['reason'] = f"Confidence below threshold ({self.confidence_threshold})"
            
            return prediction
            
        except Exception as e:
            logger.error(f"Error generating prediction at {timestamp}: {e}")
            return {
                'timestamp': timestamp,
                'prediction': 'HOLD',
                'confidence': 0.0,
                'error': str(e)
            }
    
    def _predict_technical(
        self,
        training_window: pd.DataFrame,
        current_price: float
    ) -> Dict:
        """
        Generate Technical Analysis-based prediction
        
        Uses RSI, MACD, Bollinger Bands, and moving averages.
        
        Args:
            training_window: Historical price data
            current_price: Current price
        
        Returns:
            Prediction dictionary
        """
        try:
            prices = training_window['Close'].values
            returns = training_window['Close'].pct_change().dropna()
            
            # RSI Calculation
            delta = pd.Series(prices).diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1] if len(rsi) > 0 else 50
            
            # Moving Averages
            sma_20 = prices[-20:].mean() if len(prices) >= 20 else prices.mean()
            sma_50 = prices[-50:].mean() if len(prices) >= 50 else prices.mean()
            ema_12 = pd.Series(prices).ewm(span=12).mean().iloc[-1]
            ema_26 = pd.Series(prices).ewm(span=26).mean().iloc[-1]
            
            # MACD
            macd = ema_12 - ema_26
            signal = pd.Series([macd]).ewm(span=9).mean().iloc[0]
            macd_histogram = macd - signal
            
            # Bollinger Bands
            bb_sma = prices[-20:].mean() if len(prices) >= 20 else prices.mean()
            bb_std = pd.Series(prices[-20:]).std() if len(prices) >= 20 else pd.Series(prices).std()
            upper_band = bb_sma + (bb_std * 2)
            lower_band = bb_sma - (bb_std * 2)
            bb_position = (current_price - lower_band) / (upper_band - lower_band) if upper_band != lower_band else 0.5
            
            # Volatility
            volatility = returns.std() if len(returns) > 0 else 0
            volatility_factor = 1.0 / (1.0 + volatility * 8)
            
            # Scoring system
            score = 0
            
            # RSI signals
            if current_rsi < 30:
                score += 0.3  # Oversold - bullish
            elif current_rsi > 70:
                score -= 0.3  # Overbought - bearish
            
            # Moving average signals
            if current_price > sma_20 and sma_20 > sma_50:
                score += 0.25  # Bullish trend
            elif current_price < sma_20 and sma_20 < sma_50:
                score -= 0.25  # Bearish trend
            
            # MACD signals
            if macd_histogram > 0:
                score += 0.2  # Bullish momentum
            elif macd_histogram < 0:
                score -= 0.2  # Bearish momentum
            
            # Bollinger Band signals
            if bb_position < 0.2:
                score += 0.25  # Near lower band - potential bounce
            elif bb_position > 0.8:
                score -= 0.25  # Near upper band - potential reversal
            
            # Generate prediction
            if score > 0.3:
                prediction = 'BUY'
                confidence = min(0.55 + abs(score) * 0.3, 0.85) * volatility_factor
            elif score < -0.3:
                prediction = 'SELL'
                confidence = min(0.55 + abs(score) * 0.3, 0.85) * volatility_factor
            else:
                prediction = 'HOLD'
                confidence = 0.5 * volatility_factor
            
            return {
                'prediction': prediction,
                'confidence': confidence,
                'technical_score': score,
                'rsi': current_rsi,
                'macd': macd,
                'macd_signal': signal,
                'bb_position': bb_position,
                'sma_20': sma_20,
                'sma_50': sma_50,
                'volatility': volatility
            }
            
        except Exception as e:
            logger.error(f"Error in Technical prediction: {e}")
            return {'prediction': 'HOLD', 'confidence': 0.0, 'error': str(e)}
    
    def _predict_lstm(
        self,
        training_window: pd.DataFrame,
        current_price: float
    ) -> Dict:
        """
        Generate LSTM-based prediction
        
        Uses price sequences and technical indicators to predict future direction.
        
        Args:
            training_window: Historical price data
            current_price: Current price
        
        Returns:
            Prediction dictionary
        """
        try:
            # Prepare price sequence
            prices = training_window['Close'].values
            
            # Normalize prices (z-score)
            prices_norm = (prices - prices.mean()) / prices.std()
            
            # Calculate technical features
            returns = np.diff(prices) / prices[:-1]
            
            # Moving averages
            sma_20 = prices[-20:].mean() if len(prices) >= 20 else prices.mean()
            sma_50 = prices[-50:].mean() if len(prices) >= 50 else prices.mean()
            
            # Price position relative to moving averages
            price_vs_sma20 = (current_price - sma_20) / sma_20
            price_vs_sma50 = (current_price - sma_50) / sma_50
            
            # Momentum indicators
            recent_momentum = returns[-5:].mean() if len(returns) >= 5 else 0
            medium_momentum = returns[-20:].mean() if len(returns) >= 20 else 0
            
            # Volatility
            volatility = returns.std() if len(returns) > 0 else 0
            
            # Simple LSTM-like prediction (pattern matching)
            # Check if recent price action suggests continuation or reversal
            
            # Trend continuation signal
            trend_signal = 0
            if price_vs_sma20 > 0.02 and price_vs_sma50 > 0.02:
                trend_signal = 1  # Bullish
            elif price_vs_sma20 < -0.02 and price_vs_sma50 < -0.02:
                trend_signal = -1  # Bearish
            
            # Momentum signal
            momentum_signal = 0
            if recent_momentum > 0.01 and medium_momentum > 0.005:
                momentum_signal = 1
            elif recent_momentum < -0.01 and medium_momentum < -0.005:
                momentum_signal = -1
            
            # Combined signal
            combined_signal = (trend_signal * 0.6 + momentum_signal * 0.4)
            
            # Volatility adjustment
            volatility_factor = 1.0 / (1.0 + volatility * 8)
            
            # Generate prediction
            if combined_signal > 0.3:
                prediction = 'BUY'
                confidence = min(0.55 + combined_signal * 0.25, 0.85) * volatility_factor
            elif combined_signal < -0.3:
                prediction = 'SELL'
                confidence = min(0.55 + abs(combined_signal) * 0.25, 0.85) * volatility_factor
            else:
                prediction = 'HOLD'
                confidence = 0.5 * volatility_factor
            
            return {
                'prediction': prediction,
                'confidence': confidence,
                'trend_signal': trend_signal,
                'momentum_signal': momentum_signal,
                'combined_signal': combined_signal,
                'volatility': volatility
            }
            
        except Exception as e:
            logger.error(f"Error in LSTM prediction: {e}")
            return {'prediction': 'HOLD', 'confidence': 0.0, 'error': str(e)}
    
    def _predict_momentum(
        self,
        training_window: pd.DataFrame,
        current_price: float
    ) -> Dict:
        """
        Generate Momentum-based prediction
        
        Uses price momentum, trend strength, and rate of change.
        
        Args:
            training_window: Historical price data
            current_price: Current price
        
        Returns:
            Prediction dictionary
        """
        try:
            prices = training_window['Close'].values
            returns = training_window['Close'].pct_change().dropna()
            
            # Short-term momentum (5 days)
            recent_return = returns.tail(5).mean()
            
            # Medium-term momentum (20 days)
            medium_return = returns.tail(20).mean()
            
            # Long-term momentum (60 days)
            long_return = returns.mean()
            
            # Rate of Change (ROC)
            roc_10 = (current_price - prices[-10]) / prices[-10] if len(prices) > 10 else 0
            roc_20 = (current_price - prices[-20]) / prices[-20] if len(prices) > 20 else 0
            
            # Trend strength (linear regression slope)
            days = np.arange(len(training_window))
            trend_slope = np.polyfit(days, prices, 1)[0]
            trend_strength = trend_slope / current_price  # Normalized
            
            # Acceleration (second derivative)
            if len(returns) > 1:
                acceleration = returns.diff().tail(10).mean()
            else:
                acceleration = 0
            
            # Volatility
            volatility = returns.std() if len(returns) > 0 else 0
            volatility_factor = 1.0 / (1.0 + volatility * 10)
            
            # Momentum score (combining all factors)
            momentum_score = (
                recent_return * 0.35 +
                medium_return * 0.25 +
                trend_strength * 0.20 +
                roc_20 * 0.15 +
                acceleration * 0.05
            )
            
            # Clip score
            momentum_score = np.clip(momentum_score, -1, 1)
            
            # Generate prediction with more sensitive thresholds
            # Lower thresholds to generate more actionable signals
            if momentum_score > 0.003:  # 0.3% threshold (was 25%)
                prediction = 'BUY'
                confidence = min(0.5 + abs(momentum_score) * 15, 0.85) * volatility_factor
            elif momentum_score < -0.003:  # -0.3% threshold (was -25%)
                prediction = 'SELL'
                confidence = min(0.5 + abs(momentum_score) * 15, 0.85) * volatility_factor
            else:
                prediction = 'HOLD'
                confidence = 0.5 * volatility_factor
            
            return {
                'prediction': prediction,
                'confidence': confidence,
                'momentum_score': momentum_score,
                'recent_return': recent_return,
                'medium_return': medium_return,
                'trend_strength': trend_strength,
                'roc_20': roc_20,
                'acceleration': acceleration,
                'volatility': volatility
            }
            
        except Exception as e:
            logger.error(f"Error in Momentum prediction: {e}")
            return {'prediction': 'HOLD', 'confidence': 0.0, 'error': str(e)}
    
    def _predict_ensemble(
        self,
        training_window: pd.DataFrame,
        current_price: float
    ) -> Dict:
        """
        Generate ensemble prediction (combines LSTM + Technical + Momentum)
        
        New improved ensemble without synthetic FinBERT.
        Uses three complementary approaches:
        - LSTM: Pattern recognition and trend continuation
        - Technical: Classical technical indicators (RSI, MACD, BB)
        - Momentum: Price momentum and rate of change
        
        Args:
            training_window: Historical price data
            current_price: Current price
        
        Returns:
            Prediction dictionary
        """
        try:
            # Get predictions from all three models
            lstm_pred = self._predict_lstm(training_window, current_price)
            technical_pred = self._predict_technical(training_window, current_price)
            momentum_pred = self._predict_momentum(training_window, current_price)
            
            # Weighted voting (LSTM: 40%, Technical: 35%, Momentum: 25%)
            lstm_weight = 0.40
            technical_weight = 0.35
            momentum_weight = 0.25
            
            # Convert predictions to scores
            pred_to_score = {'BUY': 1, 'HOLD': 0, 'SELL': -1}
            
            lstm_score = pred_to_score[lstm_pred['prediction']] * lstm_pred['confidence']
            technical_score = pred_to_score[technical_pred['prediction']] * technical_pred['confidence']
            momentum_score = pred_to_score[momentum_pred['prediction']] * momentum_pred['confidence']
            
            # Weighted ensemble score
            ensemble_score = (
                lstm_score * lstm_weight +
                technical_score * technical_weight +
                momentum_score * momentum_weight
            )
            
            # Combined confidence (weighted average)
            ensemble_confidence = (
                lstm_pred['confidence'] * lstm_weight +
                technical_pred['confidence'] * technical_weight +
                momentum_pred['confidence'] * momentum_weight
            )
            
            # Consensus bonus (all three agree = higher confidence)
            all_predictions = [
                lstm_pred['prediction'],
                technical_pred['prediction'],
                momentum_pred['prediction']
            ]
            
            if len(set(all_predictions)) == 1 and all_predictions[0] != 'HOLD':
                # All three agree on BUY or SELL
                ensemble_confidence = min(ensemble_confidence * 1.15, 0.9)
                ensemble_score *= 1.1
            
            # Generate final prediction
            if ensemble_score > 0.15:
                prediction = 'BUY'
            elif ensemble_score < -0.15:
                prediction = 'SELL'
            else:
                prediction = 'HOLD'
            
            return {
                'prediction': prediction,
                'confidence': ensemble_confidence,
                'ensemble_score': ensemble_score,
                'lstm': lstm_pred,
                'technical': technical_pred,
                'momentum': momentum_pred,
                'consensus': len(set(all_predictions)) == 1
            }
            
        except Exception as e:
            logger.error(f"Error in ensemble prediction: {e}")
            return {'prediction': 'HOLD', 'confidence': 0.0, 'error': str(e)}
    
    def walk_forward_backtest(
        self,
        data: pd.DataFrame,
        start_date: str,
        end_date: str,
        prediction_frequency: str = 'daily',
        lookback_days: int = 60
    ) -> pd.DataFrame:
        """
        Perform walk-forward backtesting across date range
        
        Args:
            data: Complete historical data
            start_date: Backtest start date (YYYY-MM-DD)
            end_date: Backtest end date (YYYY-MM-DD)
            prediction_frequency: 'daily', 'weekly', or 'monthly'
            lookback_days: Days of history to use for each prediction
        
        Returns:
            DataFrame with predictions and metadata
        """
        logger.info(
            f"Starting walk-forward backtest from {start_date} to {end_date} "
            f"(frequency={prediction_frequency})"
        )
        
        try:
            # Convert dates and normalize timezone
            start_dt = pd.to_datetime(start_date)
            end_dt = pd.to_datetime(end_date)
            
            # Remove timezone from data index if present
            data_copy = data.copy()
            if data_copy.index.tz is not None:
                data_copy.index = data_copy.index.tz_localize(None)
            
            # Filter data to backtest period
            backtest_data = data_copy[(data_copy.index >= start_dt) & (data_copy.index <= end_dt)]
            
            if backtest_data.empty:
                logger.error("No data in backtest period")
                return pd.DataFrame()
            
            # Generate prediction dates based on frequency
            if prediction_frequency == 'daily':
                prediction_dates = backtest_data.index
            elif prediction_frequency == 'weekly':
                prediction_dates = backtest_data.resample('W').last().index
            elif prediction_frequency == 'monthly':
                prediction_dates = backtest_data.resample('M').last().index
            else:
                raise ValueError(f"Invalid frequency: {prediction_frequency}")
            
            # Generate predictions for each timestamp
            predictions = []
            total_dates = len(prediction_dates)
            
            for i, timestamp in enumerate(prediction_dates):
                if (i + 1) % 50 == 0:
                    logger.info(f"Processing {i+1}/{total_dates} predictions...")
                
                # Generate prediction
                prediction = self.predict_at_timestamp(
                    timestamp=timestamp,
                    historical_data=data_copy,  # Pass timezone-normalized data
                    lookback_days=lookback_days
                )
                
                # Add actual price (for later evaluation)
                if timestamp in data_copy.index:
                    prediction['actual_price'] = data_copy.loc[timestamp, 'Close']
                    
                    # Also get next day's price (if available) for forward return
                    future_dates = data_copy.index[data_copy.index > timestamp]
                    if len(future_dates) > 0:
                        next_date = future_dates[0]
                        prediction['next_price'] = data_copy.loc[next_date, 'Close']
                        prediction['forward_return'] = (
                            (prediction['next_price'] - prediction['actual_price']) /
                            prediction['actual_price']
                        )
                
                predictions.append(prediction)
            
            # Convert to DataFrame
            results_df = pd.DataFrame(predictions)
            
            logger.info(
                f"Backtest complete: {len(results_df)} predictions generated"
            )
            
            return results_df
            
        except Exception as e:
            logger.error(f"Error in walk-forward backtest: {e}")
            return pd.DataFrame()
    
    def evaluate_predictions(self, predictions_df: pd.DataFrame) -> Dict:
        """
        Evaluate prediction accuracy
        
        Args:
            predictions_df: DataFrame with predictions and forward returns
        
        Returns:
            Dictionary with evaluation metrics
        """
        try:
            if predictions_df.empty or 'forward_return' not in predictions_df.columns:
                return {'error': 'Insufficient data for evaluation'}
            
            # Filter valid predictions
            valid_preds = predictions_df[
                (predictions_df['prediction'] != 'HOLD') &
                (predictions_df['forward_return'].notna())
            ].copy()
            
            if len(valid_preds) == 0:
                return {'error': 'No valid predictions to evaluate'}
            
            # Calculate accuracy
            valid_preds['correct'] = (
                ((valid_preds['prediction'] == 'BUY') & (valid_preds['forward_return'] > 0)) |
                ((valid_preds['prediction'] == 'SELL') & (valid_preds['forward_return'] < 0))
            )
            
            accuracy = valid_preds['correct'].mean()
            
            # Buy/Sell accuracy
            buy_preds = valid_preds[valid_preds['prediction'] == 'BUY']
            sell_preds = valid_preds[valid_preds['prediction'] == 'SELL']
            
            buy_accuracy = buy_preds['correct'].mean() if len(buy_preds) > 0 else 0
            sell_accuracy = sell_preds['correct'].mean() if len(sell_preds) > 0 else 0
            
            # Average returns
            buy_returns = buy_preds['forward_return'].mean() if len(buy_preds) > 0 else 0
            sell_returns = sell_preds['forward_return'].mean() if len(sell_preds) > 0 else 0
            
            return {
                'total_predictions': len(predictions_df),
                'actionable_predictions': len(valid_preds),
                'buy_signals': len(buy_preds),
                'sell_signals': len(sell_preds),
                'overall_accuracy': accuracy,
                'buy_accuracy': buy_accuracy,
                'sell_accuracy': sell_accuracy,
                'avg_buy_return': buy_returns,
                'avg_sell_return': sell_returns,
                'avg_confidence': valid_preds['confidence'].mean()
            }
            
        except Exception as e:
            logger.error(f"Error evaluating predictions: {e}")
            return {'error': str(e)}
