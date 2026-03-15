#!/usr/bin/env python3
"""
Cross-Market Feature Engineering
Adds market regime and cross-market features to improve predictions

Author: Trading System v1.3.13 - REGIME EDITION
Date: January 5, 2026
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd

logger = logging.getLogger(__name__)


class CrossMarketFeatures:
    """
    Engineers cross-market features for better stock predictions
    
    Key insight: ASX stocks don't move in isolation. They respond to:
    1. Overnight US market moves (S&P 500, NASDAQ)
    2. Commodity prices (iron ore, oil, lithium, gold)
    3. Currency movements (AUD/USD, USD index)
    4. Interest rate expectations (US 10Y, AU 10Y)
    5. Market sentiment (VIX, risk appetite)
    
    These features often explain MORE variance than technical indicators alone.
    """
    
    def __init__(self):
        """Initialize cross-market feature engineer"""
        self.cache = {}
        self.last_update = None
        logger.info("[OK] CrossMarketFeatures initialized")
    
    def add_features(self, stock_data: Dict, market_data: Dict) -> Dict:
        """
        Add cross-market features to stock data
        
        Args:
            stock_data: Individual stock data dictionary
            market_data: Market-level data (US indices, commodities, FX, rates)
        
        Returns:
            Enhanced stock_data with cross-market features
        """
        try:
            # Extract market data
            sp500 = market_data.get('sp500_change', 0)
            nasdaq = market_data.get('nasdaq_change', 0)
            iron_ore = market_data.get('iron_ore_change', 0)
            oil = market_data.get('oil_change', 0)
            aud_usd = market_data.get('aud_usd_change', 0)
            usd_index = market_data.get('usd_index_change', 0)
            us_10y = market_data.get('us_10y_change', 0)
            au_10y = market_data.get('au_10y_change', 0)
            vix = market_data.get('vix_level', 20)
            
            # Get stock sector
            sector = stock_data.get('sector', 'Unknown')
            
            # ===== MARKET-LEVEL FEATURES =====
            stock_data['us_market_features'] = {
                'sp500_change': sp500,
                'nasdaq_change': nasdaq,
                'vix_level': vix,
            }
            
            stock_data['commodity_features'] = {
                'iron_ore_change': iron_ore,
                'oil_change': oil,
            }
            
            stock_data['fx_features'] = {
                'aud_usd_change': aud_usd,
                'usd_index_change': usd_index,
            }
            
            stock_data['rate_features'] = {
                'us_10y_change': us_10y,
                'au_10y_change': au_10y,
                'rate_spread': au_10y - us_10y,  # AU-US spread
            }
            
            # ===== DERIVED FEATURES (Most Powerful) =====
            
            # 1. ASX Relative Bias
            #    Measures how much ASX is disadvantaged vs US tech rally
            #    High positive = US tech strong, commodities weak = bad for ASX
            asx_relative_bias = nasdaq - iron_ore
            stock_data['asx_relative_bias'] = asx_relative_bias
            
            # 2. USD Pressure Index
            #    Combines USD strength signals
            #    High = USD strong = negative for ASX
            usd_pressure = usd_index - aud_usd  # Higher = worse for ASX
            stock_data['usd_pressure'] = usd_pressure
            
            # 3. Commodity Momentum
            #    Average of key commodities
            #    Critical for Australian materials/energy sectors
            commodity_momentum = (iron_ore + oil) / 2.0
            stock_data['commodity_momentum'] = commodity_momentum
            
            # 4. Risk Appetite Score
            #    Combines multiple risk signals
            #    Positive = risk-on, Negative = risk-off
            risk_appetite = (sp500 + nasdaq) / 2.0 - (vix - 20) / 10.0
            stock_data['risk_appetite'] = risk_appetite
            
            # 5. Rate Divergence
            #    Measures AU vs US rate expectations divergence
            #    Large positive = AU rates rising relative to US = negative for ASX
            rate_divergence = (au_10y - us_10y)
            stock_data['rate_divergence'] = rate_divergence
            
            # ===== SECTOR-SPECIFIC FEATURES =====
            
            # Materials sector - highly commodity-sensitive
            if sector == 'Materials':
                stock_data['sector_tailwind'] = iron_ore * 1.5 + oil * 0.5  # Iron ore matters most
                stock_data['sector_headwind'] = usd_pressure * 0.8 + asx_relative_bias * 0.5
            
            # Energy sector - oil-driven
            elif sector == 'Energy':
                stock_data['sector_tailwind'] = oil * 1.5 + commodity_momentum * 0.5
                stock_data['sector_headwind'] = usd_pressure * 0.6
            
            # Financials - rate-sensitive, flow-sensitive
            elif sector == 'Financials':
                stock_data['sector_tailwind'] = 0 if rate_divergence < 0 else -rate_divergence * 2  # Higher AU rates = bad
                stock_data['sector_headwind'] = usd_pressure * 1.2 + asx_relative_bias * 0.8  # Flow concerns
            
            # Technology - benefits from NASDAQ strength but ASX tech small
            elif sector == 'Technology':
                stock_data['sector_tailwind'] = nasdaq * 0.5  # Modest benefit
                stock_data['sector_headwind'] = usd_pressure * 0.3  # Less sensitive
            
            # Healthcare - defensive, less market-sensitive
            elif sector == 'Healthcare':
                stock_data['sector_tailwind'] = 0 if risk_appetite < 0 else risk_appetite * 0.3
                stock_data['sector_headwind'] = usd_pressure * 0.4  # Moderate FX impact
            
            # Consumer - rate-sensitive, sentiment-driven
            elif sector == 'Consumer':
                stock_data['sector_tailwind'] = risk_appetite * 0.8
                stock_data['sector_headwind'] = rate_divergence * 1.0 + usd_pressure * 0.5
            
            # Utilities / Real Estate - highly rate-sensitive
            elif sector in ['Utilities', 'Real Estate']:
                stock_data['sector_tailwind'] = 0 if rate_divergence > 0 else -rate_divergence * 1.5
                stock_data['sector_headwind'] = (au_10y if au_10y > 0 else 0) * 2.0  # Rising rates = very bad
            
            # Industrials - broad exposure
            elif sector == 'Industrials':
                stock_data['sector_tailwind'] = risk_appetite * 0.6 + commodity_momentum * 0.4
                stock_data['sector_headwind'] = usd_pressure * 0.7
            
            # Default
            else:
                stock_data['sector_tailwind'] = risk_appetite * 0.5
                stock_data['sector_headwind'] = usd_pressure * 0.5
            
            # ===== NET SECTOR BIAS =====
            # Combined tailwind/headwind score
            net_sector_bias = stock_data.get('sector_tailwind', 0) - stock_data.get('sector_headwind', 0)
            stock_data['net_sector_bias'] = net_sector_bias
            
            # ===== OPPORTUNITY ADJUSTMENT =====
            # This will be used to adjust opportunity scores
            # Positive = boost score, Negative = penalize score
            opportunity_adjustment = (
                net_sector_bias * 0.4 +          # Sector-specific factors (40%)
                commodity_momentum * 0.3 +       # Commodity momentum (30%)
                -usd_pressure * 0.2 +            # USD pressure (20% penalty)
                risk_appetite * 0.1              # Risk appetite (10%)
            )
            stock_data['opportunity_adjustment'] = opportunity_adjustment
            
            logger.debug(f"  Added cross-market features for {stock_data.get('symbol', 'UNKNOWN')}")
            logger.debug(f"    ASX bias: {asx_relative_bias:.2f}, USD pressure: {usd_pressure:.2f}")
            logger.debug(f"    Net sector bias: {net_sector_bias:.2f}, Adjustment: {opportunity_adjustment:.2f}")
            
            return stock_data
            
        except Exception as e:
            logger.error(f"[X] Error adding cross-market features: {e}", exc_info=True)
            # Return original data if feature engineering fails
            return stock_data
    
    def add_features_batch(self, stocks: List[Dict], market_data: Dict) -> List[Dict]:
        """
        Add cross-market features to a batch of stocks
        
        Args:
            stocks: List of stock data dictionaries
            market_data: Market-level data
        
        Returns:
            List of enhanced stock data dictionaries
        """
        logger.info(f"[TOOL] Adding cross-market features to {len(stocks)} stocks...")
        
        enhanced_stocks = []
        for stock in stocks:
            enhanced = self.add_features(stock, market_data)
            enhanced_stocks.append(enhanced)
        
        logger.info(f"[OK] Added cross-market features to {len(enhanced_stocks)} stocks")
        return enhanced_stocks
    
    def calculate_correlation_matrix(self, stocks: List[Dict]) -> pd.DataFrame:
        """
        Calculate correlation between cross-market features and stock returns
        
        Useful for understanding which features matter most
        """
        try:
            # Extract features and returns
            data = []
            for stock in stocks:
                row = {
                    'return': stock.get('return', 0),
                    'asx_relative_bias': stock.get('asx_relative_bias', 0),
                    'usd_pressure': stock.get('usd_pressure', 0),
                    'commodity_momentum': stock.get('commodity_momentum', 0),
                    'risk_appetite': stock.get('risk_appetite', 0),
                    'rate_divergence': stock.get('rate_divergence', 0),
                    'net_sector_bias': stock.get('net_sector_bias', 0),
                }
                data.append(row)
            
            df = pd.DataFrame(data)
            corr_matrix = df.corr()
            
            logger.info("[#] Feature correlation with returns:")
            return_corr = corr_matrix['return'].sort_values(ascending=False)
            for feature, corr in return_corr.items():
                if feature != 'return':
                    logger.info(f"  {feature:25s}: {corr:+.3f}")
            
            return corr_matrix
            
        except Exception as e:
            logger.error(f"[X] Error calculating correlations: {e}")
            return pd.DataFrame()


def test_cross_market_features():
    """Test cross-market feature engineering"""
    
    print("\n" + "="*80)
    print("TESTING CROSS-MARKET FEATURE ENGINEERING")
    print("="*80)
    
    engineer = CrossMarketFeatures()
    
    # Sample market data (US tech rally, commodities weak)
    market_data = {
        'sp500_change': 0.8,
        'nasdaq_change': 1.5,
        'iron_ore_change': -2.5,
        'oil_change': -1.8,
        'aud_usd_change': -0.6,
        'usd_index_change': 0.5,
        'us_10y_change': -3,
        'au_10y_change': -1,
        'vix_level': 15,
    }
    
    # Sample stocks from different sectors
    stocks = [
        {
            'symbol': 'BHP.AX',
            'name': 'BHP Group',
            'sector': 'Materials',
            'price': 45.20,
        },
        {
            'symbol': 'CBA.AX',
            'name': 'Commonwealth Bank',
            'sector': 'Financials',
            'price': 105.50,
        },
        {
            'symbol': 'WDS.AX',
            'name': 'Woodside Energy',
            'sector': 'Energy',
            'price': 28.50,
        },
        {
            'symbol': 'CSL.AX',
            'name': 'CSL Limited',
            'sector': 'Healthcare',
            'price': 285.00,
        },
    ]
    
    # Add features
    enhanced_stocks = engineer.add_features_batch(stocks, market_data)
    
    # Display results
    for stock in enhanced_stocks:
        print(f"\n{'='*80}")
        print(f"Stock: {stock['symbol']} - {stock['name']} ({stock['sector']})")
        print(f"{'='*80}")
        print(f"\n[#] Market-Level Features:")
        print(f"  US Market: S&P {market_data['sp500_change']:+.1f}%, NASDAQ {market_data['nasdaq_change']:+.1f}%")
        print(f"  Commodities: Iron ore {market_data['iron_ore_change']:+.1f}%, Oil {market_data['oil_change']:+.1f}%")
        print(f"  FX: AUD/USD {market_data['aud_usd_change']:+.1f}%, USD Index {market_data['usd_index_change']:+.1f}%")
        
        print(f"\n[TOOL] Derived Features:")
        print(f"  ASX Relative Bias:    {stock.get('asx_relative_bias', 0):+.2f}  (NASDAQ - Iron ore)")
        print(f"  USD Pressure:         {stock.get('usd_pressure', 0):+.2f}  (USD strength)")
        print(f"  Commodity Momentum:   {stock.get('commodity_momentum', 0):+.2f}  (Avg commodities)")
        print(f"  Risk Appetite:        {stock.get('risk_appetite', 0):+.2f}  (Risk-on/off)")
        print(f"  Rate Divergence:      {stock.get('rate_divergence', 0):+.2f}  (AU-US spread)")
        
        print(f"\n[*] Sector-Specific:")
        print(f"  Sector Tailwind:      {stock.get('sector_tailwind', 0):+.2f}")
        print(f"  Sector Headwind:      {stock.get('sector_headwind', 0):+.2f}")
        print(f"  Net Sector Bias:      {stock.get('net_sector_bias', 0):+.2f}")
        
        print(f"\n[i] Opportunity Adjustment: {stock.get('opportunity_adjustment', 0):+.2f}")
        
        # Interpretation
        adjustment = stock.get('opportunity_adjustment', 0)
        if adjustment < -0.5:
            interpretation = "[X] STRONG HEADWINDS - Reduce opportunity score significantly"
        elif adjustment < -0.2:
            interpretation = "[!] MODERATE HEADWINDS - Reduce opportunity score"
        elif adjustment > 0.5:
            interpretation = "[OK] STRONG TAILWINDS - Boost opportunity score significantly"
        elif adjustment > 0.2:
            interpretation = "[+] MODERATE TAILWINDS - Boost opportunity score"
        else:
            interpretation = "[-] NEUTRAL - No significant adjustment"
        
        print(f"  Interpretation: {interpretation}")


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    test_cross_market_features()
