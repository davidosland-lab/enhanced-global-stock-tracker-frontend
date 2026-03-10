"""
Dual Regime Analyzer
====================
Combines both Multi-Factor and HMM regime detection for comprehensive market analysis.

This module provides a unified interface that runs BOTH detection methods and combines
their insights to provide:
- Multi-factor: WHY regimes occur + sector-specific guidance
- HMM: WHEN regimes will change + probabilistic crash risk

All three pipelines (AU, UK, US) use this for comprehensive regime intelligence.

Author: Unified Trading System v1.3.15.176
Date: February 23, 2026
"""

import logging
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class DualRegimeAnalyzer:
    """
    Unified Regime Analyzer combining Multi-Factor and HMM approaches
    
    Provides comprehensive regime intelligence by running both:
    1. Multi-Factor Detection (EventGuard) - Explains WHY + Sector impacts
    2. HMM Detection (Optional) - Predicts WHEN + Probabilistic risk
    
    Output combines both analyses for superior trading insights.
    """
    
    def __init__(self, market: str = 'AU'):
        """
        Initialize Dual Regime Analyzer
        
        Args:
            market: Market identifier ('AU', 'US', 'UK')
        """
        self.market = market
        self.event_guard = None
        self.hmm_engine = None
        
        # Initialize Multi-Factor (EventGuard)
        try:
            from .event_risk_guard import EventRiskGuard
            self.event_guard = EventRiskGuard(market=market)
            logger.info(f"[OK] Multi-Factor regime detection initialized for {market}")
        except Exception as e:
            logger.warning(f"Multi-Factor detection unavailable: {e}")
        
        # Initialize HMM (market-specific)
        try:
            if market == 'US':
                from .us_market_regime_engine import USMarketRegimeEngine
                self.hmm_engine = USMarketRegimeEngine()
                logger.info(f"[OK] HMM regime detection initialized for US")
            elif market in ['AU', 'UK']:
                # Create HMM engine for AU/UK based on their primary indices
                from .us_market_regime_engine import USMarketRegimeEngine
                # Adapt for AU (^AXJO) or UK (^FTSE)
                index_map = {'AU': '^AXJO', 'UK': '^FTSE'}
                self.hmm_engine = USMarketRegimeEngine()
                self.hmm_engine.index_symbol = index_map.get(market, '^AXJO')
                logger.info(f"[OK] HMM regime detection initialized for {market} ({self.hmm_engine.index_symbol})")
        except Exception as e:
            logger.warning(f"HMM detection unavailable for {market}: {e}")
    
    def analyze(self) -> Dict:
        """
        Perform comprehensive dual-method regime analysis
        
        Returns:
            Dictionary containing:
            {
                'multi_factor': {...},  # Multi-factor analysis results
                'hmm': {...},           # HMM analysis results
                'combined': {...},      # Unified insights
                'timestamp': str
            }
        """
        logger.info(f"[DUAL] Running comprehensive regime analysis for {self.market}...")
        
        result = {
            'market': self.market,
            'timestamp': datetime.now().isoformat(),
            'multi_factor': None,
            'hmm': None,
            'combined': {},
            'methods_available': {
                'multi_factor': self.event_guard is not None,
                'hmm': self.hmm_engine is not None
            }
        }
        
        # Run Multi-Factor Analysis
        if self.event_guard:
            try:
                # Refresh market data for accurate analysis
                if hasattr(self.event_guard, 'refresh_market_data'):
                    self.event_guard.refresh_market_data()
                
                # Get regime analysis
                mf_result = self.event_guard.get_latest_regime()
                result['multi_factor'] = mf_result
                logger.info(f"[MF] Multi-Factor: {mf_result.get('regime_label', 'N/A')} | "
                          f"Risk: {mf_result.get('crash_risk_score', 0):.1%}")
            except Exception as e:
                logger.error(f"Multi-Factor analysis failed: {e}")
                result['multi_factor'] = {'error': str(e)}
        
        # Run HMM Analysis
        if self.hmm_engine:
            try:
                hmm_result = self.hmm_engine.analyse()
                result['hmm'] = hmm_result
                logger.info(f"[HMM] Volatility: {hmm_result.get('regime_label', 'N/A')} | "
                          f"Risk: {hmm_result.get('crash_risk_score', 0):.1%} | "
                          f"Method: {hmm_result.get('method', 'N/A')}")
            except Exception as e:
                logger.error(f"HMM analysis failed: {e}")
                result['hmm'] = {'error': str(e)}
        
        # Combine insights
        result['combined'] = self._combine_analyses(
            result.get('multi_factor'),
            result.get('hmm')
        )
        
        logger.info(f"[DUAL] Combined regime: {result['combined'].get('regime_summary', 'N/A')}")
        return result
    
    def _combine_analyses(self, multi_factor: Optional[Dict], hmm: Optional[Dict]) -> Dict:
        """
        Combine Multi-Factor and HMM analyses into unified insights
        
        Args:
            multi_factor: Multi-factor analysis results
            hmm: HMM analysis results
            
        Returns:
            Combined analysis with unified insights
        """
        combined = {
            'regime_summary': 'Unknown',
            'crash_risk_combined': 0.0,
            'confidence': 'UNKNOWN',
            'trading_guidance': [],
            'warnings': []
        }
        
        # Extract regime labels
        mf_regime = multi_factor.get('regime_label', 'UNKNOWN') if multi_factor else 'UNKNOWN'
        hmm_regime = hmm.get('regime_label', 'unknown') if hmm else 'unknown'
        
        # Extract crash risks
        mf_risk = multi_factor.get('crash_risk_score', 0.0) if multi_factor else 0.0
        hmm_risk = hmm.get('crash_risk_score', 0.0) if hmm else 0.0
        
        # Combine regime summary
        if multi_factor and hmm:
            combined['regime_summary'] = f"{mf_regime} (Multi-Factor) | {hmm_regime.upper()} (HMM)"
            
            # Weight crash risks (Multi-factor 60%, HMM 40% - multi-factor more comprehensive)
            combined['crash_risk_combined'] = (mf_risk * 0.6) + (hmm_risk * 0.4)
            
            # Determine confidence based on agreement
            if self._regimes_agree(mf_regime, hmm_regime, mf_risk, hmm_risk):
                combined['confidence'] = 'HIGH'
                combined['trading_guidance'].append("[OK] Both methods agree - high confidence signals")
            else:
                combined['confidence'] = 'MEDIUM'
                combined['warnings'].append("[!] Methods show divergence - proceed with caution")
        
        elif multi_factor:
            combined['regime_summary'] = f"{mf_regime} (Multi-Factor only)"
            combined['crash_risk_combined'] = mf_risk
            combined['confidence'] = 'MEDIUM'
            combined['warnings'].append("HMM not available - using Multi-Factor only")
        
        elif hmm:
            combined['regime_summary'] = f"{hmm_regime.upper()} (HMM only)"
            combined['crash_risk_combined'] = hmm_risk
            combined['confidence'] = 'MEDIUM'
            combined['warnings'].append("Multi-Factor not available - using HMM only")
        
        # Add sector guidance from multi-factor
        if multi_factor and 'sector_impacts' in multi_factor:
            combined['sector_impacts'] = multi_factor['sector_impacts']
        
        # Add transition warnings from HMM
        if hmm and hmm.get('method') == 'HMM':
            probs = hmm.get('state_probabilities', {})
            high_vol_prob = probs.get('high_vol', 0.0)
            if high_vol_prob > 0.15:
                combined['warnings'].append(f"[!] HMM: {high_vol_prob:.0%} probability of high volatility state")
        
        # Trading guidance based on combined risk
        risk = combined['crash_risk_combined']
        if risk < 0.10:
            combined['trading_guidance'].append("[OK] Low risk environment - normal position sizing")
        elif risk < 0.25:
            combined['trading_guidance'].append("[!] Moderate risk - consider reducing leverage")
        else:
            combined['trading_guidance'].append("[ALERT] High risk - reduce exposure, raise cash")
        
        return combined
    
    def _regimes_agree(self, mf_regime: str, hmm_regime: str, mf_risk: float, hmm_risk: float) -> bool:
        """
        Check if Multi-Factor and HMM regimes are in agreement
        
        Args:
            mf_regime: Multi-factor regime label
            hmm_regime: HMM regime label
            mf_risk: Multi-factor crash risk
            hmm_risk: HMM crash risk
            
        Returns:
            True if regimes broadly agree, False otherwise
        """
        # Map regimes to risk levels
        mf_is_bullish = any(x in mf_regime.upper() for x in ['BULL', 'RISK_ON', 'RALLY', 'STRONG'])
        mf_is_bearish = any(x in mf_regime.upper() for x in ['BEAR', 'RISK_OFF', 'WEAK', 'CRASH'])
        
        hmm_is_low_vol = hmm_regime in ['low_vol', 'LOW_VOL']
        hmm_is_high_vol = hmm_regime in ['high_vol', 'HIGH_VOL']
        
        # Check risk alignment
        both_low_risk = (mf_risk < 0.20 and hmm_risk < 0.20)
        both_high_risk = (mf_risk > 0.30 and hmm_risk > 0.30)
        
        # Check regime alignment
        bullish_and_low_vol = (mf_is_bullish and hmm_is_low_vol)
        bearish_and_high_vol = (mf_is_bearish and hmm_is_high_vol)
        
        # Agreement if risks align OR regimes align
        return both_low_risk or both_high_risk or bullish_and_low_vol or bearish_and_high_vol
    
    def get_trading_guidance(self) -> Dict:
        """
        Get actionable trading guidance based on current regime analysis
        
        Returns:
            Dictionary with trading recommendations
        """
        analysis = self.analyze()
        combined = analysis.get('combined', {})
        
        guidance = {
            'regime': combined.get('regime_summary', 'Unknown'),
            'crash_risk': combined.get('crash_risk_combined', 0.0),
            'confidence': combined.get('confidence', 'UNKNOWN'),
            'position_sizing': self._get_position_sizing(combined.get('crash_risk_combined', 0.0)),
            'sector_focus': self._get_sector_focus(analysis.get('multi_factor')),
            'timing_guidance': self._get_timing_guidance(analysis.get('hmm')),
            'warnings': combined.get('warnings', []),
            'recommendations': combined.get('trading_guidance', [])
        }
        
        return guidance
    
    def _get_position_sizing(self, risk: float) -> str:
        """Get position sizing recommendation based on crash risk"""
        if risk < 0.10:
            return "Normal (100% allocation)"
        elif risk < 0.20:
            return "Cautious (80% allocation)"
        elif risk < 0.30:
            return "Defensive (60% allocation)"
        else:
            return "Minimal (30-40% allocation, raise cash)"
    
    def _get_sector_focus(self, multi_factor: Optional[Dict]) -> str:
        """Get sector focus from multi-factor analysis"""
        if not multi_factor or 'sector_impacts' not in multi_factor:
            return "Not available"
        
        impacts = multi_factor['sector_impacts']
        if not impacts:
            return "Neutral - no strong sector signals"
        
        # Find best and worst sectors
        sorted_sectors = sorted(impacts.items(), key=lambda x: x[1], reverse=True)
        
        if sorted_sectors:
            best = sorted_sectors[0]
            worst = sorted_sectors[-1]
            return f"Favor: {best[0]} ({best[1]:+.1f}) | Avoid: {worst[0]} ({worst[1]:+.1f})"
        
        return "Neutral"
    
    def _get_timing_guidance(self, hmm: Optional[Dict]) -> str:
        """Get timing guidance from HMM analysis"""
        if not hmm:
            return "Not available"
        
        method = hmm.get('method', 'Unknown')
        if method == 'Fallback':
            return "Using volatility thresholds (HMM not installed)"
        
        # Check for transition warnings
        probs = hmm.get('state_probabilities', {})
        medium_vol = probs.get('medium_vol', 0.0)
        high_vol = probs.get('high_vol', 0.0)
        
        if high_vol > 0.25:
            return f"[!] Transition warning: {high_vol:.0%} high-vol probability - expect volatility"
        elif medium_vol > 0.40 and high_vol > 0.15:
            return f"Caution: Regime may be shifting (medium {medium_vol:.0%}, high {high_vol:.0%})"
        else:
            return "Stable regime - no transition warning"


if __name__ == "__main__":
    # Test Dual Regime Analyzer
    print("\n" + "="*80)
    print("DUAL REGIME ANALYZER TEST")
    print("="*80)
    
    for market in ['AU', 'UK', 'US']:
        print(f"\n[{market}] Testing Dual Regime Analysis...")
        analyzer = DualRegimeAnalyzer(market=market)
        
        print(f"\n[{market}] Running analysis...")
        result = analyzer.analyze()
        
        print(f"\n[{market}] Results:")
        mf = result.get('multi_factor') or {}
        hmm = result.get('hmm') or {}
        combined = result.get('combined') or {}
        
        print(f"   Multi-Factor: {mf.get('regime_label', 'N/A')}")
        print(f"   HMM: {hmm.get('regime_label', 'N/A')}")
        print(f"   Combined: {combined.get('regime_summary', 'N/A')}")
        print(f"   Crash Risk: {combined.get('crash_risk_combined', 0):.1%}")
        print(f"   Confidence: {combined.get('confidence', 'N/A')}")
        
        print(f"\n[{market}] Trading Guidance:")
        guidance = analyzer.get_trading_guidance()
        print(f"   Position Sizing: {guidance['position_sizing']}")
        print(f"   Sector Focus: {guidance['sector_focus']}")
        print(f"   Timing: {guidance['timing_guidance']}")
        
        if guidance['warnings']:
            print(f"\n[{market}] Warnings:")
            for warning in guidance['warnings']:
                print(f"     {warning}")
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)
