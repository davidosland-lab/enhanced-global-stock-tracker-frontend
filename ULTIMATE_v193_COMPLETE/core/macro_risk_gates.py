"""
Macro Risk Gates - v193.9 Critical Trading Risk Protection
==========================================================

Prevents catastrophic losses by blocking trades during extreme risk conditions.

CRITICAL FIX for v193.9:
- Addresses issue where financials were bought during:
  * World Risk 100/100 (EXTREME - nuclear threat)
  * US markets down -2.47% to -2.74%
  * VIX 59.3 (elevated fear)
  * No FinBERT sentiment data (blind trading)
  
Result: All 3 positions underwater (-0.56% portfolio, USD556 loss)

This module implements 4 critical macro risk gates:
1. World Event Risk gate (block if >80/100)
2. US Market Performance gate (block if down >1.5%)
3. VIX Volatility gate (require 70%+ confidence if VIX >30)
4. Sector-Specific gate (no financials during risk-off)

Author: Enhanced Global Stock Tracker
Version: v193.9
Date: March 4, 2026
"""

import logging
from typing import Dict, Tuple, Optional
from datetime import datetime, timedelta
import yfinance as yf

logger = logging.getLogger(__name__)


class MacroRiskGatekeeper:
    """
    Macro risk gatekeeper - prevents trading during extreme risk conditions
    
    Gates are evaluated in order of severity:
    1. World Event Risk (most critical)
    2. US Market Performance  
    3. VIX Volatility
    4. Sector-Specific Rules
    
    Each gate can:
    - BLOCK the trade entirely (return False)
    - REDUCE position size (return multiplier <1.0)
    - ALLOW with normal sizing (return multiplier 1.0)
    """
    
    # Financial sector symbols (banks, insurance sensitive to market)
    FINANCIAL_SECTORS = [
        # US Banks
        'JPM', 'BAC', 'WFC', 'C', 'GS', 'MS', 'USB', 'PNC', 'TFC', 'COF',
        # US Insurance
        'BRK-B', 'BRK.B', 'PGR', 'TRV', 'ALL', 'MET', 'PRU', 'AIG', 'AFL', 'HIG',
        # Australian Banks
        'CBA.AX', 'NAB.AX', 'WBC.AX', 'ANZ.AX', 'BOQ.AX', 'BEN.AX',
        # UK Banks
        'HSBA.L', 'LLOY.L', 'BARC.L', 'NWG.L', 'STAN.L',
        # UK Insurance
        'LGEN.L', 'PRU.L', 'AVAV.L', 'RSA.L',
        # Energy (correlated with market during crises)
        'XOM', 'CVX', 'BP', 'BP.L', 'SHEL.L', 'RDS-A', 'RDS-B', 'COP', 'EOG'
    ]
    
    def __init__(
        self,
        world_risk_threshold: int = 80,
        us_market_threshold: float = -1.5,
        vix_threshold: float = 30.0,
        vix_confidence_required: float = 0.70,
        financial_world_risk_threshold: int = 60,
        financial_us_market_threshold: float = -1.0
    ):
        """
        Initialize macro risk gatekeeper
        
        Args:
            world_risk_threshold: World risk above this blocks all trades (default: 80/100)
            us_market_threshold: US market change% below this blocks trades (default: -1.5%)
            vix_threshold: VIX above this requires higher confidence (default: 30)
            vix_confidence_required: Min confidence needed when VIX elevated (default: 70%)
            financial_world_risk_threshold: World risk above this blocks financials (default: 60/100)
            financial_us_market_threshold: US change below this blocks financials (default: -1.0%)
        """
        self.world_risk_threshold = world_risk_threshold
        self.us_market_threshold = us_market_threshold
        self.vix_threshold = vix_threshold
        self.vix_confidence_required = vix_confidence_required
        self.financial_world_risk_threshold = financial_world_risk_threshold
        self.financial_us_market_threshold = financial_us_market_threshold
        
        # Cache for market data (avoid repeated API calls)
        self._cache = {}
        self._cache_timestamp = None
        self._cache_duration = timedelta(minutes=5)
        
        logger.info("[RISK GATES] Macro risk gatekeeper initialized")
        logger.info(f"  World Risk threshold: {world_risk_threshold}/100")
        logger.info(f"  US Market threshold: {us_market_threshold}%")
        logger.info(f"  VIX threshold: {vix_threshold}")
        logger.info(f"  Financial restrictions: World Risk >{financial_world_risk_threshold}, US <{financial_us_market_threshold}%")
    
    def should_allow_new_position(
        self,
        symbol: str,
        signal: Dict,
        confidence: float,
        world_risk_score: Optional[float] = None,
        us_market_change: Optional[float] = None,
        vix: Optional[float] = None
    ) -> Tuple[bool, float, str]:
        """
        Check if new position should be allowed based on macro risk conditions
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'CBA.AX', 'BP.L')
            signal: Trading signal dictionary
            confidence: Signal confidence (0.0-1.0)
            world_risk_score: World event risk score 0-100 (None = fetch from report)
            us_market_change: US market overnight change % (None = fetch live)
            vix: VIX volatility index (None = fetch live)
        
        Returns:
            Tuple of (allow_trade, position_multiplier, reason)
            - allow_trade (bool): Whether to proceed with trade
            - position_multiplier (float): 0.0 to 1.0 for position sizing
            - reason (str): Detailed explanation of decision
        """
        # Get macro context
        if world_risk_score is None:
            world_risk_score = self._get_world_risk_score()
        
        if us_market_change is None:
            us_market_change = self._get_us_overnight_performance()
        
        if vix is None:
            vix = self._get_vix()
        
        # Determine if symbol is in financial sector
        is_financial = self._is_financial_sector(symbol)
        sector_label = "FINANCIAL" if is_financial else "NON-FINANCIAL"
        
        logger.debug(
            f"[RISK CHECK] {symbol} ({sector_label}): "
            f"World Risk={world_risk_score:.0f}/100, US={us_market_change:+.2f}%, VIX={vix:.1f}, "
            f"Confidence={confidence:.0%}"
        )
        
        # =================================================================
        # GATE 1: World Event Risk (HIGHEST PRIORITY)
        # =================================================================
        if world_risk_score >= self.world_risk_threshold:
            reason = (
                f"[U+1F6AB] EXTREME WORLD RISK: {world_risk_score:.0f}/100 >= {self.world_risk_threshold} "
                f"(nuclear threat or major geopolitical event) - NO NEW POSITIONS"
            )
            logger.warning(f"[GATE 1 BLOCKED] {symbol}: {reason}")
            return False, 0.0, reason
        
        # Moderate world risk: reduce position size
        if world_risk_score >= 60:
            reduction = 0.50  # 50% reduction
            reason = (
                f"[!] HIGH WORLD RISK: {world_risk_score:.0f}/100 >= 60 "
                f"- REDUCE position to {reduction:.0%}"
            )
            logger.warning(f"[GATE 1 REDUCE] {symbol}: {reason}")
            # Continue to other gates but with reduced position
        else:
            reduction = 1.0  # No reduction from world risk
        
        # =================================================================
        # GATE 2: US Market Performance (CRITICAL FOR ASX/UK)
        # =================================================================
        if us_market_change <= self.us_market_threshold:
            reason = (
                f"[U+1F6AB] US MARKET SELLOFF: {us_market_change:+.2f}% <= {self.us_market_threshold}% "
                f"- Risk-off environment, NO NEW POSITIONS"
            )
            logger.warning(f"[GATE 2 BLOCKED] {symbol}: {reason}")
            return False, 0.0, reason
        
        # Moderate US decline: reduce position
        if us_market_change <= -0.75:
            us_reduction = 0.75  # 25% reduction
            reduction *= us_reduction
            logger.warning(
                f"[GATE 2 REDUCE] {symbol}: US market {us_market_change:+.2f}% "
                f"- REDUCE position by {1-us_reduction:.0%}"
            )
        
        # =================================================================
        # GATE 3: VIX Volatility (Fear Index)
        # =================================================================
        if vix >= self.vix_threshold:
            if confidence < self.vix_confidence_required:
                reason = (
                    f"[U+1F6AB] HIGH VIX + LOW CONFIDENCE: VIX={vix:.1f} >= {self.vix_threshold} "
                    f"requires {self.vix_confidence_required:.0%}+ confidence, got {confidence:.0%}"
                )
                logger.warning(f"[GATE 3 BLOCKED] {symbol}: {reason}")
                return False, 0.0, reason
            else:
                # High VIX but sufficient confidence: reduce position
                vix_reduction = 0.75  # 25% reduction
                reduction *= vix_reduction
                logger.warning(
                    f"[GATE 3 REDUCE] {symbol}: VIX={vix:.1f} (elevated fear) "
                    f"- REDUCE position by {1-vix_reduction:.0%}"
                )
        
        # =================================================================
        # GATE 4: Sector-Specific Rules (FINANCIALS)
        # =================================================================
        if is_financial:
            # Financials are HIGHEST BETA - most sensitive to market conditions
            # Block financials at lower thresholds than general market
            
            # Check world risk for financials
            if world_risk_score >= self.financial_world_risk_threshold:
                reason = (
                    f"[U+1F6AB] FINANCIAL + HIGH RISK: {symbol} is financial sector, "
                    f"World Risk {world_risk_score:.0f}/100 >= {self.financial_world_risk_threshold} "
                    f"- NO FINANCIAL POSITIONS during elevated risk"
                )
                logger.warning(f"[GATE 4 BLOCKED] {symbol}: {reason}")
                return False, 0.0, reason
            
            # Check US market for financials
            if us_market_change <= self.financial_us_market_threshold:
                reason = (
                    f"[U+1F6AB] FINANCIAL + US DECLINE: {symbol} is financial sector, "
                    f"US market {us_market_change:+.2f}% <= {self.financial_us_market_threshold}% "
                    f"- NO FINANCIAL POSITIONS during market weakness (high beta)"
                )
                logger.warning(f"[GATE 4 BLOCKED] {symbol}: {reason}")
                return False, 0.0, reason
            
            # Additional caution for financials
            if world_risk_score >= 50 or us_market_change <= -0.5:
                financial_reduction = 0.70  # 30% additional reduction for financials
                reduction *= financial_reduction
                logger.warning(
                    f"[GATE 4 REDUCE] {symbol}: Financial sector with elevated risk "
                    f"- REDUCE position by {1-financial_reduction:.0%}"
                )
        
        # =================================================================
        # ALL GATES PASSED - Compile final decision
        # =================================================================
        if reduction < 1.0:
            reason = (
                f"[OK] ALLOW with {reduction:.0%} position (World Risk: {world_risk_score:.0f}/100, "
                f"US: {us_market_change:+.2f}%, VIX: {vix:.1f}, Sector: {sector_label})"
            )
            logger.info(f"[ALLOW REDUCED] {symbol}: {reason}")
            return True, reduction, reason
        else:
            reason = (
                f"[OK] ALLOW with full position (World Risk: {world_risk_score:.0f}/100, "
                f"US: {us_market_change:+.2f}%, VIX: {vix:.1f}, Sector: {sector_label})"
            )
            logger.info(f"[ALLOW FULL] {symbol}: {reason}")
            return True, 1.0, reason
    
    def _is_financial_sector(self, symbol: str) -> bool:
        """Check if symbol is in financial sector"""
        return symbol.upper() in [s.upper() for s in self.FINANCIAL_SECTORS]
    
    def _get_world_risk_score(self) -> float:
        """
        Get world event risk score from morning report
        
        Returns:
            World risk score 0-100 (default: 50 if unavailable)
        """
        # Check cache first
        if self._is_cache_valid():
            cached = self._cache.get('world_risk')
            if cached is not None:
                return cached
        
        try:
            # Try to read from AU morning report
            import json
            from pathlib import Path
            
            report_path = Path(__file__).parent.parent / 'reports' / 'screening' / 'au_morning_report.json'
            
            if report_path.exists():
                with open(report_path, 'r') as f:
                    report = json.load(f)
                    
                world_risk = report.get('world_event_risk', {}).get('world_risk_score', 50.0)
                
                # Update cache
                self._cache['world_risk'] = world_risk
                self._cache_timestamp = datetime.now()
                
                logger.debug(f"[WORLD RISK] Loaded from report: {world_risk:.0f}/100")
                return world_risk
        except Exception as e:
            logger.warning(f"[WORLD RISK] Could not load from report: {e}")
        
        # Default: moderate risk
        logger.warning("[WORLD RISK] Using default: 50/100 (moderate)")
        return 50.0
    
    def _get_us_overnight_performance(self) -> float:
        """
        Get US market overnight performance (S&P 500)
        
        Returns:
            Percentage change (e.g., -2.47 for down 2.47%)
        """
        # Check cache first
        if self._is_cache_valid():
            cached = self._cache.get('us_market')
            if cached is not None:
                return cached
        
        try:
            # Fetch S&P 500 performance
            ticker = yf.Ticker('^GSPC')
            hist = ticker.history(period='5d')
            
            if not hist.empty and len(hist) >= 2:
                latest_close = hist['Close'].iloc[-1]
                previous_close = hist['Close'].iloc[-2]
                change_pct = ((latest_close - previous_close) / previous_close) * 100
                
                # Update cache
                self._cache['us_market'] = change_pct
                self._cache_timestamp = datetime.now()
                
                logger.debug(f"[US MARKET] S&P 500: {change_pct:+.2f}%")
                return change_pct
        except Exception as e:
            logger.warning(f"[US MARKET] Could not fetch data: {e}")
        
        # Default: flat
        logger.warning("[US MARKET] Using default: 0.0% (flat)")
        return 0.0
    
    def _get_vix(self) -> float:
        """
        Get VIX (volatility index / fear gauge)
        
        Returns:
            VIX value (e.g., 59.3) or default 20.0
        """
        # Check cache first
        if self._is_cache_valid():
            cached = self._cache.get('vix')
            if cached is not None:
                return cached
        
        try:
            # Fetch VIX
            ticker = yf.Ticker('^VIX')
            hist = ticker.history(period='1d')
            
            if not hist.empty:
                vix = hist['Close'].iloc[-1]
                
                # Update cache
                self._cache['vix'] = vix
                self._cache_timestamp = datetime.now()
                
                logger.debug(f"[VIX] {vix:.1f}")
                return vix
        except Exception as e:
            logger.warning(f"[VIX] Could not fetch data: {e}")
        
        # Default: normal volatility
        logger.warning("[VIX] Using default: 20.0 (normal)")
        return 20.0
    
    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid"""
        if self._cache_timestamp is None:
            return False
        return (datetime.now() - self._cache_timestamp) < self._cache_duration
    
    def clear_cache(self):
        """Clear cached market data (force refresh)"""
        self._cache = {}
        self._cache_timestamp = None
        logger.debug("[CACHE] Cleared macro risk data cache")


# Convenience function for easy import
def create_risk_gatekeeper(**kwargs) -> MacroRiskGatekeeper:
    """Create and return a macro risk gatekeeper instance"""
    return MacroRiskGatekeeper(**kwargs)
