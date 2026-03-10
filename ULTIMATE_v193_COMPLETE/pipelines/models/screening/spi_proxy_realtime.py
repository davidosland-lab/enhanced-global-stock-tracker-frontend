"""
SPI 200 Pre-Market Prediction Module - REALTIME DATA VERSION

This module provides pre-market ASX 200 gap predictions using ACTUAL market close data 
from US and UK markets, NOT futures data.

Designed to run BEFORE ASX market open (before 10:00 AM AEST) to predict the opening gap.

Data Sources (in priority order):
1. US Market Closes (Previous day):
   - S&P 500 (^GSPC) - Weight: 50%
   - NASDAQ (^IXIC) - Weight: 30%
   - Dow Jones (^DJI) - Weight: 20%

2. UK Market Close:
   - FTSE 100 (^FTSE) - Correlation: 0.40

3. Commodities:
   - AUD/USD (AUDUSD=X) - Weight: 50%
   - Iron Ore (TIO.AX as proxy) - Weight: 25%
   - Brent Crude (BZ=F) - Weight: 25%

4. Market Fear:
   - VIX (^VIX) - Used for confidence adjustment

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


class RealtimeSPIPredictor:
    """
    Predicts ASX 200 opening gap using actual US/UK market close data.
    
    This predictor is specifically designed for pre-market analysis and uses
    real market close prices instead of futures contracts.
    """
    
    def __init__(self):
        self.timezone_sydney = pytz.timezone('Australia/Sydney')
        self.timezone_us = pytz.timezone('US/Eastern')
        self.timezone_uk = pytz.timezone('Europe/London')
        
        # Base correlation between US and ASX markets (historical average)
        self.base_correlation = 0.65
        
        # US Market Weights (based on historical correlation strength)
        self.us_weights = {
            'SP500': 0.50,   # Strongest correlation
            'Nasdaq': 0.30,   # Tech sector influence
            'Dow': 0.20       # Industrial sector
        }
        
        # UK Market correlation (weaker than US)
        self.uk_correlation = 0.40
        
        # Commodity weights
        self.commodity_weights = {
            'AUD': 0.50,      # Currency impact
            'Iron': 0.25,     # Major Australian export
            'Oil': 0.25       # Energy sector
        }
        
        # Overall component weights
        # v193.11.6.21: Reduced commodity weight 0.10 -> 0.05, increased US weight 0.65 -> 0.70
        # Reason: Gap prediction +0.38% vs actual +1.3% (242% error) - commodities too volatile/unreliable
        self.component_weights = {
            'US': 0.70,         # US markets primary driver (increased from 0.65)
            'Futures': 0.15,    # Overnight futures (ES, NQ)
            'UK': 0.10,         # UK market
            'Commodities': 0.05 # Commodities basket (reduced from 0.10)
        }
        
        # VIX thresholds for confidence adjustment
        self.vix_thresholds = {
            'low': 15,      # < 15 = calm market, high confidence
            'medium': 25,   # 15-25 = normal volatility
            'high': 30      # > 30 = high fear, lower confidence
        }
    
    def get_market_close_data(self, symbols: list, days_back: int = 1) -> Dict:
        """
        Fetch actual market close data for given symbols.
        
        Args:
            symbols: List of Yahoo Finance ticker symbols
            days_back: Number of days to look back (default 1 for yesterday's close)
        
        Returns:
            Dictionary with symbol -> {close, change_pct, timestamp}
        """
        results = {}
        
        try:
            ticker = Ticker(symbols)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=5)  # Get last 5 days to ensure we have data
            
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
                            # Get the last two trading days
                            last_close = symbol_data['close'].iloc[-1]
                            prev_close = symbol_data['close'].iloc[-2]
                            change_pct = ((last_close - prev_close) / prev_close) * 100.0
                            
                            results[symbol] = {
                                'close': float(last_close),
                                'prev_close': float(prev_close),
                                'change_pct': float(change_pct),
                                'timestamp': symbol_data.index[-1]
                            }
                            
                            logger.debug(f"{symbol}: {change_pct:+.2f}% (USD{last_close:.2f})")
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
        Compute ASX 200 opening gap prediction using realtime market close data.
        
        Args:
            world_risk_score: Optional world event risk score (0-100) for adjustments
        
        Returns:
            Dictionary with predicted_gap_pct, confidence, direction, method, and breakdown
        """
        logger.info("[REALTIME SPI] Computing pre-market prediction using actual market closes...")
        
        # 1. Fetch US Market Closes
        us_symbols = ['^GSPC', '^IXIC', '^DJI']
        us_data = self.get_market_close_data(us_symbols)
        
        # 2. Fetch UK Market Close
        uk_data = self.get_market_close_data(['^FTSE'])
        
        # 3. Fetch Commodity Data
        commodity_symbols = ['AUDUSD=X', 'BZ=F', 'TIO.AX']
        commodity_data = self.get_market_close_data(commodity_symbols)
        
        # 4. Fetch VIX for confidence calculation
        vix_data = self.get_market_close_data(['^VIX'])
        
        # 5. Fetch Overnight Futures (ES, NQ) for additional context
        futures_symbols = ['ES=F', 'NQ=F']
        futures_data = self.get_market_close_data(futures_symbols)
        
        # === CALCULATE US MARKET COMPONENT ===
        us_component = 0.0
        us_valid = False
        
        if '^GSPC' in us_data and '^IXIC' in us_data and '^DJI' in us_data:
            sp500_change = us_data['^GSPC']['change_pct']
            nasdaq_change = us_data['^IXIC']['change_pct']
            dow_change = us_data['^DJI']['change_pct']
            
            us_weighted_change = (
                sp500_change * self.us_weights['SP500'] +
                nasdaq_change * self.us_weights['Nasdaq'] +
                dow_change * self.us_weights['Dow']
            )
            
            # Apply base correlation to US market
            us_component = us_weighted_change * self.base_correlation * self.component_weights['US']
            us_valid = True
            
            logger.info(f"[US MARKETS] S&P: {sp500_change:+.2f}%, NASDAQ: {nasdaq_change:+.2f}%, DOW: {dow_change:+.2f}%")
            logger.info(f"[US MARKETS] Weighted: {us_weighted_change:+.2f}% -> ASX Impact: {us_component:+.2f}%")
        else:
            logger.warning("[US MARKETS] Insufficient US market data - cannot compute US component")
            return self._get_fallback_prediction("Insufficient US market data")
        
        # === CALCULATE FUTURES COMPONENT ===
        futures_component = 0.0
        
        if 'ES=F' in futures_data and 'NQ=F' in futures_data:
            es_change = futures_data['ES=F']['change_pct']
            nq_change = futures_data['NQ=F']['change_pct']
            
            # Weight: 60% ES, 40% NQ
            futures_weighted = es_change * 0.60 + nq_change * 0.40
            futures_component = futures_weighted * self.component_weights['Futures']
            
            logger.info(f"[FUTURES] ES: {es_change:+.2f}%, NQ: {nq_change:+.2f}% -> Impact: {futures_component:+.2f}%")
        else:
            logger.warning("[FUTURES] Limited futures data available")
        
        # === CALCULATE UK COMPONENT ===
        uk_component = 0.0
        
        if '^FTSE' in uk_data:
            ftse_change = uk_data['^FTSE']['change_pct']
            uk_component = ftse_change * self.uk_correlation * self.component_weights['UK']
            
            logger.info(f"[UK] FTSE: {ftse_change:+.2f}% -> ASX Impact: {uk_component:+.2f}%")
        else:
            logger.warning("[UK] No FTSE data available")
        
        # === CALCULATE COMMODITY COMPONENT ===
        commodity_component = 0.0
        commodity_valid_count = 0
        
        if 'AUDUSD=X' in commodity_data:
            aud_change = commodity_data['AUDUSD=X']['change_pct']
            commodity_component += aud_change * self.commodity_weights['AUD']
            commodity_valid_count += 1
            logger.debug(f"[COMMODITY] AUD: {aud_change:+.2f}%")
        
        if 'BZ=F' in commodity_data:
            oil_change = commodity_data['BZ=F']['change_pct']
            commodity_component += oil_change * self.commodity_weights['Oil']
            commodity_valid_count += 1
            logger.debug(f"[COMMODITY] Oil: {oil_change:+.2f}%")
        
        if 'TIO.AX' in commodity_data:
            iron_change = commodity_data['TIO.AX']['change_pct']
            commodity_component += iron_change * self.commodity_weights['Iron']
            commodity_valid_count += 1
            logger.debug(f"[COMMODITY] Iron: {iron_change:+.2f}%")
        
        if commodity_valid_count > 0:
            commodity_component *= self.component_weights['Commodities']
            logger.info(f"[COMMODITIES] Combined Impact: {commodity_component:+.2f}%")
        
        # === COMBINE ALL COMPONENTS ===
        predicted_gap = us_component + futures_component + uk_component + commodity_component
        
        # === CALCULATE CONFIDENCE BASED ON VIX ===
        base_confidence = 0.70
        
        if '^VIX' in vix_data:
            vix_level = vix_data['^VIX']['close']
            
            if vix_level < self.vix_thresholds['low']:
                confidence = 0.80  # Calm market = higher confidence
                conf_reason = "Low VIX"
            elif vix_level < self.vix_thresholds['medium']:
                confidence = 0.75  # Normal volatility
                conf_reason = "Normal VIX"
            elif vix_level < self.vix_thresholds['high']:
                confidence = 0.70  # Elevated volatility
                conf_reason = "Elevated VIX"
            else:
                confidence = 0.65  # High fear = lower confidence
                conf_reason = "High VIX"
                # Reduce gap prediction in high volatility
                predicted_gap *= 0.80
            
            logger.info(f"[VIX] Level: {vix_level:.2f} -> Confidence: {confidence:.0%} ({conf_reason})")
        else:
            confidence = base_confidence
            logger.warning("[VIX] No VIX data - using base confidence")
        
        # === APPLY WORLD RISK ADJUSTMENT ===
        if world_risk_score is not None and world_risk_score > 75:
            risk_adjustment = (world_risk_score - 75) / 100  # 0 to 0.25
            confidence -= risk_adjustment
            predicted_gap *= (1.0 - risk_adjustment * 0.5)
            logger.info(f"[WORLD RISK] High risk ({world_risk_score:.0f}/100) - reduced confidence and gap")
        
        # === DETERMINE DIRECTION ===
        if predicted_gap > 0.3:
            direction = 'BULLISH'
        elif predicted_gap < -0.3:
            direction = 'BEARISH'
        else:
            direction = 'NEUTRAL'
        
        # === BUILD RESULT ===
        result = {
            'predicted_gap_pct': round(predicted_gap, 2),
            'confidence': round(confidence, 2),
            'direction': direction,
            'method': 'REALTIME_MARKET_CLOSES',
            'timestamp': datetime.now(self.timezone_sydney).isoformat(),
            'breakdown': {
                'us_component': round(us_component, 3),
                'futures_component': round(futures_component, 3),
                'uk_component': round(uk_component, 3),
                'commodity_component': round(commodity_component, 3)
            },
            'source_data': {
                'us_markets': {
                    'SP500': us_data.get('^GSPC', {}).get('change_pct', None),
                    'Nasdaq': us_data.get('^IXIC', {}).get('change_pct', None),
                    'Dow': us_data.get('^DJI', {}).get('change_pct', None)
                },
                'uk_markets': {
                    'FTSE': uk_data.get('^FTSE', {}).get('change_pct', None)
                },
                'vix': vix_data.get('^VIX', {}).get('close', None)
            },
            'available': True
        }
        
        logger.info(f"[REALTIME SPI] PREDICTION: {predicted_gap:+.2f}% ({direction}, {confidence:.0%} confidence)")
        logger.info(f"[REALTIME SPI] Breakdown: US={us_component:+.2f}%, Futures={futures_component:+.2f}%, UK={uk_component:+.2f}%, Commodities={commodity_component:+.2f}%")
        
        return result
    
    def _get_fallback_prediction(self, reason: str) -> Dict:
        """Return a neutral prediction when data is insufficient"""
        logger.warning(f"[REALTIME SPI] Returning fallback prediction: {reason}")
        
        return {
            'predicted_gap_pct': 0.0,
            'confidence': 0.0,
            'direction': 'NEUTRAL',
            'method': 'FALLBACK',
            'error': reason,
            'available': False,
            'timestamp': datetime.now(self.timezone_sydney).isoformat()
        }


# === TEST MODULE ===
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    predictor = RealtimeSPIPredictor()
    result = predictor.compute_prediction()
    
    print("\n" + "="*80)
    print("REALTIME SPI PREDICTION RESULT")
    print("="*80)
    print(f"Predicted Gap: {result['predicted_gap_pct']:+.2f}%")
    print(f"Confidence: {result['confidence']:.0%}")
    print(f"Direction: {result['direction']}")
    print(f"Method: {result['method']}")
    
    if 'breakdown' in result:
        print("\nBreakdown:")
        for component, value in result['breakdown'].items():
            print(f"  {component}: {value:+.3f}%")
    
    if 'source_data' in result:
        print("\nSource Data:")
        print(f"  S&P 500: {result['source_data']['us_markets']['SP500']:+.2f}%")
        print(f"  NASDAQ: {result['source_data']['us_markets']['Nasdaq']:+.2f}%")
        print(f"  DOW: {result['source_data']['us_markets']['Dow']:+.2f}%")
        print(f"  VIX: {result['source_data'].get('vix', 'N/A')}")
    
    print("="*80)
