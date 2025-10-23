"""
Technical Analysis Library Integration Module
Integrates multiple open-source TA libraries:
- TA-Lib (via talib-python)
- Pandas TA
- Custom pattern recognition
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
import asyncio

# Try importing TA libraries (with fallbacks)
try:
    import talib
    TALIB_AVAILABLE = True
except ImportError:
    TALIB_AVAILABLE = False
    logging.warning("TA-Lib not available. Install with: pip install TA-Lib")

try:
    import pandas_ta as ta
    PANDAS_TA_AVAILABLE = True
except ImportError:
    PANDAS_TA_AVAILABLE = False
    logging.warning("Pandas TA not available. Install with: pip install pandas-ta")

logger = logging.getLogger(__name__)


class EnhancedTechnicalAnalyzer:
    """
    Enhanced technical analysis using multiple open-source libraries
    """
    
    def __init__(self):
        self.talib_available = TALIB_AVAILABLE
        self.pandas_ta_available = PANDAS_TA_AVAILABLE
        
    async def analyze_with_talib(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Perform comprehensive analysis using TA-Lib
        """
        if not self.talib_available:
            return {"error": "TA-Lib not installed"}
        
        try:
            results = {}
            
            # Price data
            high = df['High'].values
            low = df['Low'].values
            close = df['Close'].values
            open_ = df['Open'].values
            volume = df['Volume'].values
            
            # Overlap Studies
            results['sma'] = {
                'sma_10': talib.SMA(close, timeperiod=10).tolist(),
                'sma_20': talib.SMA(close, timeperiod=20).tolist(),
                'sma_50': talib.SMA(close, timeperiod=50).tolist(),
                'sma_200': talib.SMA(close, timeperiod=200).tolist()
            }
            
            results['ema'] = {
                'ema_12': talib.EMA(close, timeperiod=12).tolist(),
                'ema_26': talib.EMA(close, timeperiod=26).tolist(),
                'ema_50': talib.EMA(close, timeperiod=50).tolist()
            }
            
            # Bollinger Bands
            upper, middle, lower = talib.BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2)
            results['bollinger_bands'] = {
                'upper': upper.tolist(),
                'middle': middle.tolist(),
                'lower': lower.tolist()
            }
            
            # Momentum Indicators
            results['rsi'] = {
                'rsi_14': talib.RSI(close, timeperiod=14).tolist(),
                'rsi_21': talib.RSI(close, timeperiod=21).tolist(),
                'rsi_9': talib.RSI(close, timeperiod=9).tolist()
            }
            
            # MACD
            macd, macd_signal, macd_hist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
            results['macd'] = {
                'macd': macd.tolist(),
                'signal': macd_signal.tolist(),
                'histogram': macd_hist.tolist()
            }
            
            # Stochastic
            slowk, slowd = talib.STOCH(high, low, close, 
                                       fastk_period=14, slowk_period=3, 
                                       slowk_matype=0, slowd_period=3, slowd_matype=0)
            results['stochastic'] = {
                'k': slowk.tolist(),
                'd': slowd.tolist()
            }
            
            # ADX - Average Directional Movement Index
            results['adx'] = talib.ADX(high, low, close, timeperiod=14).tolist()
            results['plus_di'] = talib.PLUS_DI(high, low, close, timeperiod=14).tolist()
            results['minus_di'] = talib.MINUS_DI(high, low, close, timeperiod=14).tolist()
            
            # ATR - Average True Range
            results['atr'] = talib.ATR(high, low, close, timeperiod=14).tolist()
            
            # CCI - Commodity Channel Index
            results['cci'] = talib.CCI(high, low, close, timeperiod=20).tolist()
            
            # Williams %R
            results['williams_r'] = talib.WILLR(high, low, close, timeperiod=14).tolist()
            
            # MFI - Money Flow Index
            results['mfi'] = talib.MFI(high, low, close, volume, timeperiod=14).tolist()
            
            # OBV - On Balance Volume
            results['obv'] = talib.OBV(close, volume).tolist()
            
            # ROC - Rate of Change
            results['roc'] = talib.ROC(close, timeperiod=10).tolist()
            
            # Ichimoku Cloud Components
            results['ichimoku'] = self._calculate_ichimoku(df)
            
            # VWAP - Volume Weighted Average Price
            results['vwap'] = self._calculate_vwap(df)
            
            # Parabolic SAR
            results['sar'] = talib.SAR(high, low, acceleration=0.02, maximum=0.2).tolist()
            
            # Candlestick Pattern Recognition
            results['patterns'] = self._detect_candlestick_patterns(open_, high, low, close)
            
            # Calculate current values (last non-NaN values)
            results['current_values'] = {
                'rsi_14': self._get_current_value(results['rsi']['rsi_14']),
                'macd': self._get_current_value(results['macd']['macd']),
                'adx': self._get_current_value(results['adx']),
                'atr': self._get_current_value(results['atr']),
                'cci': self._get_current_value(results['cci']),
                'mfi': self._get_current_value(results['mfi']),
                'williams_r': self._get_current_value(results['williams_r']),
                'stoch_k': self._get_current_value(results['stochastic']['k']),
                'stoch_d': self._get_current_value(results['stochastic']['d'])
            }
            
            # Generate signals
            results['signals'] = self._generate_talib_signals(results)
            
            return results
            
        except Exception as e:
            logger.error(f"TA-Lib analysis error: {str(e)}")
            return {"error": str(e)}
    
    def _detect_candlestick_patterns(self, open_: np.ndarray, high: np.ndarray, 
                                    low: np.ndarray, close: np.ndarray) -> Dict[str, Any]:
        """
        Detect candlestick patterns using TA-Lib
        """
        if not self.talib_available:
            return {}
        
        patterns = {}
        
        # Bullish Patterns
        patterns['hammer'] = talib.CDLHAMMER(open_, high, low, close).tolist()
        patterns['bullish_engulfing'] = talib.CDLENGULFING(open_, high, low, close).tolist()
        patterns['morning_star'] = talib.CDLMORNINGSTAR(open_, high, low, close).tolist()
        patterns['three_white_soldiers'] = talib.CDL3WHITESOLDIERS(open_, high, low, close).tolist()
        patterns['bullish_harami'] = talib.CDLHARAMI(open_, high, low, close).tolist()
        
        # Bearish Patterns
        patterns['hanging_man'] = talib.CDLHANGINGMAN(open_, high, low, close).tolist()
        patterns['shooting_star'] = talib.CDLSHOOTINGSTAR(open_, high, low, close).tolist()
        patterns['evening_star'] = talib.CDLEVENINGSTAR(open_, high, low, close).tolist()
        patterns['three_black_crows'] = talib.CDL3BLACKCROWS(open_, high, low, close).tolist()
        patterns['bearish_harami'] = talib.CDLHARAMI(open_, high, low, close).tolist()
        
        # Neutral/Reversal Patterns
        patterns['doji'] = talib.CDLDOJI(open_, high, low, close).tolist()
        patterns['doji_star'] = talib.CDLDOJISTAR(open_, high, low, close).tolist()
        patterns['spinning_top'] = talib.CDLSPINNINGTOP(open_, high, low, close).tolist()
        patterns['marubozu'] = talib.CDLMARUBOZU(open_, high, low, close).tolist()
        
        # Find active patterns (non-zero values)
        active_patterns = []
        for pattern_name, values in patterns.items():
            if values and len(values) > 0:
                last_value = values[-1] if not np.isnan(values[-1]) else 0
                if last_value != 0:
                    active_patterns.append({
                        'name': pattern_name.replace('_', ' ').title(),
                        'signal': 'bullish' if last_value > 0 else 'bearish',
                        'strength': abs(last_value)
                    })
        
        patterns['active'] = active_patterns
        
        return patterns
    
    async def analyze_with_pandas_ta(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Perform analysis using Pandas TA library
        """
        if not self.pandas_ta_available:
            return {"error": "Pandas TA not installed"}
        
        try:
            results = {}
            
            # Create a copy to avoid modifying original
            df_ta = df.copy()
            
            # Add all available indicators
            df_ta.ta.strategy("All")  # This adds ALL indicators
            
            # Extract key indicators
            indicator_columns = [col for col in df_ta.columns if col not in df.columns]
            
            # Group indicators by type
            results['trend'] = {}
            results['momentum'] = {}
            results['volatility'] = {}
            results['volume'] = {}
            results['others'] = {}
            
            for col in indicator_columns:
                col_lower = col.lower()
                if 'sma' in col_lower or 'ema' in col_lower or 'wma' in col_lower:
                    results['trend'][col] = df_ta[col].tolist()
                elif 'rsi' in col_lower or 'macd' in col_lower or 'stoch' in col_lower:
                    results['momentum'][col] = df_ta[col].tolist()
                elif 'bb' in col_lower or 'atr' in col_lower or 'kc' in col_lower:
                    results['volatility'][col] = df_ta[col].tolist()
                elif 'obv' in col_lower or 'cmf' in col_lower or 'mfi' in col_lower:
                    results['volume'][col] = df_ta[col].tolist()
                else:
                    results['others'][col] = df_ta[col].tolist()
            
            # Custom indicators using Pandas TA
            results['custom'] = {
                'awesome_oscillator': df_ta.ta.ao().tolist() if 'ao' in df_ta.ta.indicators() else None,
                'keltner_channels': self._get_keltner_channels(df_ta),
                'donchian_channels': self._get_donchian_channels(df_ta),
                'fisher_transform': df_ta.ta.fisher().tolist() if 'fisher' in df_ta.ta.indicators() else None,
                'hull_moving_average': df_ta.ta.hma(length=20).tolist() if 'hma' in df_ta.ta.indicators() else None
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Pandas TA analysis error: {str(e)}")
            return {"error": str(e)}
    
    def _calculate_ichimoku(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate Ichimoku Cloud components
        """
        try:
            high = df['High']
            low = df['Low']
            close = df['Close']
            
            # Tenkan-sen (Conversion Line): (9-period high + 9-period low)/2
            period9_high = high.rolling(window=9).max()
            period9_low = low.rolling(window=9).min()
            tenkan_sen = (period9_high + period9_low) / 2
            
            # Kijun-sen (Base Line): (26-period high + 26-period low)/2
            period26_high = high.rolling(window=26).max()
            period26_low = low.rolling(window=26).min()
            kijun_sen = (period26_high + period26_low) / 2
            
            # Senkou Span A (Leading Span A): (Tenkan-sen + Kijun-sen)/2 (26 periods ahead)
            senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(26)
            
            # Senkou Span B (Leading Span B): (52-period high + 52-period low)/2 (26 periods ahead)
            period52_high = high.rolling(window=52).max()
            period52_low = low.rolling(window=52).min()
            senkou_span_b = ((period52_high + period52_low) / 2).shift(26)
            
            # Chikou Span (Lagging Span): Close plotted 26 days in the past
            chikou_span = close.shift(-26)
            
            return {
                'tenkan_sen': tenkan_sen.tolist(),
                'kijun_sen': kijun_sen.tolist(),
                'senkou_span_a': senkou_span_a.tolist(),
                'senkou_span_b': senkou_span_b.tolist(),
                'chikou_span': chikou_span.tolist()
            }
        except Exception as e:
            logger.error(f"Ichimoku calculation error: {str(e)}")
            return {}
    
    def _calculate_vwap(self, df: pd.DataFrame) -> List[float]:
        """
        Calculate Volume Weighted Average Price
        """
        try:
            typical_price = (df['High'] + df['Low'] + df['Close']) / 3
            vwap = (typical_price * df['Volume']).cumsum() / df['Volume'].cumsum()
            return vwap.tolist()
        except Exception as e:
            logger.error(f"VWAP calculation error: {str(e)}")
            return []
    
    def _get_keltner_channels(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get Keltner Channels if available
        """
        try:
            kc_cols = [col for col in df.columns if 'KC' in col.upper()]
            if kc_cols:
                return {col: df[col].tolist() for col in kc_cols}
            return {}
        except:
            return {}
    
    def _get_donchian_channels(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get Donchian Channels if available
        """
        try:
            dc_cols = [col for col in df.columns if 'DC' in col.upper()]
            if dc_cols:
                return {col: df[col].tolist() for col in dc_cols}
            return {}
        except:
            return {}
    
    def _get_current_value(self, series: List) -> Optional[float]:
        """
        Get the last non-NaN value from a series
        """
        if not series:
            return None
        
        for i in range(len(series) - 1, -1, -1):
            if series[i] is not None and not np.isnan(series[i]):
                return float(series[i])
        return None
    
    def _generate_talib_signals(self, indicators: Dict) -> Dict[str, Any]:
        """
        Generate trading signals based on TA-Lib indicators
        """
        signals = {
            'overall': 'NEUTRAL',
            'trend': 'NEUTRAL',
            'momentum': 'NEUTRAL',
            'volume': 'NEUTRAL',
            'strength': 0,
            'components': []
        }
        
        buy_signals = 0
        sell_signals = 0
        
        # RSI Signal
        rsi_value = indicators.get('current_values', {}).get('rsi_14')
        if rsi_value:
            if rsi_value < 30:
                buy_signals += 2
                signals['components'].append({'indicator': 'RSI', 'signal': 'BUY', 'value': rsi_value})
            elif rsi_value > 70:
                sell_signals += 2
                signals['components'].append({'indicator': 'RSI', 'signal': 'SELL', 'value': rsi_value})
            else:
                signals['components'].append({'indicator': 'RSI', 'signal': 'NEUTRAL', 'value': rsi_value})
        
        # MACD Signal
        macd_value = indicators.get('current_values', {}).get('macd')
        if macd_value:
            if macd_value > 0:
                buy_signals += 1
                signals['components'].append({'indicator': 'MACD', 'signal': 'BUY', 'value': macd_value})
            else:
                sell_signals += 1
                signals['components'].append({'indicator': 'MACD', 'signal': 'SELL', 'value': macd_value})
        
        # ADX Trend Strength
        adx_value = indicators.get('current_values', {}).get('adx')
        if adx_value:
            if adx_value > 25:
                signals['trend'] = 'STRONG'
            else:
                signals['trend'] = 'WEAK'
            signals['components'].append({'indicator': 'ADX', 'signal': 'TREND', 'value': adx_value})
        
        # Stochastic Signal
        stoch_k = indicators.get('current_values', {}).get('stoch_k')
        stoch_d = indicators.get('current_values', {}).get('stoch_d')
        if stoch_k and stoch_d:
            if stoch_k < 20 and stoch_d < 20:
                buy_signals += 1
                signals['components'].append({'indicator': 'Stochastic', 'signal': 'BUY', 'value': stoch_k})
            elif stoch_k > 80 and stoch_d > 80:
                sell_signals += 1
                signals['components'].append({'indicator': 'Stochastic', 'signal': 'SELL', 'value': stoch_k})
        
        # MFI Signal
        mfi_value = indicators.get('current_values', {}).get('mfi')
        if mfi_value:
            if mfi_value < 20:
                buy_signals += 1
                signals['components'].append({'indicator': 'MFI', 'signal': 'BUY', 'value': mfi_value})
            elif mfi_value > 80:
                sell_signals += 1
                signals['components'].append({'indicator': 'MFI', 'signal': 'SELL', 'value': mfi_value})
        
        # Overall Signal
        total_signals = buy_signals + sell_signals
        if total_signals > 0:
            if buy_signals > sell_signals * 1.5:
                signals['overall'] = 'STRONG BUY'
                signals['strength'] = min(100, (buy_signals / total_signals) * 100)
            elif buy_signals > sell_signals:
                signals['overall'] = 'BUY'
                signals['strength'] = min(100, (buy_signals / total_signals) * 80)
            elif sell_signals > buy_signals * 1.5:
                signals['overall'] = 'STRONG SELL'
                signals['strength'] = min(100, (sell_signals / total_signals) * 100)
            elif sell_signals > buy_signals:
                signals['overall'] = 'SELL'
                signals['strength'] = min(100, (sell_signals / total_signals) * 80)
            else:
                signals['overall'] = 'NEUTRAL'
                signals['strength'] = 50
        
        return signals
    
    def detect_chart_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Detect chart patterns (Head & Shoulders, Triangles, Flags, etc.)
        This is a simplified implementation - real pattern detection is complex
        """
        patterns = {
            'detected': [],
            'potential': []
        }
        
        try:
            high = df['High'].values
            low = df['Low'].values
            close = df['Close'].values
            
            # Simple pattern detection logic (placeholder)
            # In reality, this would use sophisticated algorithms
            
            # Head and Shoulders detection (simplified)
            if len(close) >= 50:
                # Look for potential head and shoulders pattern
                mid = len(close) // 2
                left_shoulder = np.max(high[mid-25:mid-15])
                head = np.max(high[mid-10:mid+10])
                right_shoulder = np.max(high[mid+15:mid+25])
                
                if head > left_shoulder and head > right_shoulder:
                    if abs(left_shoulder - right_shoulder) / left_shoulder < 0.05:
                        patterns['detected'].append({
                            'name': 'Head and Shoulders',
                            'type': 'reversal',
                            'signal': 'bearish',
                            'confidence': 0.7
                        })
            
            # Triangle pattern detection (simplified)
            if len(close) >= 20:
                recent_highs = high[-20:]
                recent_lows = low[-20:]
                
                # Check for converging highs and lows
                high_trend = np.polyfit(range(len(recent_highs)), recent_highs, 1)[0]
                low_trend = np.polyfit(range(len(recent_lows)), recent_lows, 1)[0]
                
                if abs(high_trend) < abs(low_trend):
                    patterns['potential'].append({
                        'name': 'Ascending Triangle',
                        'type': 'continuation',
                        'signal': 'bullish',
                        'confidence': 0.6
                    })
                elif abs(low_trend) < abs(high_trend):
                    patterns['potential'].append({
                        'name': 'Descending Triangle',
                        'type': 'continuation',
                        'signal': 'bearish',
                        'confidence': 0.6
                    })
            
            # Flag pattern detection (simplified)
            if len(close) >= 30:
                # Look for strong move followed by consolidation
                initial_move = close[-30:-20]
                consolidation = close[-20:-10]
                
                move_range = np.max(initial_move) - np.min(initial_move)
                consol_range = np.max(consolidation) - np.min(consolidation)
                
                if consol_range < move_range * 0.5:
                    if initial_move[-1] > initial_move[0]:
                        patterns['potential'].append({
                            'name': 'Bull Flag',
                            'type': 'continuation',
                            'signal': 'bullish',
                            'confidence': 0.65
                        })
                    else:
                        patterns['potential'].append({
                            'name': 'Bear Flag',
                            'type': 'continuation',
                            'signal': 'bearish',
                            'confidence': 0.65
                        })
            
            # Double Top/Bottom detection (simplified)
            if len(close) >= 40:
                peaks = []
                troughs = []
                
                for i in range(10, len(close) - 10):
                    if high[i] == max(high[i-10:i+10]):
                        peaks.append((i, high[i]))
                    if low[i] == min(low[i-10:i+10]):
                        troughs.append((i, low[i]))
                
                # Check for double top
                if len(peaks) >= 2:
                    last_two_peaks = peaks[-2:]
                    if abs(last_two_peaks[0][1] - last_two_peaks[1][1]) / last_two_peaks[0][1] < 0.03:
                        patterns['detected'].append({
                            'name': 'Double Top',
                            'type': 'reversal',
                            'signal': 'bearish',
                            'confidence': 0.75
                        })
                
                # Check for double bottom
                if len(troughs) >= 2:
                    last_two_troughs = troughs[-2:]
                    if abs(last_two_troughs[0][1] - last_two_troughs[1][1]) / last_two_troughs[0][1] < 0.03:
                        patterns['detected'].append({
                            'name': 'Double Bottom',
                            'type': 'reversal',
                            'signal': 'bullish',
                            'confidence': 0.75
                        })
            
        except Exception as e:
            logger.error(f"Pattern detection error: {str(e)}")
        
        return patterns


# Export the analyzer class
analyzer = EnhancedTechnicalAnalyzer()