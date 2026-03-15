#!/usr/bin/env python3
"""
Market Regime Detection System
Identifies macro market regimes to improve stock predictions

Author: Trading System v1.3.13 - REGIME EDITION
Date: January 5, 2026
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class MarketRegime(Enum):
    """Market regime classifications"""
    # US Market Regimes
    US_TECH_RISK_ON = "US_TECH_RISK_ON"          # NASDAQ outperforming, tech-led rally
    US_TECH_RISK_OFF = "US_TECH_RISK_OFF"        # Tech selling off
    US_BROAD_RALLY = "US_BROAD_RALLY"            # S&P 500 broad rally
    US_RISK_OFF = "US_RISK_OFF"                  # Flight to safety
    
    # Commodity Regimes
    COMMODITY_STRONG = "COMMODITY_STRONG"        # Iron ore, oil, lithium up
    COMMODITY_WEAK = "COMMODITY_WEAK"            # Commodities down
    COMMODITY_MIXED = "COMMODITY_MIXED"          # Mixed signals
    
    # Rate Regimes
    RATE_CUT_EXPECTATION = "RATE_CUT_EXPECTATION"    # Market pricing rate cuts
    RATE_HIKE_FEAR = "RATE_HIKE_FEAR"                # Rate hike concerns
    RBA_HIGHER_LONGER = "RBA_HIGHER_LONGER"          # Australian rates sticky
    FED_DOVISH = "FED_DOVISH"                        # Fed dovish signals
    
    # Currency Regimes
    USD_STRENGTH = "USD_STRENGTH"                # USD up, AUD down
    USD_WEAKNESS = "USD_WEAKNESS"                # USD down, AUD up
    AUD_UNDER_PRESSURE = "AUD_UNDER_PRESSURE"    # AUD weakening vs basket
    
    # Composite Regimes
    RISK_ON_GLOBAL = "RISK_ON_GLOBAL"            # Global risk-on
    RISK_OFF_GLOBAL = "RISK_OFF_GLOBAL"          # Global risk-off
    ROTATION_VALUE = "ROTATION_VALUE"            # Value stocks outperforming
    ROTATION_GROWTH = "ROTATION_GROWTH"          # Growth stocks outperforming


class MarketRegimeDetector:
    """
    Detects market regimes based on overnight US session, commodities, rates, and FX
    
    This is CRITICAL for ASX predictions because:
    1. ASX heavily weighted to banks, resources, energy
    2. US gains often tech-led (NASDAQ) - ASX can't participate
    3. Commodity weakness hits Australia directly
    4. Rate expectations differ (RBA vs Fed)
    5. Currency effects (AUD/USD) drive flows
    6. "Buy US, sell rest" global capital rotation
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize regime detector with configuration"""
        self.config = self._load_config(config_path)
        self.thresholds = self.config.get('regime_thresholds', {})
        self.current_regime = None
        self.regime_history = []
        logger.info("[OK] MarketRegimeDetector initialized")
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load regime detection configuration"""
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        
        # Default configuration
        return {
            'regime_thresholds': {
                # US Market thresholds (% changes)
                'nasdaq_tech_threshold': 1.0,      # NASDAQ up >1% = tech rally
                'sp500_broad_threshold': 0.8,      # S&P up >0.8% = broad rally
                'nasdaq_outperformance': 0.5,      # NASDAQ - S&P >0.5% = tech-led
                
                # Commodity thresholds (% changes)
                'iron_ore_strong': 2.0,            # Iron ore up >2%
                'iron_ore_weak': -2.0,             # Iron ore down >2%
                'oil_strong': 2.0,                 # Oil up >2%
                'oil_weak': -2.0,                  # Oil down >2%
                
                # Currency thresholds (% changes)
                'aud_usd_strong': 0.5,             # AUD/USD up >0.5%
                'aud_usd_weak': -0.5,              # AUD/USD down >0.5%
                'usd_index_strong': 0.4,           # DXY up >0.4%
                
                # Rate thresholds (bps changes)
                'us_10y_cut_signal': -5,           # US 10Y down >5bps = rate cut hopes
                'us_10y_hike_signal': 5,           # US 10Y up >5bps = rate hike fears
            },
            'regime_weights': {
                # Impact weights for different regimes on ASX sectors
                'US_TECH_RISK_ON': {
                    'Financials': -0.3,      # Banks underperform (global flows to US)
                    'Materials': -0.4,       # Miners underperform (tech focus)
                    'Energy': -0.3,          # Energy underperforms
                    'Technology': 0.5,       # ASX tech benefits (small)
                    'Healthcare': 0.2,       # Healthcare neutral to positive
                },
                'COMMODITY_WEAK': {
                    'Financials': -0.2,      # Banks suffer (economy concerns)
                    'Materials': -0.8,       # Miners hit hardest
                    'Energy': -0.6,          # Energy stocks down
                    'Industrials': -0.3,     # Industrials suffer
                },
                'USD_STRENGTH': {
                    'Financials': -0.4,      # Foreign flows exit
                    'Materials': -0.3,       # Export competitiveness hit
                    'Energy': -0.3,          # Commodities priced in USD
                    'all': -0.2,             # Overall negative for ASX
                },
                'RBA_HIGHER_LONGER': {
                    'Financials': -0.5,      # Banks under pressure
                    'Consumer': -0.4,        # Consumer discretionary hurt
                    'Utilities': -0.3,       # REITs and utilities down
                    'Real Estate': -0.6,     # Property sector hammered
                },
            }
        }
    
    def detect_regime(self, market_data: Dict) -> Dict:
        """
        Detect current market regime based on overnight data
        
        Args:
            market_data: Dictionary containing:
                - sp500_change: S&P 500 % change
                - nasdaq_change: NASDAQ % change
                - iron_ore_change: Iron ore % change
                - oil_change: Oil % change
                - aud_usd_change: AUD/USD % change
                - usd_index_change: USD index % change
                - us_10y_change: US 10Y yield change (bps)
                - au_10y_change: AU 10Y yield change (bps)
                - vix_level: VIX level
                - timestamp: Data timestamp
        
        Returns:
            Dictionary containing:
                - primary_regime: Main regime classification
                - secondary_regimes: List of secondary regimes
                - regime_strength: Strength score (0-1)
                - regime_explanation: Human-readable explanation
                - sector_impacts: Expected impact by ASX sector
                - confidence: Detection confidence (0-1)
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
            vix = market_data.get('vix_level', 20)
            
            # Detect individual regime components
            us_regime = self._detect_us_market_regime(sp500, nasdaq, vix)
            commodity_regime = self._detect_commodity_regime(iron_ore, oil)
            fx_regime = self._detect_fx_regime(aud_usd, usd_index)
            rate_regime = self._detect_rate_regime(us_10y)
            
            # Combine into primary regime
            primary_regime, strength = self._determine_primary_regime(
                us_regime, commodity_regime, fx_regime, rate_regime, market_data
            )
            
            # Gather all active regimes
            all_regimes = [us_regime, commodity_regime, fx_regime, rate_regime]
            secondary_regimes = [r for r in all_regimes if r and r != primary_regime]
            
            # Calculate sector impacts
            sector_impacts = self._calculate_sector_impacts(
                primary_regime, secondary_regimes, market_data
            )
            
            # Generate explanation
            explanation = self._generate_regime_explanation(
                primary_regime, secondary_regimes, market_data
            )
            
            # Calculate confidence
            confidence = self._calculate_confidence(market_data, strength)
            
            # Store current regime
            self.current_regime = {
                'primary_regime': primary_regime,
                'secondary_regimes': secondary_regimes,
                'regime_strength': strength,
                'regime_explanation': explanation,
                'sector_impacts': sector_impacts,
                'confidence': confidence,
                'market_data': market_data,
                'timestamp': market_data.get('timestamp', datetime.now().isoformat())
            }
            
            # Update history
            self.regime_history.append(self.current_regime)
            if len(self.regime_history) > 30:  # Keep last 30 days
                self.regime_history.pop(0)
            
            logger.info(f"[OK] Regime detected: {primary_regime} (strength: {strength:.2f}, confidence: {confidence:.2f})")
            logger.info(f"   Explanation: {explanation}")
            
            return self.current_regime
            
        except Exception as e:
            logger.error(f"[X] Error detecting regime: {e}", exc_info=True)
            return self._get_default_regime()
    
    def _detect_us_market_regime(self, sp500: float, nasdaq: float, vix: float) -> Optional[MarketRegime]:
        """Detect US market regime"""
        nasdaq_threshold = self.thresholds['nasdaq_tech_threshold']
        sp500_threshold = self.thresholds['sp500_broad_threshold']
        outperformance = self.thresholds['nasdaq_outperformance']
        
        # Tech-led rally: NASDAQ up strong and outperforming S&P
        if nasdaq > nasdaq_threshold and (nasdaq - sp500) > outperformance:
            return MarketRegime.US_TECH_RISK_ON
        
        # Broad rally: S&P strong, NASDAQ not dramatically outperforming
        elif sp500 > sp500_threshold and abs(nasdaq - sp500) < outperformance:
            return MarketRegime.US_BROAD_RALLY
        
        # Risk off: Both down and VIX high
        elif sp500 < -0.5 and nasdaq < -0.5 and vix > 20:
            return MarketRegime.US_RISK_OFF
        
        # Tech selling: NASDAQ down more than S&P
        elif nasdaq < -0.5 and (sp500 - nasdaq) > outperformance:
            return MarketRegime.US_TECH_RISK_OFF
        
        return None
    
    def _detect_commodity_regime(self, iron_ore: float, oil: float) -> Optional[MarketRegime]:
        """Detect commodity regime"""
        iron_strong = self.thresholds['iron_ore_strong']
        iron_weak = self.thresholds['iron_ore_weak']
        oil_strong = self.thresholds['oil_strong']
        oil_weak = self.thresholds['oil_weak']
        
        # Both strong
        if iron_ore > iron_strong and oil > oil_strong:
            return MarketRegime.COMMODITY_STRONG
        
        # Both weak
        elif iron_ore < iron_weak and oil < oil_weak:
            return MarketRegime.COMMODITY_WEAK
        
        # One strong, one weak
        elif (iron_ore > iron_strong and oil < oil_weak) or (iron_ore < iron_weak and oil > oil_strong):
            return MarketRegime.COMMODITY_MIXED
        
        # Iron ore particularly weak (critical for Australia)
        elif iron_ore < iron_weak:
            return MarketRegime.COMMODITY_WEAK
        
        return None
    
    def _detect_fx_regime(self, aud_usd: float, usd_index: float) -> Optional[MarketRegime]:
        """Detect FX regime"""
        aud_strong = self.thresholds['aud_usd_strong']
        aud_weak = self.thresholds['aud_usd_weak']
        usd_strong = self.thresholds['usd_index_strong']
        
        # USD strengthening
        if usd_index > usd_strong or aud_usd < aud_weak:
            return MarketRegime.USD_STRENGTH
        
        # USD weakening
        elif usd_index < -usd_strong or aud_usd > aud_strong:
            return MarketRegime.USD_WEAKNESS
        
        # AUD specifically under pressure
        elif aud_usd < aud_weak:
            return MarketRegime.AUD_UNDER_PRESSURE
        
        return None
    
    def _detect_rate_regime(self, us_10y: float) -> Optional[MarketRegime]:
        """Detect rate regime"""
        cut_signal = self.thresholds['us_10y_cut_signal']
        hike_signal = self.thresholds['us_10y_hike_signal']
        
        # Rate cut expectations
        if us_10y < cut_signal:
            return MarketRegime.RATE_CUT_EXPECTATION
        
        # Rate hike fears
        elif us_10y > hike_signal:
            return MarketRegime.RATE_HIKE_FEAR
        
        return None
    
    def _determine_primary_regime(
        self, 
        us_regime: Optional[MarketRegime],
        commodity_regime: Optional[MarketRegime],
        fx_regime: Optional[MarketRegime],
        rate_regime: Optional[MarketRegime],
        market_data: Dict
    ) -> Tuple[MarketRegime, float]:
        """
        Determine primary regime and strength
        
        Priority order for ASX:
        1. Commodity regime (most direct impact)
        2. FX regime (affects flows)
        3. US regime (sentiment spillover)
        4. Rate regime (affects sectors differently)
        """
        
        # Calculate regime strength scores
        scores = {}
        
        # Commodity regime gets highest priority for ASX
        if commodity_regime:
            iron_ore = abs(market_data.get('iron_ore_change', 0))
            oil = abs(market_data.get('oil_change', 0))
            commodity_strength = min((iron_ore + oil) / 8.0, 1.0)  # Normalize to 0-1
            scores[commodity_regime] = commodity_strength * 1.5  # 50% bonus
        
        # FX regime (critical for foreign flows)
        if fx_regime:
            aud_move = abs(market_data.get('aud_usd_change', 0))
            fx_strength = min(aud_move / 1.0, 1.0)  # Normalize to 0-1
            scores[fx_regime] = fx_strength * 1.3  # 30% bonus
        
        # US regime (sentiment impact)
        if us_regime:
            nasdaq = abs(market_data.get('nasdaq_change', 0))
            sp500 = abs(market_data.get('sp500_change', 0))
            us_strength = min((nasdaq + sp500) / 4.0, 1.0)  # Normalize to 0-1
            scores[us_regime] = us_strength * 1.0  # No bonus
        
        # Rate regime (sector-specific)
        if rate_regime:
            us_10y = abs(market_data.get('us_10y_change', 0))
            rate_strength = min(us_10y / 10.0, 1.0)  # Normalize to 0-1
            scores[rate_regime] = rate_strength * 1.1  # 10% bonus
        
        # Select primary regime (highest score)
        if scores:
            primary = max(scores, key=scores.get)
            strength = min(scores[primary], 1.0)
            return primary, strength
        
        # Default to risk-off when unable to determine regime (conservative approach)
        logger.warning("[REGIME] Unable to determine regime from market data, defaulting to US_RISK_OFF")
        return MarketRegime.US_RISK_OFF, 0.3
    
    def _calculate_sector_impacts(
        self,
        primary_regime: MarketRegime,
        secondary_regimes: List[MarketRegime],
        market_data: Dict
    ) -> Dict[str, float]:
        """
        Calculate expected impact on ASX sectors
        
        Returns dict of sector -> impact score (-1 to +1)
        Negative = expected underperformance
        Positive = expected outperformance
        """
        
        sector_impacts = {
            'Financials': 0.0,
            'Materials': 0.0,
            'Energy': 0.0,
            'Healthcare': 0.0,
            'Consumer': 0.0,
            'Technology': 0.0,
            'Industrials': 0.0,
            'Utilities': 0.0,
            'Real Estate': 0.0,
        }
        
        # Apply primary regime impacts (full weight)
        primary_weights = self.config['regime_weights'].get(primary_regime.value, {})
        for sector, impact in primary_weights.items():
            if sector == 'all':
                for s in sector_impacts:
                    sector_impacts[s] += impact
            elif sector in sector_impacts:
                sector_impacts[sector] += impact
        
        # Apply secondary regime impacts (half weight)
        for regime in secondary_regimes:
            regime_weights = self.config['regime_weights'].get(regime.value, {})
            for sector, impact in regime_weights.items():
                if sector == 'all':
                    for s in sector_impacts:
                        sector_impacts[s] += impact * 0.5
                elif sector in sector_impacts:
                    sector_impacts[sector] += impact * 0.5
        
        # Clamp to -1 to +1 range
        for sector in sector_impacts:
            sector_impacts[sector] = max(-1.0, min(1.0, sector_impacts[sector]))
        
        return sector_impacts
    
    def _generate_regime_explanation(
        self,
        primary_regime: MarketRegime,
        secondary_regimes: List[MarketRegime],
        market_data: Dict
    ) -> str:
        """Generate human-readable regime explanation"""
        
        explanations = {
            MarketRegime.US_TECH_RISK_ON: "US tech-led rally (NASDAQ outperforming). ASX likely to underperform - limited tech exposure, capital flowing to US.",
            MarketRegime.US_BROAD_RALLY: "Broad US market rally. ASX may see modest gains if commodities and AUD stable.",
            MarketRegime.US_RISK_OFF: "US risk-off mode. Flight to safety - expect ASX weakness, especially resources.",
            MarketRegime.US_TECH_RISK_OFF: "US tech selling off. Limited direct impact on ASX but negative sentiment.",
            MarketRegime.COMMODITY_STRONG: "Commodities rallying strongly. Major positive for ASX miners and energy - this is when Australia outperforms.",
            MarketRegime.COMMODITY_WEAK: "Commodity weakness. Direct hit to ASX - miners, energy stocks will drag index regardless of US strength.",
            MarketRegime.COMMODITY_MIXED: "Mixed commodity signals. Selective opportunities in resources.",
            MarketRegime.RATE_CUT_EXPECTATION: "Market pricing US rate cuts. Benefits growth stocks but check RBA positioning.",
            MarketRegime.RATE_HIKE_FEAR: "Rate hike concerns rising. Negative for banks, REITs, rate-sensitive sectors.",
            MarketRegime.RBA_HIGHER_LONGER: "RBA expected to hold rates high. Pressure on banks, property, consumer discretionary.",
            MarketRegime.USD_STRENGTH: "USD strengthening / AUD falling. Foreign flows exiting ASX - broad negative pressure.",
            MarketRegime.USD_WEAKNESS: "USD weakening / AUD rising. Positive for ASX - foreign capital inflows likely.",
            MarketRegime.AUD_UNDER_PRESSURE: "AUD under significant pressure. Exporters benefit long-term but near-term equity weakness.",
        }
        
        primary_text = explanations.get(primary_regime, "Market regime unclear.")
        
        if secondary_regimes:
            secondary_texts = [
                explanations.get(r, "") for r in secondary_regimes[:2]  # Top 2 secondary
            ]
            secondary_text = " Also: " + "; ".join([t for t in secondary_texts if t])
            return primary_text + secondary_text
        
        return primary_text
    
    def _calculate_confidence(self, market_data: Dict, strength: float) -> float:
        """Calculate detection confidence based on data quality and clarity"""
        
        # Base confidence from regime strength
        confidence = strength
        
        # Boost confidence if multiple indicators align
        sp500 = market_data.get('sp500_change', 0)
        nasdaq = market_data.get('nasdaq_change', 0)
        iron_ore = market_data.get('iron_ore_change', 0)
        oil = market_data.get('oil_change', 0)
        aud_usd = market_data.get('aud_usd_change', 0)
        
        # Check for alignment
        moves = [sp500, nasdaq, iron_ore, oil, aud_usd]
        moves_nonzero = [m for m in moves if abs(m) > 0.1]
        
        if moves_nonzero:
            # If most moves point same direction, boost confidence
            positive_count = sum(1 for m in moves_nonzero if m > 0)
            negative_count = sum(1 for m in moves_nonzero if m < 0)
            alignment = max(positive_count, negative_count) / len(moves_nonzero)
            
            # Alignment bonus (up to +0.2)
            confidence += alignment * 0.2
        
        # Reduce confidence if VIX is very high (uncertainty)
        vix = market_data.get('vix_level', 20)
        if vix > 30:
            confidence -= 0.15
        elif vix > 25:
            confidence -= 0.1
        
        # Clamp to 0-1
        return max(0.0, min(1.0, confidence))
    
    def _get_default_regime(self) -> Dict:
        """Return default regime for error cases"""
        return {
            'primary_regime': MarketRegime.US_BROAD_RALLY,
            'secondary_regimes': [],
            'regime_strength': 0.3,
            'regime_explanation': "Default regime - insufficient data",
            'sector_impacts': {},
            'confidence': 0.1,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_sector_adjustment(self, sector: str) -> float:
        """
        Get regime-based adjustment for a specific sector
        
        Args:
            sector: Sector name (e.g., 'Financials', 'Materials')
        
        Returns:
            Adjustment factor (-1 to +1)
            Negative = reduce opportunity score
            Positive = boost opportunity score
        """
        if not self.current_regime:
            return 0.0
        
        return self.current_regime.get('sector_impacts', {}).get(sector, 0.0)
    
    def should_trade_today(self, sector: str) -> bool:
        """
        Determine if today is favorable for trading a given sector
        
        Returns True if sector_adjustment > -0.3
        """
        adjustment = self.get_sector_adjustment(sector)
        return adjustment > -0.3
    
    def get_regime_report(self) -> str:
        """Generate formatted regime report"""
        if not self.current_regime:
            return "No regime data available"
        
        report = []
        report.append("\n" + "="*80)
        report.append("MARKET REGIME ANALYSIS")
        report.append("="*80)
        report.append(f"Primary Regime: {self.current_regime['primary_regime'].value}")
        report.append(f"Strength: {self.current_regime['regime_strength']:.2f}")
        report.append(f"Confidence: {self.current_regime['confidence']:.2f}")
        report.append(f"\nExplanation: {self.current_regime['regime_explanation']}")
        
        if self.current_regime['secondary_regimes']:
            report.append(f"\nSecondary Regimes:")
            for regime in self.current_regime['secondary_regimes']:
                report.append(f"  - {regime.value}")
        
        report.append(f"\nSECTOR IMPACT FORECAST:")
        report.append("-" * 80)
        
        sector_impacts = self.current_regime['sector_impacts']
        # Sort by impact (most negative first, then most positive)
        sorted_sectors = sorted(sector_impacts.items(), key=lambda x: x[1])
        
        for sector, impact in sorted_sectors:
            if impact < -0.3:
                emoji = "[X]"
                label = "AVOID"
            elif impact < -0.1:
                emoji = "[!]"
                label = "CAUTION"
            elif impact > 0.3:
                emoji = "[OK]"
                label = "FAVOR"
            elif impact > 0.1:
                emoji = "[+]"
                label = "OK"
            else:
                emoji = "[-]"
                label = "NEUTRAL"
            
            report.append(f"  {emoji} {sector:20s} {impact:+.2f}  ({label})")
        
        report.append("="*80)
        
        return "\n".join(report)


def test_regime_detector():
    """Test the regime detector with sample data"""
    
    print("\n" + "="*80)
    print("TESTING MARKET REGIME DETECTOR")
    print("="*80)
    
    detector = MarketRegimeDetector()
    
    # Test scenarios
    scenarios = [
        {
            'name': "US Tech Rally, Commodities Weak",
            'data': {
                'sp500_change': 0.8,
                'nasdaq_change': 1.5,
                'iron_ore_change': -2.5,
                'oil_change': -1.8,
                'aud_usd_change': -0.6,
                'usd_index_change': 0.5,
                'us_10y_change': -3,
                'vix_level': 15,
                'timestamp': datetime.now().isoformat()
            }
        },
        {
            'name': "Commodity Boom",
            'data': {
                'sp500_change': 0.3,
                'nasdaq_change': 0.2,
                'iron_ore_change': 3.5,
                'oil_change': 2.8,
                'aud_usd_change': 0.8,
                'usd_index_change': -0.3,
                'us_10y_change': 2,
                'vix_level': 18,
                'timestamp': datetime.now().isoformat()
            }
        },
        {
            'name': "Risk Off",
            'data': {
                'sp500_change': -1.2,
                'nasdaq_change': -1.5,
                'iron_ore_change': -1.5,
                'oil_change': -2.0,
                'aud_usd_change': -0.8,
                'usd_index_change': 0.8,
                'us_10y_change': -8,
                'vix_level': 28,
                'timestamp': datetime.now().isoformat()
            }
        },
    ]
    
    for scenario in scenarios:
        print(f"\n{'='*80}")
        print(f"SCENARIO: {scenario['name']}")
        print(f"{'='*80}")
        
        result = detector.detect_regime(scenario['data'])
        print(detector.get_regime_report())
        
        print(f"\n[#] Market Data:")
        print(f"  S&P 500: {scenario['data']['sp500_change']:+.1f}%")
        print(f"  NASDAQ: {scenario['data']['nasdaq_change']:+.1f}%")
        print(f"  Iron Ore: {scenario['data']['iron_ore_change']:+.1f}%")
        print(f"  Oil: {scenario['data']['oil_change']:+.1f}%")
        print(f"  AUD/USD: {scenario['data']['aud_usd_change']:+.1f}%")
        print(f"  VIX: {scenario['data']['vix_level']:.1f}")


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    test_regime_detector()
