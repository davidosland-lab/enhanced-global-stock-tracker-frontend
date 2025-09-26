"""
Technical Analysis Engine for Stock Market Data
Provides comprehensive technical indicators and analysis
Imported from GSMT-Ver-813 project
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import yfinance as yf
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class TrendDirection(Enum):
    STRONG_BULLISH = "strong_bullish"
    BULLISH = "bullish"
    NEUTRAL = "neutral"
    BEARISH = "bearish"
    STRONG_BEARISH = "strong_bearish"

class SignalStrength(Enum):
    STRONG_BUY = "strong_buy"
    BUY = "buy"
    HOLD = "hold"
    SELL = "sell"
    STRONG_SELL = "strong_sell"

@dataclass
class TechnicalSignal:
    """Represents a technical analysis signal"""
    indicator: str
    value: float
    signal: SignalStrength
    confidence: float
    description: str

class TechnicalAnalysisEngine:
    """
    Comprehensive technical analysis engine for stock market data
    Includes RSI, MACD, Bollinger Bands, SMA, EMA, and more
    """
    
    def __init__(self):
        self.indicators = {}
        self.signals = []
        logger.info("📊 Technical Analysis Engine initialized")
    
    def calculate_rsi(self, prices: pd.Series, periods: int = 14) -> Dict[str, Any]:
        """
        Calculate Relative Strength Index (RSI)
        
        Args:
            prices: Series of closing prices
            periods: RSI calculation period (default 14)
            
        Returns:
            Dict containing RSI value and interpretation
        """
        try:
            if len(prices) < periods + 1:
                return {"value": 50.0, "signal": "neutral", "description": "Insufficient data"}
            
            # Calculate price changes
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
            
            # Avoid division by zero
            loss = loss.replace(0, 0.001)
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            current_rsi = float(rsi.iloc[-1])
            
            # Handle NaN/inf values
            if pd.isna(current_rsi) or np.isinf(current_rsi):
                current_rsi = 50.0
            
            # Interpret RSI
            if current_rsi >= 70:
                signal = SignalStrength.SELL
                description = f"Overbought (RSI: {current_rsi:.2f})"
            elif current_rsi <= 30:
                signal = SignalStrength.BUY
                description = f"Oversold (RSI: {current_rsi:.2f})"
            elif current_rsi >= 60:
                signal = SignalStrength.HOLD
                description = f"Moderately bullish (RSI: {current_rsi:.2f})"
            elif current_rsi <= 40:
                signal = SignalStrength.HOLD
                description = f"Moderately bearish (RSI: {current_rsi:.2f})"
            else:
                signal = SignalStrength.HOLD
                description = f"Neutral (RSI: {current_rsi:.2f})"
            
            # Calculate RSI divergence
            rsi_series = rsi.dropna()
            divergence = self._detect_divergence(prices[-len(rsi_series):], rsi_series)
            
            return {
                "value": current_rsi,
                "signal": signal.value,
                "description": description,
                "divergence": divergence,
                "series": rsi.tolist()
            }
            
        except Exception as e:
            logger.error(f"Error calculating RSI: {e}")
            return {"value": 50.0, "signal": "neutral", "description": "Calculation error"}
    
    def calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, Any]:
        """
        Calculate MACD (Moving Average Convergence Divergence)
        
        Args:
            prices: Series of closing prices
            fast: Fast EMA period (default 12)
            slow: Slow EMA period (default 26)
            signal: Signal line EMA period (default 9)
            
        Returns:
            Dict containing MACD values and interpretation
        """
        try:
            if len(prices) < slow + signal:
                return {"macd": 0, "signal": 0, "histogram": 0, "interpretation": "Insufficient data"}
            
            # Calculate EMAs
            ema_fast = prices.ewm(span=fast, adjust=False).mean()
            ema_slow = prices.ewm(span=slow, adjust=False).mean()
            
            # Calculate MACD line
            macd_line = ema_fast - ema_slow
            
            # Calculate signal line
            signal_line = macd_line.ewm(span=signal, adjust=False).mean()
            
            # Calculate histogram
            histogram = macd_line - signal_line
            
            current_macd = float(macd_line.iloc[-1])
            current_signal = float(signal_line.iloc[-1])
            current_histogram = float(histogram.iloc[-1])
            
            # Check for crossovers
            prev_histogram = float(histogram.iloc[-2]) if len(histogram) > 1 else 0
            
            if current_histogram > 0 and prev_histogram <= 0:
                interpretation = SignalStrength.BUY
                description = "MACD bullish crossover"
            elif current_histogram < 0 and prev_histogram >= 0:
                interpretation = SignalStrength.SELL
                description = "MACD bearish crossover"
            elif current_histogram > prev_histogram:
                interpretation = SignalStrength.BUY if current_histogram > 0 else SignalStrength.HOLD
                description = "MACD momentum increasing"
            elif current_histogram < prev_histogram:
                interpretation = SignalStrength.SELL if current_histogram < 0 else SignalStrength.HOLD
                description = "MACD momentum decreasing"
            else:
                interpretation = SignalStrength.HOLD
                description = "MACD neutral"
            
            return {
                "macd": current_macd,
                "signal": current_signal,
                "histogram": current_histogram,
                "interpretation": interpretation.value,
                "description": description,
                "macd_series": macd_line.tolist(),
                "signal_series": signal_line.tolist(),
                "histogram_series": histogram.tolist()
            }
            
        except Exception as e:
            logger.error(f"Error calculating MACD: {e}")
            return {"macd": 0, "signal": 0, "histogram": 0, "interpretation": "error"}
    
    def calculate_bollinger_bands(self, prices: pd.Series, periods: int = 20, std_dev: int = 2) -> Dict[str, Any]:
        """
        Calculate Bollinger Bands
        
        Args:
            prices: Series of closing prices
            periods: SMA period (default 20)
            std_dev: Number of standard deviations (default 2)
            
        Returns:
            Dict containing Bollinger Bands values and position
        """
        try:
            if len(prices) < periods:
                return {"upper": 0, "middle": 0, "lower": 0, "position": 0.5}
            
            # Calculate moving average
            sma = prices.rolling(window=periods).mean()
            
            # Calculate standard deviation
            std = prices.rolling(window=periods).std()
            
            # Calculate bands
            upper_band = sma + (std * std_dev)
            lower_band = sma - (std * std_dev)
            
            current_price = float(prices.iloc[-1])
            current_upper = float(upper_band.iloc[-1])
            current_middle = float(sma.iloc[-1])
            current_lower = float(lower_band.iloc[-1])
            
            # Calculate position within bands (0 = lower, 1 = upper)
            band_width = current_upper - current_lower
            if band_width > 0:
                position = (current_price - current_lower) / band_width
                position = max(0, min(1, position))
            else:
                position = 0.5
            
            # Interpret position
            if position >= 0.95:
                interpretation = SignalStrength.STRONG_SELL
                description = "Price at upper band - overbought"
            elif position >= 0.8:
                interpretation = SignalStrength.SELL
                description = "Price near upper band"
            elif position <= 0.05:
                interpretation = SignalStrength.STRONG_BUY
                description = "Price at lower band - oversold"
            elif position <= 0.2:
                interpretation = SignalStrength.BUY
                description = "Price near lower band"
            else:
                interpretation = SignalStrength.HOLD
                description = f"Price within bands ({position:.1%})"
            
            # Calculate band squeeze (volatility indicator)
            band_width_series = (upper_band - lower_band) / sma
            current_width = float(band_width_series.iloc[-1])
            avg_width = float(band_width_series.mean())
            squeeze = current_width < avg_width * 0.8
            
            return {
                "upper": current_upper,
                "middle": current_middle,
                "lower": current_lower,
                "current_price": current_price,
                "position": position,
                "interpretation": interpretation.value,
                "description": description,
                "squeeze": squeeze,
                "upper_series": upper_band.tolist(),
                "middle_series": sma.tolist(),
                "lower_series": lower_band.tolist()
            }
            
        except Exception as e:
            logger.error(f"Error calculating Bollinger Bands: {e}")
            return {"upper": 0, "middle": 0, "lower": 0, "position": 0.5}
    
    def calculate_moving_averages(self, prices: pd.Series) -> Dict[str, Any]:
        """
        Calculate various moving averages (SMA and EMA)
        
        Args:
            prices: Series of closing prices
            
        Returns:
            Dict containing moving average values and signals
        """
        try:
            current_price = float(prices.iloc[-1])
            ma_signals = []
            
            # Calculate different period MAs
            periods = [10, 20, 50, 100, 200]
            sma_values = {}
            ema_values = {}
            
            for period in periods:
                if len(prices) >= period:
                    sma = prices.rolling(window=period).mean()
                    ema = prices.ewm(span=period, adjust=False).mean()
                    
                    sma_values[f"SMA_{period}"] = float(sma.iloc[-1])
                    ema_values[f"EMA_{period}"] = float(ema.iloc[-1])
                    
                    # Check if price is above/below MA
                    if current_price > sma_values[f"SMA_{period}"]:
                        ma_signals.append(f"Above SMA{period}")
                    else:
                        ma_signals.append(f"Below SMA{period}")
            
            # Golden Cross / Death Cross detection
            cross_signal = None
            if "SMA_50" in sma_values and "SMA_200" in sma_values:
                sma50 = prices.rolling(window=50).mean()
                sma200 = prices.rolling(window=200).mean()
                
                if len(sma50) > 1 and len(sma200) > 1:
                    # Check for crossovers
                    if sma50.iloc[-1] > sma200.iloc[-1] and sma50.iloc[-2] <= sma200.iloc[-2]:
                        cross_signal = "Golden Cross (Bullish)"
                    elif sma50.iloc[-1] < sma200.iloc[-1] and sma50.iloc[-2] >= sma200.iloc[-2]:
                        cross_signal = "Death Cross (Bearish)"
            
            # Overall MA trend
            above_count = sum(1 for s in ma_signals if "Above" in s)
            below_count = sum(1 for s in ma_signals if "Below" in s)
            
            if above_count > below_count * 1.5:
                trend = TrendDirection.BULLISH
            elif below_count > above_count * 1.5:
                trend = TrendDirection.BEARISH
            else:
                trend = TrendDirection.NEUTRAL
            
            return {
                "sma": sma_values,
                "ema": ema_values,
                "signals": ma_signals,
                "cross_signal": cross_signal,
                "trend": trend.value,
                "current_price": current_price
            }
            
        except Exception as e:
            logger.error(f"Error calculating moving averages: {e}")
            return {"sma": {}, "ema": {}, "signals": [], "trend": "neutral"}
    
    def calculate_volume_indicators(self, prices: pd.Series, volumes: pd.Series) -> Dict[str, Any]:
        """
        Calculate volume-based indicators
        
        Args:
            prices: Series of closing prices
            volumes: Series of volumes
            
        Returns:
            Dict containing volume indicators
        """
        try:
            # On-Balance Volume (OBV)
            obv = (np.sign(prices.diff()) * volumes).cumsum()
            current_obv = float(obv.iloc[-1])
            obv_trend = "bullish" if obv.iloc[-1] > obv.iloc[-5:].mean() else "bearish"
            
            # Volume Moving Average
            volume_ma = volumes.rolling(window=20).mean()
            current_volume = float(volumes.iloc[-1])
            avg_volume = float(volume_ma.iloc[-1]) if not pd.isna(volume_ma.iloc[-1]) else current_volume
            
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
            
            # Volume trend
            if volume_ratio > 1.5:
                volume_signal = "High volume - strong conviction"
            elif volume_ratio > 1.2:
                volume_signal = "Above average volume"
            elif volume_ratio < 0.8:
                volume_signal = "Low volume - weak conviction"
            else:
                volume_signal = "Normal volume"
            
            # Money Flow Index (simplified)
            typical_price = (prices + prices.shift(1) + prices.shift(2)) / 3
            money_flow = typical_price * volumes
            positive_flow = money_flow.where(prices.diff() > 0, 0)
            negative_flow = money_flow.where(prices.diff() < 0, 0)
            
            mfi_ratio = positive_flow.rolling(14).sum() / negative_flow.rolling(14).sum()
            mfi = 100 - (100 / (1 + mfi_ratio))
            current_mfi = float(mfi.iloc[-1]) if not pd.isna(mfi.iloc[-1]) else 50
            
            return {
                "obv": current_obv,
                "obv_trend": obv_trend,
                "volume_ratio": volume_ratio,
                "volume_signal": volume_signal,
                "mfi": current_mfi,
                "current_volume": current_volume,
                "avg_volume": avg_volume
            }
            
        except Exception as e:
            logger.error(f"Error calculating volume indicators: {e}")
            return {"obv": 0, "volume_ratio": 1.0, "mfi": 50}
    
    def calculate_momentum_indicators(self, prices: pd.Series) -> Dict[str, Any]:
        """
        Calculate momentum indicators
        
        Args:
            prices: Series of closing prices
            
        Returns:
            Dict containing momentum indicators
        """
        try:
            # Rate of Change (ROC)
            roc_periods = [10, 20]
            roc_values = {}
            
            for period in roc_periods:
                if len(prices) > period:
                    roc = ((prices.iloc[-1] - prices.iloc[-period-1]) / prices.iloc[-period-1]) * 100
                    roc_values[f"ROC_{period}"] = float(roc)
            
            # Stochastic Oscillator
            period = 14
            if len(prices) >= period:
                low_min = prices.rolling(window=period).min()
                high_max = prices.rolling(window=period).max()
                
                k_percent = 100 * ((prices - low_min) / (high_max - low_min))
                d_percent = k_percent.rolling(window=3).mean()
                
                current_k = float(k_percent.iloc[-1]) if not pd.isna(k_percent.iloc[-1]) else 50
                current_d = float(d_percent.iloc[-1]) if not pd.isna(d_percent.iloc[-1]) else 50
                
                # Stochastic interpretation
                if current_k > 80:
                    stoch_signal = "Overbought"
                elif current_k < 20:
                    stoch_signal = "Oversold"
                else:
                    stoch_signal = "Neutral"
            else:
                current_k = 50
                current_d = 50
                stoch_signal = "Insufficient data"
            
            # Williams %R
            if len(prices) >= 14:
                williams_r = -100 * ((high_max.iloc[-1] - prices.iloc[-1]) / (high_max.iloc[-1] - low_min.iloc[-1]))
                williams_r_value = float(williams_r) if not pd.isna(williams_r) else -50
            else:
                williams_r_value = -50
            
            # Overall momentum
            momentum_score = 0
            if roc_values.get("ROC_10", 0) > 0:
                momentum_score += 1
            if roc_values.get("ROC_20", 0) > 0:
                momentum_score += 1
            if current_k > 50:
                momentum_score += 1
            if williams_r_value > -50:
                momentum_score += 1
            
            if momentum_score >= 3:
                momentum_trend = "Strong Positive"
            elif momentum_score >= 2:
                momentum_trend = "Positive"
            elif momentum_score >= 1:
                momentum_trend = "Neutral"
            else:
                momentum_trend = "Negative"
            
            return {
                "roc": roc_values,
                "stochastic_k": current_k,
                "stochastic_d": current_d,
                "stochastic_signal": stoch_signal,
                "williams_r": williams_r_value,
                "momentum_trend": momentum_trend
            }
            
        except Exception as e:
            logger.error(f"Error calculating momentum indicators: {e}")
            return {"roc": {}, "stochastic_k": 50, "stochastic_d": 50, "momentum_trend": "neutral"}
    
    def _detect_divergence(self, prices: pd.Series, indicator: pd.Series) -> str:
        """
        Detect divergence between price and indicator
        
        Args:
            prices: Series of prices
            indicator: Series of indicator values
            
        Returns:
            Divergence type (bullish, bearish, or none)
        """
        try:
            if len(prices) < 10 or len(indicator) < 10:
                return "none"
            
            # Find recent peaks and troughs
            price_highs = prices.rolling(window=5).max() == prices
            price_lows = prices.rolling(window=5).min() == prices
            
            indicator_highs = indicator.rolling(window=5).max() == indicator
            indicator_lows = indicator.rolling(window=5).min() == indicator
            
            # Check for divergence in last 20 periods
            lookback = min(20, len(prices) - 1)
            
            # Bearish divergence: price makes higher high, indicator makes lower high
            if (prices.iloc[-1] > prices.iloc[-lookback:-1].max() and 
                indicator.iloc[-1] < indicator.iloc[-lookback:-1].max()):
                return "bearish_divergence"
            
            # Bullish divergence: price makes lower low, indicator makes higher low
            if (prices.iloc[-1] < prices.iloc[-lookback:-1].min() and 
                indicator.iloc[-1] > indicator.iloc[-lookback:-1].min()):
                return "bullish_divergence"
            
            return "none"
            
        except:
            return "none"
    
    def generate_comprehensive_analysis(self, symbol: str, period: str = "3mo", interval: str = "1d") -> Dict[str, Any]:
        """
        Generate comprehensive technical analysis for a symbol
        
        Args:
            symbol: Stock symbol
            period: Time period for data
            interval: Data interval
            
        Returns:
            Dict containing all technical indicators and overall analysis
        """
        try:
            # Fetch data
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period, interval=interval)
            
            if hist.empty:
                return {"error": "No data available for symbol"}
            
            prices = hist['Close']
            volumes = hist['Volume']
            
            # Calculate all indicators
            rsi = self.calculate_rsi(prices)
            macd = self.calculate_macd(prices)
            bollinger = self.calculate_bollinger_bands(prices)
            moving_averages = self.calculate_moving_averages(prices)
            volume_indicators = self.calculate_volume_indicators(prices, volumes)
            momentum = self.calculate_momentum_indicators(prices)
            
            # Generate overall signal
            signals = []
            
            # RSI signal
            if rsi['value'] <= 30:
                signals.append(TechnicalSignal("RSI", rsi['value'], SignalStrength.BUY, 0.7, rsi['description']))
            elif rsi['value'] >= 70:
                signals.append(TechnicalSignal("RSI", rsi['value'], SignalStrength.SELL, 0.7, rsi['description']))
            
            # MACD signal
            if macd['interpretation'] in ['strong_buy', 'buy']:
                signals.append(TechnicalSignal("MACD", macd['histogram'], SignalStrength.BUY, 0.8, macd['description']))
            elif macd['interpretation'] in ['strong_sell', 'sell']:
                signals.append(TechnicalSignal("MACD", macd['histogram'], SignalStrength.SELL, 0.8, macd['description']))
            
            # Bollinger signal
            if bollinger['position'] <= 0.2:
                signals.append(TechnicalSignal("Bollinger", bollinger['position'], SignalStrength.BUY, 0.6, bollinger['description']))
            elif bollinger['position'] >= 0.8:
                signals.append(TechnicalSignal("Bollinger", bollinger['position'], SignalStrength.SELL, 0.6, bollinger['description']))
            
            # Calculate overall recommendation
            buy_signals = sum(1 for s in signals if s.signal in [SignalStrength.BUY, SignalStrength.STRONG_BUY])
            sell_signals = sum(1 for s in signals if s.signal in [SignalStrength.SELL, SignalStrength.STRONG_SELL])
            
            if buy_signals > sell_signals * 1.5:
                overall_signal = "BUY"
                confidence = buy_signals / len(signals) if signals else 0.5
            elif sell_signals > buy_signals * 1.5:
                overall_signal = "SELL"
                confidence = sell_signals / len(signals) if signals else 0.5
            else:
                overall_signal = "HOLD"
                confidence = 0.5
            
            return {
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "current_price": float(prices.iloc[-1]),
                "indicators": {
                    "rsi": rsi,
                    "macd": macd,
                    "bollinger_bands": bollinger,
                    "moving_averages": moving_averages,
                    "volume": volume_indicators,
                    "momentum": momentum
                },
                "signals": [{"indicator": s.indicator, "signal": s.signal.value, "confidence": s.confidence, "description": s.description} for s in signals],
                "overall_signal": overall_signal,
                "confidence": confidence,
                "price_data": {
                    "open": float(hist['Open'].iloc[-1]),
                    "high": float(hist['High'].iloc[-1]),
                    "low": float(hist['Low'].iloc[-1]),
                    "close": float(hist['Close'].iloc[-1]),
                    "volume": float(hist['Volume'].iloc[-1])
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating comprehensive analysis: {e}")
            return {"error": str(e)}
    
    def get_candlestick_data(self, symbol: str, period: str = "1mo", interval: str = "1d") -> Dict[str, Any]:
        """
        Get candlestick data with technical indicators for charting
        
        Args:
            symbol: Stock symbol
            period: Time period
            interval: Data interval
            
        Returns:
            Dict containing OHLCV data and technical indicators
        """
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period, interval=interval)
            
            if hist.empty:
                return {"error": "No data available"}
            
            # Prepare candlestick data
            candlestick_data = []
            for index, row in hist.iterrows():
                candlestick_data.append({
                    "timestamp": index.isoformat(),
                    "open": float(row['Open']),
                    "high": float(row['High']),
                    "low": float(row['Low']),
                    "close": float(row['Close']),
                    "volume": float(row['Volume'])
                })
            
            # Calculate indicators for overlay
            prices = hist['Close']
            
            # Moving averages
            sma20 = prices.rolling(window=20).mean()
            sma50 = prices.rolling(window=50).mean() if len(prices) >= 50 else None
            ema12 = prices.ewm(span=12, adjust=False).mean()
            ema26 = prices.ewm(span=26, adjust=False).mean()
            
            # Bollinger Bands
            bollinger = self.calculate_bollinger_bands(prices)
            
            # RSI
            rsi = self.calculate_rsi(prices)
            
            # MACD
            macd = self.calculate_macd(prices)
            
            return {
                "symbol": symbol,
                "period": period,
                "interval": interval,
                "data": candlestick_data,
                "indicators": {
                    "sma20": sma20.tolist() if sma20 is not None else [],
                    "sma50": sma50.tolist() if sma50 is not None else [],
                    "ema12": ema12.tolist(),
                    "ema26": ema26.tolist(),
                    "bollinger_upper": bollinger.get("upper_series", []),
                    "bollinger_middle": bollinger.get("middle_series", []),
                    "bollinger_lower": bollinger.get("lower_series", []),
                    "rsi": rsi.get("series", []),
                    "macd": macd.get("macd_series", []),
                    "macd_signal": macd.get("signal_series", []),
                    "macd_histogram": macd.get("histogram_series", [])
                },
                "metadata": {
                    "name": ticker.info.get('longName', symbol),
                    "exchange": ticker.info.get('exchange', 'Unknown'),
                    "currency": ticker.info.get('currency', 'USD'),
                    "last_updated": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting candlestick data: {e}")
            return {"error": str(e)}

# Create singleton instance
technical_engine = TechnicalAnalysisEngine()