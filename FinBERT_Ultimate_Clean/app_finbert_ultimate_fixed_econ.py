#!/usr/bin/env python3
"""
Economic Data Fix - Extracts just the fixed get_economic_indicators method
This can be integrated into app_finbert_ultimate.py
"""

import yfinance as yf
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict

logger = logging.getLogger(__name__)

def get_economic_indicators(self) -> Dict[str, float]:
    """Fetch economic indicators from multiple sources"""
    indicators = {}
    
    # First, try to get data from Yahoo Finance (free, no API key needed)
    try:
        # VIX - Volatility Index
        vix = yf.Ticker("^VIX")
        vix_hist = vix.history(period="1d")
        if not vix_hist.empty:
            indicators['vix'] = float(vix_hist['Close'].iloc[-1])
        else:
            indicators['vix'] = 0.0
            
        # 10-Year Treasury Yield
        tnx = yf.Ticker("^TNX")
        tnx_hist = tnx.history(period="1d")
        if not tnx_hist.empty:
            indicators['treasury_10y'] = float(tnx_hist['Close'].iloc[-1])
        else:
            indicators['treasury_10y'] = 0.0
            
        # DXY - US Dollar Index
        dxy = yf.Ticker("DX-Y.NYB")
        dxy_hist = dxy.history(period="1d")
        if not dxy_hist.empty:
            indicators['dollar_index'] = float(dxy_hist['Close'].iloc[-1])
        else:
            indicators['dollar_index'] = 0.0
            
        # Gold Price (as inflation hedge indicator)
        gold = yf.Ticker("GC=F")
        gold_hist = gold.history(period="1d")
        if not gold_hist.empty:
            indicators['gold'] = float(gold_hist['Close'].iloc[-1])
        else:
            indicators['gold'] = 0.0
            
        # Oil Price (WTI Crude)
        oil = yf.Ticker("CL=F")
        oil_hist = oil.history(period="1d")
        if not oil_hist.empty:
            indicators['oil_wti'] = float(oil_hist['Close'].iloc[-1])
        else:
            indicators['oil_wti'] = 0.0
            
        logger.info(f"Fetched Yahoo Finance indicators: {indicators}")
        
    except Exception as e:
        logger.warning(f"Failed to fetch Yahoo Finance indicators: {e}")
    
    # Try FRED API if we have a valid key (not 'demo')
    if self.fred_key and self.fred_key != 'demo':
        series = {
            'DFF': 'fed_funds_rate',
            'UNRATE': 'unemployment',
            'CPIAUCSL': 'cpi',
            'GDPC1': 'gdp',
        }
        
        for series_id, name in series.items():
            try:
                url = f"https://api.stlouisfed.org/fred/series/observations"
                params = {
                    'series_id': series_id,
                    'api_key': self.fred_key,
                    'file_type': 'json',
                    'limit': 1,
                    'sort_order': 'desc'
                }
                
                response = requests.get(url, params=params, timeout=5)
                data = response.json()
                
                if 'observations' in data and data['observations']:
                    value = float(data['observations'][0]['value'])
                    indicators[name] = value
                else:
                    indicators[name] = 0.0
                    
            except Exception as e:
                logger.warning(f"Failed to fetch {series_id}: {e}")
                indicators[name] = 0.0
    else:
        # Use fallback/estimated values if no FRED API key
        indicators['fed_funds_rate'] = 5.33  # Current as of Oct 2024
        indicators['unemployment'] = 3.9      # Current estimate
        indicators['cpi'] = 310.0            # Approximate CPI
        indicators['gdp'] = 27000.0          # Approximate GDP in billions
    
    # Ensure all indicators have a value
    required_indicators = [
        'vix', 'treasury_10y', 'dollar_index', 'gold', 'oil_wti',
        'fed_funds_rate', 'unemployment', 'cpi', 'gdp'
    ]
    
    for ind in required_indicators:
        if ind not in indicators:
            indicators[ind] = 0.0
    
    return indicators