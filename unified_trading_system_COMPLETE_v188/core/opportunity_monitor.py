"""
Opportunity Monitor - v1.3.15.188
Monitors and filters trading opportunities based on confidence and market conditions.
v188: Confidence threshold lowered from 65.0 to 48.0
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TradingOpportunity:
    """Represents a potential trading opportunity."""
    symbol: str
    signal: str  # BUY, SELL, HOLD
    confidence: float  # 0-100
    price: float
    technical_score: float
    sentiment_score: float
    urgency: str  # CRITICAL, HIGH, MEDIUM, LOW
    timestamp: datetime
    metadata: Dict


class OpportunityMonitor:
    """
    Monitors and filters trading opportunities based on thresholds.
    v188: Updated confidence_threshold from 65.0 to 48.0
    """
    
    def __init__(
        self,
        confidence_threshold: float = 48.0,  # v188: lowered from 65.0
        max_opportunities: int = 50,
        enable_alerts: bool = True
    ):
        """
        Initialize opportunity monitor.
        
        Args:
            confidence_threshold: Minimum confidence to consider (default 48.0%)
            max_opportunities: Maximum opportunities to track
            enable_alerts: Enable alerting for high-priority opportunities
        """
        self.confidence_threshold = confidence_threshold
        self.max_opportunities = max_opportunities
        self.enable_alerts = enable_alerts
        
        self.opportunities: List[TradingOpportunity] = []
        self.filtered_count = 0
        self.alert_count = 0
        
        logger.info(
            f"[OpportunityMonitor] Initialized: "
            f"confidence_threshold={self.confidence_threshold}%, "
            f"max_opportunities={self.max_opportunities}"
        )
    
    def evaluate_opportunity(
        self,
        symbol: str,
        signal: str,
        confidence: float,
        price: float,
        technical_score: float = 0.0,
        sentiment_score: float = 0.0,
        metadata: Optional[Dict] = None
    ) -> Optional[TradingOpportunity]:
        """
        Evaluate if a signal represents a valid trading opportunity.
        
        Args:
            symbol: Stock symbol
            signal: Trading signal (BUY/SELL/HOLD)
            confidence: Signal confidence (0-100)
            price: Current price
            technical_score: Technical analysis score
            sentiment_score: Sentiment analysis score
            metadata: Additional metadata
            
        Returns:
            TradingOpportunity if valid, None otherwise
        """
        # Convert confidence to percentage if needed
        conf_pct = confidence * 100 if confidence <= 1.0 else confidence
        
        # Filter by confidence threshold
        if conf_pct < self.confidence_threshold:
            self.filtered_count += 1
            logger.debug(
                f"{symbol}: Filtered out - confidence {conf_pct:.1f}% < {self.confidence_threshold}%"
            )
            return None
        
        # Filter non-actionable signals
        if signal not in ['BUY', 'SELL']:
            return None
        
        # Calculate composite confidence
        composite_conf = self._calculate_composite_confidence(
            conf_pct, technical_score, sentiment_score
        )
        
        # Determine urgency level
        urgency = self._determine_urgency(composite_conf)
        
        # Create opportunity
        opportunity = TradingOpportunity(
            symbol=symbol,
            signal=signal,
            confidence=composite_conf,
            price=price,
            technical_score=technical_score,
            sentiment_score=sentiment_score,
            urgency=urgency,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        
        # Add to list
        self._add_opportunity(opportunity)
        
        # Alert if high priority
        if urgency in ['CRITICAL', 'HIGH'] and self.enable_alerts:
            self._trigger_alert(opportunity)
        
        logger.info(
            f"{symbol}: Opportunity detected - {signal} @ {composite_conf:.1f}% "
            f"confidence, urgency={urgency}"
        )
        
        return opportunity
    
    def _calculate_composite_confidence(
        self,
        base_confidence: float,
        technical_score: float,
        sentiment_score: float
    ) -> float:
        """
        Calculate composite confidence from multiple sources.
        
        Weights:
        - Base confidence: 60%
        - Technical score: 25%
        - Sentiment score: 15%
        """
        # Normalize scores to 0-100 range
        tech_normalized = (technical_score + 1) * 50  # Assumes tech score is -1 to 1
        sent_normalized = (sentiment_score + 1) * 50  # Assumes sent score is -1 to 1
        
        # Weighted average
        composite = (
            base_confidence * 0.60 +
            tech_normalized * 0.25 +
            sent_normalized * 0.15
        )
        
        # Adjust for market conditions (placeholder - would use real market data)
        market_adjustment = 0  # Could be +/- 5 based on VIX, indices, etc.
        composite += market_adjustment
        
        # Cap at 100
        return min(composite, 100.0)
    
    def _determine_urgency(self, confidence: float) -> str:
        """
        Determine urgency level based on confidence.
        
        v188 thresholds:
        - CRITICAL: >= 85%
        - HIGH: >= 75%
        - MEDIUM: >= 48%  (v188 lowered from 65%)
        - LOW: < 48%
        """
        if confidence >= 85:
            return 'CRITICAL'
        elif confidence >= 75:
            return 'HIGH'
        elif confidence >= 48.0:  # v188: lowered from 65.0
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _add_opportunity(self, opportunity: TradingOpportunity):
        """Add opportunity to the tracking list."""
        # Remove oldest if at capacity
        if len(self.opportunities) >= self.max_opportunities:
            self.opportunities.pop(0)
        
        self.opportunities.append(opportunity)
    
    def _trigger_alert(self, opportunity: TradingOpportunity):
        """Trigger an alert for high-priority opportunity."""
        self.alert_count += 1
        logger.warning(
            f"[ALERT] {opportunity.urgency} opportunity: "
            f"{opportunity.symbol} {opportunity.signal} @ {opportunity.confidence:.1f}% "
            f"confidence (price=${opportunity.price:.2f})"
        )
    
    def get_top_opportunities(
        self,
        limit: int = 10,
        min_urgency: Optional[str] = None
    ) -> List[TradingOpportunity]:
        """
        Get top opportunities sorted by confidence.
        
        Args:
            limit: Maximum number to return
            min_urgency: Minimum urgency level (CRITICAL, HIGH, MEDIUM, LOW)
            
        Returns:
            List of top opportunities
        """
        filtered = self.opportunities
        
        # Filter by urgency if specified
        if min_urgency:
            urgency_levels = {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
            min_level = urgency_levels.get(min_urgency, 1)
            filtered = [
                opp for opp in filtered
                if urgency_levels.get(opp.urgency, 1) >= min_level
            ]
        
        # Sort by confidence descending
        sorted_opps = sorted(
            filtered,
            key=lambda x: x.confidence,
            reverse=True
        )
        
        return sorted_opps[:limit]
    
    def get_statistics(self) -> Dict:
        """Get monitoring statistics."""
        return {
            'total_opportunities': len(self.opportunities),
            'filtered_count': self.filtered_count,
            'alert_count': self.alert_count,
            'confidence_threshold': self.confidence_threshold,
            'urgency_breakdown': self._get_urgency_breakdown()
        }
    
    def _get_urgency_breakdown(self) -> Dict[str, int]:
        """Get count of opportunities by urgency level."""
        breakdown = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        for opp in self.opportunities:
            if opp.urgency in breakdown:
                breakdown[opp.urgency] += 1
        return breakdown
    
    def clear_old_opportunities(self, max_age_hours: int = 24):
        """Remove opportunities older than specified hours."""
        now = datetime.now()
        self.opportunities = [
            opp for opp in self.opportunities
            if (now - opp.timestamp).total_seconds() < max_age_hours * 3600
        ]
        logger.info(f"Cleared opportunities older than {max_age_hours}h")


if __name__ == '__main__':
    print("OpportunityMonitor v1.3.15.188")
    print("v188 patch: confidence_threshold = 48.0%")
    
    monitor = OpportunityMonitor()
    print(f"Confidence threshold: {monitor.confidence_threshold}%")
    print(f"Max opportunities: {monitor.max_opportunities}")
    
    # Test opportunity evaluation
    opp = monitor.evaluate_opportunity(
        symbol='AAPL',
        signal='BUY',
        confidence=52.1,
        price=150.0,
        technical_score=0.6,
        sentiment_score=0.4
    )
    
    if opp:
        print(f"\nOpportunity created: {opp.symbol} {opp.signal}")
        print(f"Confidence: {opp.confidence:.1f}%")
        print(f"Urgency: {opp.urgency}")
        print("✓ v188 patch verified: 52.1% >= 48.0% threshold")
    else:
        print("ERROR: Opportunity should have been created!")
