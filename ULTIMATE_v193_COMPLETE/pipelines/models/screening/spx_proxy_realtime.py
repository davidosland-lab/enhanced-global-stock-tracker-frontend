"""
S&P 500 Pre-Market Prediction Module - REALTIME FUTURES & ASIAN DATA VERSION

This module provides pre-market US market gap predictions using FUTURES and ASIAN market data.

Designed to run BEFORE US market open (before 9:30 AM EST) to predict the opening gap.

⚠️ KEY DIFFERENCE FROM UK/AU:
- US market opens FIRST among major markets
- Cannot use US closes to predict (like UK/AU do)
- Must use FUTURES and ASIAN markets instead

Data Sources (in priority order):
1. US Futures Pre-Market:
   - S&P 500 Futures (ES=F) - Weight: 50%
   - NASDAQ Futures (NQ=F) - Weight: 30%
   - Dow Futures (YM=F) - Weight: 20%

2. Asian Market Closes:
   - Nikkei 225 (^N225) - Weight: 50%
   - Hang Seng (^HSI) - Weight: 30%
   - Shanghai Composite (000001.SS) - Weight: 20%

3. Commodities Overnight:
   - Brent Crude (BZ=F) - Weight: 40%
   - Gold (GC=F) - Weight: 30%
   - US Dollar Index (DX=F) - Weight: 30%

4. European Pre-Market:
   - DAX Futures (FDAX=F) - Weight: 60%
   - Euro Stoxx 50 Futures (FESX=F) - Weight: 40%

5. Market Fear:
   - VIX Futures (VX=F) - Used for confidence adjustment

Version: 1.0.0 - REALTIME
Date: 2026-03-09
Author: AI Trading System
"""

import logging
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from yahooquery import Ticker
import pytz

logger = logging.getLogger(__name__)


class RealtimeSPXPredictor:
    """
    Predicts US market opening gap using futures and Asian market data.
    
    This predictor is specifically designed for pre-market analysis of US markets
    and uses futures data + Asian closes instead of US closes (which don't exist yet).
    """
    
    def __init__(self):
        self.timezone_us = pytz.timezone('US/Eastern')
        self.timezone_tokyo = pytz.timezone('Asia/Tokyo')
        self.timezone_hk = pytz.timezone('Asia/Hong_Kong')
        self.timezone_shanghai = pytz.timezone('Asia/Shanghai')
        
        # Base correlation (US futures are highly predictive)
        self.base_correlation = 0.85
        
        # US Futures Weights (most important for US gap prediction)
        self.us_futures_weights = {
            'SP500': 0.50,   # ES=F - Strongest predictor
            'Nasdaq': 0.30,  # NQ=F - Tech influence
            'Dow': 0.20      # YM=F - Industrials
        }
        
        # Asian Market Weights (sentiment indicator)
        self.asian_weights = {
            'Nikkei': 0.50,    # Japan - most correlated
            'HangSeng': 0.30,  # Hong Kong
            'Shanghai': 0.20   # China
        }
        
        # Commodity weights (overnight moves)
        self.commodity_weights = {
            'Oil': 0.40,     # Energy sector impact
            'Gold': 0.30,    # Risk-off indicator
            'Dollar': 0.30   # Currency strength
        }
        
        # European pre-market weights
        self.europe_weights = {
            'DAX': 0.60,     # German market
            'STOXX': 0.40    # Euro index
        }
        
        # Overall component weights
        self.component_weights = {
            'Futures': 0.70,     # US futures PRIMARY driver
            'Asian': 0.15,       # Asian sentiment
            'Commodities': 0.10, # Overnight commodities
            'Europe': 0.05       # European pre-market
        }
        
        # VIX Futures thresholds for confidence adjustment
        self.vix_thresholds = {
            'low': 15,      # < 15 = calm market, high confidence
            'medium': 25,   # 15-25 = normal volatility
            'high': 30      # > 30 = high fear, lower confidence
        }
    
    def get_futures_data(self, symbols: list) -> Dict:
        """
        Fetch current futures prices and calculate change from previous close.
        
        Args:
            symbols: List of Yahoo Finance futures ticker symbols
        
        Returns:
            Dictionary with symbol -> {price, prev_close, change_pct, timestamp}
        """
        results = {}
        
        try:
            ticker = Ticker(symbols)
            
            # Get current price data
            quotes = ticker.quotes
            
            if quotes is None or len(quotes) == 0:
                logger.warning(f"No quote data returned for {symbols}")
                return results
            
            # Get historical data for previous close
            end_date = datetime.now()
            start_date = end_date - timedelta(days=5)
            
            hist = ticker.history(start=start_date.strftime('%Y-%m-%d'),
                                end=end_date.strftime('%Y-%m-%d'),
                                interval='1d')
            
            for symbol in symbols:
                try:
                    # Get current price
                    if symbol in quotes:
                        quote = quotes[symbol]
                        current_price = quote.get('regularMarketPrice') or quote.get('preMarketPrice')
                        
                        if current_price is None:
                            logger.warning(f"No current price for {symbol}")
                            continue
                        
                        # Get previous close from history
                        prev_close = None
                        if hist is not None and len(hist) > 0 and symbol in hist.index.get_level_values(0):
                            symbol_data = hist.loc[symbol]
                            if len(symbol_data) >= 1:
                                prev_close = symbol_data['close'].iloc[-1]
                        
                        # Fallback to quote's previous close
                        if prev_close is None:
                            prev_close = quote.get('regularMarketPreviousClose')
                        
                        if prev_close and prev_close > 0:
                            change_pct = ((current_price - prev_close) / prev_close) * 100.0
                            
                            results[symbol] = {
                                'price': float(current_price),
                                'prev_close': float(prev_close),
                                'change_pct': float(change_pct),
                                'timestamp': datetime.now(self.timezone_us)
                            }
                            
                            logger.debug(f"{symbol}: {change_pct:+.2f}% (${current_price:.2f})")
                        else:
                            logger.warning(f"No previous close for {symbol}")
                    else:
                        logger.warning(f"Symbol {symbol} not found in quotes")
                        
                except Exception as e:
                    logger.error(f"Error processing {symbol}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Failed to fetch futures data: {e}")
        
        return results
    
    def get_market_close_data(self, symbols: list) -> Dict:
        """
        Fetch actual market close data for Asian markets.
        
        Args:
            symbols: List of Yahoo Finance ticker symbols
        
        Returns:
            Dictionary with symbol -> {close, prev_close, change_pct, timestamp}
        """
        results = {}
        
        try:
            ticker = Ticker(symbols)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=5)
            
            hist = ticker.history(start=start_date.strftime('%Y-%m-%d'),
                                end=end_date.strftime('%Y-%m-%d'),
                                interval='1d')
            
            if hist is None or len(hist) == 0:
                logger.warning(f"No historical data returned for {symbols}")
                return results
            
            for symbol in symbols:
                try:
                    if symbol in hist.index.get_level_values(0):
                        symbol_data = hist.loc[symbol]
                        
                        if len(symbol_data) >= 2:
                            last_close = symbol_data['close'].iloc[-1]
                            prev_close = symbol_data['close'].iloc[-2]
                            change_pct = ((last_close - prev_close) / prev_close) * 100.0
                            
                            results[symbol] = {
                                'close': float(last_close),
                                'prev_close': float(prev_close),
                                'change_pct': float(change_pct),
                                'timestamp': symbol_data.index[-1]
                            }
                            
                            logger.debug(f"{symbol}: {change_pct:+.2f}% (${last_close:.2f})")
                        else:
                            logger.warning(f"Insufficient data for {symbol} (only {len(symbol_data)} days)")
                    else:
                        logger.warning(f"Symbol {symbol} not found in data")
                        
                except Exception as e:
                    logger.error(f"Error processing {symbol}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Failed to fetch market close data: {e}")
        
        return results
    
    def compute_prediction(self, world_risk_score: Optional[float] = None) -> Dict:
        """
        Compute predicted US market opening gap using futures and Asian data.
        
        Args:
            world_risk_score: Optional world event risk score (0-100)
        
        Returns:
            Dictionary with prediction details:
            - predicted_gap_pct: Expected gap percentage
            - confidence: Prediction confidence (0-100)
            - direction: BULLISH/BEARISH/NEUTRAL
            - method: REALTIME_FUTURES_ASIAN
            - timestamp: Prediction timestamp
            - breakdown: Component contributions
            - source_data: Raw data used
        """
        logger.info("=" * 80)
        logger.info("US MARKET GAP PREDICTION - Realtime Futures & Asian Data")
        logger.info("=" * 80)
        
        # Initialize components
        futures_component = 0.0
        asian_component = 0.0
        commodity_component = 0.0
        europe_component = 0.0
        
        # Data availability flags
        has_futures = False
        has_asian = False
        has_commodities = False
        has_europe = False
        
        # Source data storage
        source_data = {
            'futures': {},
            'asian': {},
            'commodities': {},
            'europe': {}
        }
        
        # 1. Fetch US Futures Data (PRIMARY SIGNAL)
        futures_symbols = ['ES=F', 'NQ=F', 'YM=F']
        futures_data = self.get_futures_data(futures_symbols)
        
        if futures_data:
            has_futures = True
            sp_change = futures_data.get('ES=F', {}).get('change_pct', 0.0)
            nq_change = futures_data.get('NQ=F', {}).get('change_pct', 0.0)
            ym_change = futures_data.get('YM=F', {}).get('change_pct', 0.0)
            
            # Weighted futures component
            futures_component = (
                sp_change * self.us_futures_weights['SP500'] +
                nq_change * self.us_futures_weights['Nasdaq'] +
                ym_change * self.us_futures_weights['Dow']
            )
            
            source_data['futures'] = {
                'SP500_Futures': sp_change,
                'Nasdaq_Futures': nq_change,
                'Dow_Futures': ym_change
            }
            
            logger.info(f"US Futures: S&P {sp_change:+.2f}%, NASDAQ {nq_change:+.2f}%, DOW {ym_change:+.2f}%")
            logger.info(f"→ Weighted Futures Component: {futures_component:+.3f}%")
        else:
            logger.warning("⚠️  No US futures data available")
        
        # 2. Fetch Asian Market Closes
        asian_symbols = ['^N225', '^HSI', '000001.SS']
        asian_data = self.get_market_close_data(asian_symbols)
        
        if asian_data:
            has_asian = True
            nikkei_change = asian_data.get('^N225', {}).get('change_pct', 0.0)
            hsi_change = asian_data.get('^HSI', {}).get('change_pct', 0.0)
            shanghai_change = asian_data.get('000001.SS', {}).get('change_pct', 0.0)
            
            # Weighted Asian component (dampened correlation)
            asian_raw = (
                nikkei_change * self.asian_weights['Nikkei'] +
                hsi_change * self.asian_weights['HangSeng'] +
                shanghai_change * self.asian_weights['Shanghai']
            )
            asian_component = asian_raw * 0.35  # Asian markets have ~35% correlation to US
            
            source_data['asian'] = {
                'Nikkei': nikkei_change,
                'HangSeng': hsi_change,
                'Shanghai': shanghai_change
            }
            
            logger.info(f"Asian Markets: Nikkei {nikkei_change:+.2f}%, HSI {hsi_change:+.2f}%, Shanghai {shanghai_change:+.2f}%")
            logger.info(f"→ Weighted Asian Component: {asian_component:+.3f}%")
        else:
            logger.warning("⚠️  No Asian market data available")
        
        # 3. Fetch Commodity Data
        commodity_symbols = ['BZ=F', 'GC=F', 'DX=F']
        commodity_data = self.get_futures_data(commodity_symbols)
        
        if commodity_data:
            has_commodities = True
            oil_change = commodity_data.get('BZ=F', {}).get('change_pct', 0.0)
            gold_change = commodity_data.get('GC=F', {}).get('change_pct', 0.0)
            dollar_change = commodity_data.get('DX=F', {}).get('change_pct', 0.0)
            
            # Oil positive for energy sector
            # Gold inverse (risk-off when gold rises)
            # Dollar inverse (strong dollar = headwind for US stocks)
            commodity_component = (
                oil_change * self.commodity_weights['Oil'] * 0.5 -
                gold_change * self.commodity_weights['Gold'] * 0.3 -
                dollar_change * self.commodity_weights['Dollar'] * 0.4
            )
            
            source_data['commodities'] = {
                'Oil': oil_change,
                'Gold': gold_change,
                'Dollar': dollar_change
            }
            
            logger.info(f"Commodities: Oil {oil_change:+.2f}%, Gold {gold_change:+.2f}%, Dollar {dollar_change:+.2f}%")
            logger.info(f"→ Weighted Commodity Component: {commodity_component:+.3f}%")
        else:
            logger.warning("⚠️  No commodity data available")
        
        # 4. Fetch European Pre-Market
        europe_symbols = ['FDAX=F', 'FESX=F']
        europe_data = self.get_futures_data(europe_symbols)
        
        if europe_data:
            has_europe = True
            dax_change = europe_data.get('FDAX=F', {}).get('change_pct', 0.0)
            stoxx_change = europe_data.get('FESX=F', {}).get('change_pct', 0.0)
            
            # Weighted European component (low correlation)
            europe_raw = (
                dax_change * self.europe_weights['DAX'] +
                stoxx_change * self.europe_weights['STOXX']
            )
            europe_component = europe_raw * 0.25  # Europe has ~25% correlation
            
            source_data['europe'] = {
                'DAX_Futures': dax_change,
                'STOXX_Futures': stoxx_change
            }
            
            logger.info(f"Europe Pre-Market: DAX {dax_change:+.2f}%, STOXX {stoxx_change:+.2f}%")
            logger.info(f"→ Weighted Europe Component: {europe_component:+.3f}%")
        
        # 5. Combine all components with weights
        if not has_futures:
            # Cannot predict without futures data
            return self._get_fallback_prediction("No US futures data available")
        
        # Base prediction from futures (most important)
        predicted_gap = futures_component * self.component_weights['Futures']
        
        # Add Asian component if available
        if has_asian:
            predicted_gap += asian_component * self.component_weights['Asian']
        
        # Add commodity component if available
        if has_commodities:
            predicted_gap += commodity_component * self.component_weights['Commodities']
        
        # Add Europe component if available
        if has_europe:
            predicted_gap += europe_component * self.component_weights['Europe']
        
        logger.info("=" * 80)
        logger.info(f"RAW PREDICTED GAP: {predicted_gap:+.2f}%")
        
        # 6. Confidence calculation based on data availability and VIX
        base_confidence = 0.85  # High confidence since futures are very predictive
        
        # Adjust for missing data
        if not has_asian:
            base_confidence *= 0.95
        if not has_commodities:
            base_confidence *= 0.98
        if not has_europe:
            base_confidence *= 0.99
        
        # Get VIX futures for volatility adjustment
        vix_data = self.get_futures_data(['VX=F'])
        vix_value = 20.0  # Default
        
        if vix_data and 'VX=F' in vix_data:
            vix_value = vix_data['VX=F'].get('price', 20.0)
            logger.info(f"VIX Futures: {vix_value:.2f}")
        else:
            logger.info("⚠️  No VIX futures data, using base confidence")
        
        # VIX-based confidence adjustment
        if vix_value < self.vix_thresholds['low']:
            confidence = base_confidence * 0.95  # Very calm = slightly less predictive
        elif vix_value < self.vix_thresholds['medium']:
            confidence = base_confidence  # Normal volatility
        elif vix_value < self.vix_thresholds['high']:
            confidence = base_confidence * 0.90  # Elevated fear
        else:
            confidence = base_confidence * 0.80  # High fear = less predictable
            predicted_gap *= 0.85  # Dampen prediction in extreme volatility
        
        # 7. World Risk adjustment (if provided)
        if world_risk_score is not None and world_risk_score > 75:
            risk_factor = (world_risk_score - 75) / 100.0  # 0 to 0.25
            confidence *= (1.0 - risk_factor * 0.3)  # Reduce confidence up to 30%
            predicted_gap *= (1.0 - risk_factor * 0.2)  # Dampen gap up to 20%
            logger.info(f"⚠️  High World Risk ({world_risk_score:.1f}/100) - Reduced confidence and gap")
        
        # 8. Determine direction
        if predicted_gap > 0.3:
            direction = 'BULLISH'
        elif predicted_gap < -0.3:
            direction = 'BEARISH'
        else:
            direction = 'NEUTRAL'
        
        # Format final result
        result = {
            'predicted_gap_pct': round(predicted_gap, 2),
            'confidence': round(confidence * 100, 0),
            'direction': direction,
            'method': 'REALTIME_FUTURES_ASIAN',
            'timestamp': datetime.now(self.timezone_us).isoformat(),
            'breakdown': {
                'futures_component': round(futures_component * self.component_weights['Futures'], 3),
                'asian_component': round(asian_component * self.component_weights['Asian'], 3),
                'commodity_component': round(commodity_component * self.component_weights['Commodities'], 3),
                'europe_component': round(europe_component * self.component_weights['Europe'], 3)
            },
            'source_data': source_data,
            'vix_futures': vix_value,
            'world_risk_score': world_risk_score,
            'available': True
        }
        
        logger.info("=" * 80)
        logger.info(f"FINAL US MARKET GAP PREDICTION:")
        logger.info(f"  Gap: {predicted_gap:+.2f}%")
        logger.info(f"  Direction: {direction}")
        logger.info(f"  Confidence: {confidence*100:.0f}%")
        logger.info(f"  Breakdown:")
        logger.info(f"    Futures:     {result['breakdown']['futures_component']:+.3f}%")
        logger.info(f"    Asian:       {result['breakdown']['asian_component']:+.3f}%")
        logger.info(f"    Commodities: {result['breakdown']['commodity_component']:+.3f}%")
        logger.info(f"    Europe:      {result['breakdown']['europe_component']:+.3f}%")
        logger.info("=" * 80)
        
        return result
    
    def _get_fallback_prediction(self, reason: str) -> Dict:
        """Return a neutral fallback prediction when data is insufficient."""
        logger.warning(f"⚠️  Fallback prediction: {reason}")
        
        return {
            'predicted_gap_pct': 0.0,
            'confidence': 0.0,
            'direction': 'NEUTRAL',
            'method': 'FALLBACK',
            'reason': reason,
            'available': False,
            'timestamp': datetime.now(self.timezone_us).isoformat()
        }


# Test module
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    predictor = RealtimeSPXPredictor()
    result = predictor.compute_prediction()
    
    print("\n" + "=" * 80)
    print("US MARKET GAP PREDICTION TEST")
    print("=" * 80)
    print(f"Predicted Gap: {result['predicted_gap_pct']:+.2f}%")
    print(f"Direction: {result['direction']}")
    print(f"Confidence: {result['confidence']:.0f}%")
    print(f"Method: {result['method']}")
    
    if 'breakdown' in result:
        print("\nComponent Breakdown:")
        for component, value in result['breakdown'].items():
            print(f"  {component}: {value:+.3f}%")
    
    if 'source_data' in result:
        print("\nSource Data:")
        for category, data in result['source_data'].items():
            if data:
                print(f"  {category.upper()}:")
                for key, value in data.items():
                    print(f"    {key}: {value:+.2f}%")
    
    print("=" * 80)
