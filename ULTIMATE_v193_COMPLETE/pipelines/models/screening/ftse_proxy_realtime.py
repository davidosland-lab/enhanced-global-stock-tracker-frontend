"""
FTSE 100 Pre-Market Prediction Module - REALTIME DATA VERSION

This module provides pre-market FTSE 100 gap predictions using ACTUAL market close data 
from US, European, and Asian markets.

Designed to run BEFORE LSE market open (before 08:00 GMT) to predict the opening gap.

Data Sources (in priority order):
1. US Market Closes (Previous day):
   - S&P 500 (^GSPC) - Weight: 45%
   - NASDAQ (^IXIC) - Weight: 25%
   - Dow Jones (^DJI) - Weight: 15%

2. European Markets:
   - DAX (^GDAXI) - Germany - Weight: 35%
   - CAC 40 (^FCHI) - France - Weight: 25%
   - Euro Stoxx 50 (^STOXX50E) - Weight: 20%

3. FTSE Futures:
   - FTSE 100 Futures (Z=F) - Weight: 15%

4. Currency:
   - GBP/USD (GBPUSD=X) - Weight: 15%
   - EUR/GBP (EURGBP=X) - Weight: 10%

5. Commodities:
   - Brent Crude (BZ=F) - Weight: 40%
   - Gold (GC=F) - Weight: 30%
   - Copper (HG=F) - Weight: 30%

6. Market Fear:
   - VFTSE (^VFTSE) - UK VIX - Used for confidence adjustment

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


class RealtimeFTSEPredictor:
    """
    Predicts FTSE 100 opening gap using actual US/EU/Asian market close data.
    
    This predictor is specifically designed for pre-market analysis and uses
    real market close prices instead of futures contracts.
    """
    
    def __init__(self):
        self.timezone_london = pytz.timezone('Europe/London')
        self.timezone_us = pytz.timezone('US/Eastern')
        self.timezone_eu = pytz.timezone('Europe/Paris')
        
        # Base correlation between US and FTSE markets (historical average)
        # FTSE has ~50-60% correlation with S&P 500
        self.base_correlation = 0.55
        
        # US Market Weights (lower than ASX due to time zone differences)
        self.us_weights = {
            'SP500': 0.45,   # Primary driver
            'Nasdaq': 0.25,  # Tech sector
            'Dow': 0.15      # Industrial
        }
        
        # European Market Weights (very strong correlation)
        self.eu_weights = {
            'DAX': 0.35,      # Germany - strongest correlation
            'CAC': 0.25,      # France
            'STOXX': 0.20     # Euro Stoxx 50
        }
        
        # Currency Weights
        self.fx_weights = {
            'GBPUSD': 0.60,   # Primary - weak GBP helps FTSE exporters
            'EURGBP': 0.40    # Secondary - EUR/GBP relationship
        }
        
        # Commodity Weights
        self.commodity_weights = {
            'Oil': 0.40,      # Brent crude - UK has oil majors (BP, Shell)
            'Gold': 0.30,     # Safe haven
            'Copper': 0.30    # Industrial metals - mining sector
        }
        
        # Overall component weights
        self.component_weights = {
            'US': 0.35,         # US markets (overnight close)
            'Europe': 0.30,     # European markets (same day close)
            'Futures': 0.15,    # FTSE futures (Z=F)
            'FX': 0.10,         # Currency movements
            'Commodities': 0.10 # Commodity basket
        }
        
        # VFTSE (UK VIX) thresholds for confidence adjustment
        self.vftse_thresholds = {
            'low': 12,      # < 12 = calm market, high confidence
            'medium': 18,   # 12-18 = normal volatility
            'high': 25      # > 25 = high fear, lower confidence
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
        Compute FTSE 100 opening gap prediction using realtime market close data.
        
        Args:
            world_risk_score: Optional world event risk score (0-100) for adjustments
        
        Returns:
            Dictionary with predicted_gap_pct, confidence, direction, method, and breakdown
        """
        logger.info("[REALTIME FTSE] Computing pre-market prediction using actual market closes...")
        
        # 1. Fetch US Market Closes
        us_symbols = ['^GSPC', '^IXIC', '^DJI']
        us_data = self.get_market_close_data(us_symbols)
        
        # 2. Fetch European Market Closes
        eu_symbols = ['^GDAXI', '^FCHI', '^STOXX50E']
        eu_data = self.get_market_close_data(eu_symbols)
        
        # 3. Fetch FTSE Futures
        futures_symbols = ['Z=F']  # FTSE 100 Futures
        futures_data = self.get_market_close_data(futures_symbols)
        
        # 4. Fetch Currency Data
        fx_symbols = ['GBPUSD=X', 'EURGBP=X']
        fx_data = self.get_market_close_data(fx_symbols)
        
        # 5. Fetch Commodity Data
        commodity_symbols = ['BZ=F', 'GC=F', 'HG=F']  # Brent, Gold, Copper
        commodity_data = self.get_market_close_data(commodity_symbols)
        
        # 6. Fetch VFTSE for confidence calculation
        vftse_data = self.get_market_close_data(['^VFTSE'])
        
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
            
            # Apply base correlation to US market (FTSE less correlated than ASX)
            us_component = us_weighted_change * self.base_correlation * self.component_weights['US']
            us_valid = True
            
            logger.info(f"[US MARKETS] S&P: {sp500_change:+.2f}%, NASDAQ: {nasdaq_change:+.2f}%, DOW: {dow_change:+.2f}%")
            logger.info(f"[US MARKETS] Weighted: {us_weighted_change:+.2f}% → FTSE Impact: {us_component:+.2f}%")
        else:
            logger.warning("[US MARKETS] Insufficient US market data")
            if not us_data:
                return self._get_fallback_prediction("Insufficient US market data")
        
        # === CALCULATE EUROPEAN MARKET COMPONENT ===
        eu_component = 0.0
        eu_valid_count = 0
        
        if '^GDAXI' in eu_data:
            dax_change = eu_data['^GDAXI']['change_pct']
            eu_component += dax_change * self.eu_weights['DAX']
            eu_valid_count += 1
            logger.debug(f"[EUROPE] DAX: {dax_change:+.2f}%")
        
        if '^FCHI' in eu_data:
            cac_change = eu_data['^FCHI']['change_pct']
            eu_component += cac_change * self.eu_weights['CAC']
            eu_valid_count += 1
            logger.debug(f"[EUROPE] CAC 40: {cac_change:+.2f}%")
        
        if '^STOXX50E' in eu_data:
            stoxx_change = eu_data['^STOXX50E']['change_pct']
            eu_component += stoxx_change * self.eu_weights['STOXX']
            eu_valid_count += 1
            logger.debug(f"[EUROPE] STOXX 50: {stoxx_change:+.2f}%")
        
        if eu_valid_count > 0:
            # Normalize by number of valid markets
            eu_component *= (self.component_weights['Europe'] / eu_valid_count * 3)
            logger.info(f"[EUROPE] {eu_valid_count} markets → FTSE Impact: {eu_component:+.2f}%")
        else:
            logger.warning("[EUROPE] No European market data available")
        
        # === CALCULATE FUTURES COMPONENT ===
        futures_component = 0.0
        
        if 'Z=F' in futures_data:
            ftse_futures_change = futures_data['Z=F']['change_pct']
            futures_component = ftse_futures_change * self.component_weights['Futures']
            
            logger.info(f"[FUTURES] FTSE Futures (Z=F): {ftse_futures_change:+.2f}% → Impact: {futures_component:+.2f}%")
        else:
            logger.warning("[FUTURES] No FTSE futures data available")
        
        # === CALCULATE FX COMPONENT ===
        fx_component = 0.0
        fx_valid_count = 0
        
        if 'GBPUSD=X' in fx_data:
            gbpusd_change = fx_data['GBPUSD=X']['change_pct']
            # Inverse relationship: Strong GBP hurts FTSE exporters (60% of FTSE 100)
            fx_component += -gbpusd_change * self.fx_weights['GBPUSD']
            fx_valid_count += 1
            logger.debug(f"[FX] GBP/USD: {gbpusd_change:+.2f}%")
        
        if 'EURGBP=X' in fx_data:
            eurgbp_change = fx_data['EURGBP=X']['change_pct']
            # EUR/GBP relationship
            fx_component += eurgbp_change * self.fx_weights['EURGBP'] * 0.5
            fx_valid_count += 1
            logger.debug(f"[FX] EUR/GBP: {eurgbp_change:+.2f}%")
        
        if fx_valid_count > 0:
            fx_component *= self.component_weights['FX']
            logger.info(f"[FX] Currency Impact: {fx_component:+.2f}%")
        
        # === CALCULATE COMMODITY COMPONENT ===
        commodity_component = 0.0
        commodity_valid_count = 0
        
        if 'BZ=F' in commodity_data:
            oil_change = commodity_data['BZ=F']['change_pct']
            commodity_component += oil_change * self.commodity_weights['Oil']
            commodity_valid_count += 1
            logger.debug(f"[COMMODITY] Brent Oil: {oil_change:+.2f}%")
        
        if 'GC=F' in commodity_data:
            gold_change = commodity_data['GC=F']['change_pct']
            commodity_component += gold_change * self.commodity_weights['Gold'] * 0.3  # Partial correlation
            commodity_valid_count += 1
            logger.debug(f"[COMMODITY] Gold: {gold_change:+.2f}%")
        
        if 'HG=F' in commodity_data:
            copper_change = commodity_data['HG=F']['change_pct']
            commodity_component += copper_change * self.commodity_weights['Copper']
            commodity_valid_count += 1
            logger.debug(f"[COMMODITY] Copper: {copper_change:+.2f}%")
        
        if commodity_valid_count > 0:
            commodity_component *= self.component_weights['Commodities']
            logger.info(f"[COMMODITIES] Combined Impact: {commodity_component:+.2f}%")
        
        # === COMBINE ALL COMPONENTS ===
        predicted_gap = us_component + eu_component + futures_component + fx_component + commodity_component
        
        # === CALCULATE CONFIDENCE BASED ON VFTSE ===
        base_confidence = 0.70
        
        if '^VFTSE' in vftse_data:
            vftse_level = vftse_data['^VFTSE']['close']
            
            if vftse_level < self.vftse_thresholds['low']:
                confidence = 0.80  # Calm market = higher confidence
                conf_reason = "Low VFTSE"
            elif vftse_level < self.vftse_thresholds['medium']:
                confidence = 0.75  # Normal volatility
                conf_reason = "Normal VFTSE"
            elif vftse_level < self.vftse_thresholds['high']:
                confidence = 0.70  # Elevated volatility
                conf_reason = "Elevated VFTSE"
            else:
                confidence = 0.65  # High fear = lower confidence
                conf_reason = "High VFTSE"
                # Reduce gap prediction in high volatility
                predicted_gap *= 0.80
            
            logger.info(f"[VFTSE] Level: {vftse_level:.2f} → Confidence: {confidence:.0%} ({conf_reason})")
        else:
            confidence = base_confidence
            logger.warning("[VFTSE] No VFTSE data - using base confidence")
        
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
            'timestamp': datetime.now(self.timezone_london).isoformat(),
            'breakdown': {
                'us_component': round(us_component, 3),
                'europe_component': round(eu_component, 3),
                'futures_component': round(futures_component, 3),
                'fx_component': round(fx_component, 3),
                'commodity_component': round(commodity_component, 3)
            },
            'source_data': {
                'us_markets': {
                    'SP500': us_data.get('^GSPC', {}).get('change_pct', None),
                    'Nasdaq': us_data.get('^IXIC', {}).get('change_pct', None),
                    'Dow': us_data.get('^DJI', {}).get('change_pct', None)
                },
                'europe_markets': {
                    'DAX': eu_data.get('^GDAXI', {}).get('change_pct', None),
                    'CAC': eu_data.get('^FCHI', {}).get('change_pct', None),
                    'STOXX': eu_data.get('^STOXX50E', {}).get('change_pct', None)
                },
                'futures': {
                    'FTSE_Futures': futures_data.get('Z=F', {}).get('change_pct', None)
                },
                'fx': {
                    'GBPUSD': fx_data.get('GBPUSD=X', {}).get('change_pct', None),
                    'EURGBP': fx_data.get('EURGBP=X', {}).get('change_pct', None)
                },
                'vftse': vftse_data.get('^VFTSE', {}).get('close', None)
            },
            'available': True
        }
        
        logger.info(f"[REALTIME FTSE] PREDICTION: {predicted_gap:+.2f}% ({direction}, {confidence:.0%} confidence)")
        logger.info(f"[REALTIME FTSE] Breakdown: US={us_component:+.2f}%, EU={eu_component:+.2f}%, Futures={futures_component:+.2f}%, FX={fx_component:+.2f}%, Commodities={commodity_component:+.2f}%")
        
        return result
    
    def _get_fallback_prediction(self, reason: str) -> Dict:
        """Return a neutral prediction when data is insufficient"""
        logger.warning(f"[REALTIME FTSE] Returning fallback prediction: {reason}")
        
        return {
            'predicted_gap_pct': 0.0,
            'confidence': 0.0,
            'direction': 'NEUTRAL',
            'method': 'FALLBACK',
            'error': reason,
            'available': False,
            'timestamp': datetime.now(self.timezone_london).isoformat()
        }


# === TEST MODULE ===
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    predictor = RealtimeFTSEPredictor()
    result = predictor.compute_prediction()
    
    print("\n" + "="*80)
    print("REALTIME FTSE PREDICTION RESULT")
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
        if result['source_data']['us_markets']['SP500']:
            print(f"  S&P 500: {result['source_data']['us_markets']['SP500']:+.2f}%")
            print(f"  NASDAQ: {result['source_data']['us_markets']['Nasdaq']:+.2f}%")
            print(f"  DOW: {result['source_data']['us_markets']['Dow']:+.2f}%")
        if result['source_data']['europe_markets']['DAX']:
            print(f"  DAX: {result['source_data']['europe_markets']['DAX']:+.2f}%")
        if result['source_data']['futures']['FTSE_Futures']:
            print(f"  FTSE Futures: {result['source_data']['futures']['FTSE_Futures']:+.2f}%")
        print(f"  VFTSE: {result['source_data'].get('vftse', 'N/A')}")
    
    print("="*80)
