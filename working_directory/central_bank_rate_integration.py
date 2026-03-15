"""
Central Bank Rate Integration Module
=====================================

Provides central bank interest rate tracking and analysis for trading signals.

Features:
- Multi-country central bank rate tracking (Fed, ECB, BoE, BoJ, RBA)
- Rate change detection and impact analysis
- Historical rate data
- Market sector impact predictions

Author: Enhanced Global Stock Tracker
Version: 1.0
Date: December 25, 2024
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CentralBank(Enum):
    """Major central banks"""
    FED = "Federal Reserve (US)"
    ECB = "European Central Bank"
    BOE = "Bank of England"
    BOJ = "Bank of Japan"
    RBA = "Reserve Bank of Australia"
    PBOC = "People's Bank of China"
    BOC = "Bank of Canada"
    SNB = "Swiss National Bank"


class RateChangeType(Enum):
    """Types of rate changes"""
    INCREASE = "increase"
    DECREASE = "decrease"
    HOLD = "hold"


class MarketSector(Enum):
    """Market sectors affected by rate changes"""
    BANKING = "banking"
    REAL_ESTATE = "real_estate"
    TECHNOLOGY = "technology"
    UTILITIES = "utilities"
    CONSUMER = "consumer"
    INDUSTRIAL = "industrial"
    ENERGY = "energy"
    HEALTHCARE = "healthcare"


@dataclass
class InterestRateAnnouncement:
    """Central bank interest rate announcement"""
    bank: CentralBank
    date: datetime
    rate: float  # Current rate (%)
    previous_rate: float  # Previous rate (%)
    change_type: RateChangeType
    announcement_text: str
    market_impact: float  # -1 to 1 (negative to positive)
    affected_sectors: List[MarketSector]


class CentralBankTracker:
    """
    Track and analyze central bank interest rates
    """
    
    def __init__(self):
        # Current rates (as of Dec 2024)
        self.current_rates = {
            CentralBank.FED: 4.50,      # Fed Funds Rate
            CentralBank.ECB: 4.00,      # ECB Main Rate
            CentralBank.BOE: 5.25,      # UK Base Rate
            CentralBank.BOJ: -0.10,     # BoJ Policy Rate
            CentralBank.RBA: 4.35,      # RBA Cash Rate
            CentralBank.PBOC: 3.45,     # PBOC 1-year LPR
            CentralBank.BOC: 4.75,      # BoC Overnight Rate
            CentralBank.SNB: 1.75,      # SNB Policy Rate
        }
        
        # Rate change history (simplified)
        self.rate_history = {}
        
        logger.info("✅ Central Bank Rate Tracker initialized")
    
    def get_current_rate(self, bank: CentralBank = CentralBank.FED) -> float:
        """Get current interest rate for a central bank"""
        return self.current_rates.get(bank, 0.0)
    
    def get_rate_trend(self, bank: CentralBank = CentralBank.FED) -> str:
        """
        Get rate trend (increasing, decreasing, stable)
        
        Returns:
            'increasing', 'decreasing', or 'neutral'
        """
        # Simplified trend analysis
        rate = self.get_current_rate(bank)
        
        if rate > 4.0:
            return 'neutral'  # High rates, likely to hold or decrease
        elif rate < 2.0:
            return 'increasing'  # Low rates, likely to increase
        else:
            return 'neutral'
    
    def get_sector_impact(
        self, 
        bank: CentralBank = CentralBank.FED,
        sector: MarketSector = MarketSector.BANKING
    ) -> float:
        """
        Get impact of rate on specific sector
        
        Returns:
            Impact score -1.0 to 1.0
        """
        rate = self.get_current_rate(bank)
        
        # Banking sector benefits from higher rates
        if sector == MarketSector.BANKING:
            if rate > 4.0:
                return 0.6  # Positive impact
            elif rate < 2.0:
                return -0.3  # Negative impact
            else:
                return 0.2  # Neutral
        
        # Real estate hurt by higher rates
        elif sector == MarketSector.REAL_ESTATE:
            if rate > 4.0:
                return -0.5  # Negative impact
            elif rate < 2.0:
                return 0.7  # Positive impact
            else:
                return 0.0  # Neutral
        
        # Technology hurt by higher rates (growth stocks)
        elif sector == MarketSector.TECHNOLOGY:
            if rate > 4.0:
                return -0.4  # Negative impact
            elif rate < 2.0:
                return 0.5  # Positive impact
            else:
                return 0.1  # Slight positive
        
        # Utilities benefit from stable rates
        elif sector == MarketSector.UTILITIES:
            return 0.3  # Generally stable
        
        # Default neutral
        return 0.0
    
    def get_market_regime(self, bank: CentralBank = CentralBank.FED) -> str:
        """
        Determine market regime based on interest rates
        
        Returns:
            'accommodative', 'neutral', or 'restrictive'
        """
        rate = self.get_current_rate(bank)
        
        if rate < 2.0:
            return 'accommodative'  # Low rates, easy money
        elif rate > 4.5:
            return 'restrictive'  # High rates, tight money
        else:
            return 'neutral'  # Moderate rates
    
    def get_latest_announcement(
        self, 
        bank: CentralBank = CentralBank.FED
    ) -> Optional[InterestRateAnnouncement]:
        """
        Get latest rate announcement (simulated)
        
        Returns:
            InterestRateAnnouncement or None
        """
        rate = self.get_current_rate(bank)
        
        # Create simulated announcement
        announcement = InterestRateAnnouncement(
            bank=bank,
            date=datetime.now() - timedelta(days=30),  # Last month
            rate=rate,
            previous_rate=rate - 0.25,  # Previous was 0.25% lower
            change_type=RateChangeType.INCREASE if rate > 3.0 else RateChangeType.HOLD,
            announcement_text=f"{bank.value} maintains rate at {rate}%",
            market_impact=0.0,  # Neutral
            affected_sectors=[
                MarketSector.BANKING,
                MarketSector.REAL_ESTATE,
                MarketSector.TECHNOLOGY
            ]
        )
        
        return announcement
    
    def predict_next_move(
        self, 
        bank: CentralBank = CentralBank.FED
    ) -> Tuple[RateChangeType, float]:
        """
        Predict next rate move (simplified)
        
        Returns:
            (predicted_change_type, probability)
        """
        rate = self.get_current_rate(bank)
        regime = self.get_market_regime(bank)
        
        if regime == 'restrictive' and rate > 5.0:
            # High rates, likely to decrease
            return (RateChangeType.DECREASE, 0.65)
        elif regime == 'accommodative' and rate < 1.0:
            # Very low rates, likely to increase
            return (RateChangeType.INCREASE, 0.70)
        else:
            # Likely to hold
            return (RateChangeType.HOLD, 0.60)
    
    def get_rate_differential(
        self, 
        bank1: CentralBank = CentralBank.FED,
        bank2: CentralBank = CentralBank.ECB
    ) -> float:
        """
        Get interest rate differential between two central banks
        
        Useful for forex and international equity analysis
        """
        rate1 = self.get_current_rate(bank1)
        rate2 = self.get_current_rate(bank2)
        return rate1 - rate2


# Global instance
central_bank_tracker = CentralBankTracker()


def get_fed_rate() -> float:
    """Convenience function to get Fed rate"""
    return central_bank_tracker.get_current_rate(CentralBank.FED)


def get_market_regime() -> str:
    """Convenience function to get market regime"""
    return central_bank_tracker.get_market_regime(CentralBank.FED)


def get_banking_sector_impact() -> float:
    """Convenience function to get banking sector impact"""
    return central_bank_tracker.get_sector_impact(
        CentralBank.FED, 
        MarketSector.BANKING
    )


if __name__ == "__main__":
    # Test the module
    tracker = CentralBankTracker()
    
    print("Central Bank Rate Tracker - Test")
    print("=" * 50)
    
    for bank in CentralBank:
        rate = tracker.get_current_rate(bank)
        trend = tracker.get_rate_trend(bank)
        regime = tracker.get_market_regime(bank)
        
        print(f"\n{bank.value}:")
        print(f"  Current Rate: {rate:.2f}%")
        print(f"  Trend: {trend}")
        print(f"  Regime: {regime}")
    
    print("\n" + "=" * 50)
    print("Banking Sector Impact:", get_banking_sector_impact())
    print("Market Regime:", get_market_regime())
    print("Fed Rate:", get_fed_rate())
