"""
Live Trading Coordinator with Intraday Monitoring Integration
==============================================================

Integrates swing trading engine (Phase 1-3) with intraday monitoring for a complete
live trading platform that operates across dual timeframes.

Features:
- Unified position management (swing + intraday)
- Cross-timeframe decision making
- Real-time risk management
- Consolidated alerting
- Broker API integration

Author: FinBERT Enhanced System
Version: 1.0
Date: December 20, 2024
"""

import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import pandas as pd
import numpy as np
from dataclasses import dataclass, asdict
from enum import Enum

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PositionType(Enum):
    """Position type classification"""
    SWING = "swing"
    INTRADAY = "intraday"


class SignalStrength(Enum):
    """Signal strength classification"""
    VERY_STRONG = "very_strong"  # >75
    STRONG = "strong"            # 60-75
    MODERATE = "moderate"        # 50-60
    WEAK = "weak"                # <50


@dataclass
class LivePosition:
    """Represents a live trading position"""
    symbol: str
    position_type: PositionType
    entry_date: datetime
    entry_price: float
    shares: int
    stop_loss: float
    trailing_stop: float
    profit_target: Optional[float]
    target_exit_date: Optional[datetime]
    current_price: float
    unrealized_pnl: float
    unrealized_pnl_pct: float
    
    # Metadata
    entry_signal_strength: float
    regime: Optional[str] = None
    notes: str = ""
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        d = asdict(self)
        d['position_type'] = self.position_type.value
        d['entry_date'] = self.entry_date.isoformat() if self.entry_date else None
        d['target_exit_date'] = self.target_exit_date.isoformat() if self.target_exit_date else None
        return d


class LiveTradingCoordinator:
    """
    Unified coordinator for swing trading and intraday monitoring
    """
    
    def __init__(
        self,
        market: str = "US",
        initial_capital: float = 100000.0,
        config_file: Optional[str] = None,
        broker_api = None,
        paper_trading: bool = True
    ):
        """
        Initialize live trading coordinator
        
        Args:
            market: Market to trade ('US' or 'ASX')
            initial_capital: Starting capital
            config_file: Path to configuration JSON
            broker_api: Broker API instance (AlpacaBroker, IBBroker, etc)
            paper_trading: If True, simulate trades (no real execution)
        """
        self.market = market
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.paper_trading = paper_trading
        self.broker = broker_api
        
        # Load configuration
        self.config = self._load_config(config_file)
        
        # Position tracking
        self.positions: Dict[str, LivePosition] = {}
        self.closed_trades: List[Dict] = []
        
        # State tracking
        self.session_start = datetime.now()
        self.last_market_sentiment = None
        self.last_macro_sentiment = None
        
        # Performance metrics
        self.metrics = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_pnl': 0.0,
            'max_drawdown': 0.0,
            'peak_capital': initial_capital
        }
        
        logger.info(f"Live Trading Coordinator initialized for {market} market")
        logger.info(f"  Initial Capital: ${initial_capital:,.2f}")
        logger.info(f"  Paper Trading: {paper_trading}")
        logger.info(f"  Max Swing Positions: 3")
    
    def _load_config(self, config_file: Optional[str]) -> Dict:
        """Load configuration from file"""
        default_config = {
            'swing_trading': {
                'holding_period_days': 5,
                'stop_loss_percent': 3.0,
                'confidence_threshold': 52.0,
                'max_position_size': 0.25,
                'use_trailing_stop': True,
                'use_profit_targets': True,
                'use_regime_detection': True,
                'use_multi_timeframe': True,
                'use_volatility_sizing': True
            },
            'intraday_monitoring': {
                'scan_interval_minutes': 15,
                'breakout_threshold': 70.0,
                'auto_trade_intraday': False,
                'max_intraday_positions': 0
            },
            'risk_management': {
                'max_total_positions': 3,
                'max_portfolio_heat': 0.06,
                'max_single_trade_risk': 0.02,
                'use_position_scaling': True
            },
            'cross_timeframe': {
                'use_intraday_for_entries': True,
                'use_intraday_for_exits': True,
                'sentiment_boost_threshold': 70,
                'sentiment_block_threshold': 30,
                'early_exit_threshold': 80
            }
        }
        
        if config_file:
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                    for key in default_config:
                        if key in user_config:
                            default_config[key].update(user_config[key])
            except Exception as e:
                logger.warning(f"Failed to load config: {e}, using defaults")
        
        return default_config
    
    def get_portfolio_status(self) -> Dict:
        """Get current portfolio status"""
        total_invested = sum(p.shares * p.entry_price for p in self.positions.values())
        total_current_value = sum(p.shares * p.current_price for p in self.positions.values())
        total_unrealized_pnl = sum(p.unrealized_pnl for p in self.positions.values())
        total_unrealized_pnl_pct = (total_unrealized_pnl / total_invested * 100) if total_invested > 0 else 0
        total_capital = self.current_capital + total_current_value
        total_return = ((total_capital - self.initial_capital) / self.initial_capital) * 100
        win_rate = (self.metrics['winning_trades'] / self.metrics['total_trades'] * 100) if self.metrics['total_trades'] > 0 else 0
        
        return {
            'timestamp': datetime.now().isoformat(),
            'capital': {
                'initial': self.initial_capital,
                'current_cash': self.current_capital,
                'invested': total_invested,
                'total_value': total_capital,
                'total_return_pct': total_return
            },
            'positions': {
                'count': len(self.positions),
                'swing': sum(1 for p in self.positions.values() if p.position_type == PositionType.SWING),
                'intraday': sum(1 for p in self.positions.values() if p.position_type == PositionType.INTRADAY),
                'symbols': list(self.positions.keys()),
                'total_unrealized_pnl': total_unrealized_pnl,
                'total_unrealized_pnl_pct': total_unrealized_pnl_pct
            },
            'performance': {
                'total_trades': self.metrics['total_trades'],
                'winning_trades': self.metrics['winning_trades'],
                'losing_trades': self.metrics['losing_trades'],
                'win_rate': win_rate,
                'total_realized_pnl': self.metrics['total_pnl'],
                'max_drawdown': self.metrics['max_drawdown'] * 100
            }
        }
    
    def save_state(self, filepath: str) -> None:
        """Save coordinator state to file"""
        state = {
            'timestamp': datetime.now().isoformat(),
            'market': self.market,
            'capital': self.current_capital,
            'positions': [p.to_dict() for p in self.positions.values()],
            'closed_trades': self.closed_trades,
            'metrics': self.metrics
        }
        
        try:
            with open(filepath, 'w') as f:
                json.dump(state, f, indent=2)
            logger.info(f"State saved to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save state: {e}")


if __name__ == "__main__":
    # Example usage
    coordinator = LiveTradingCoordinator(
        market="US",
        initial_capital=100000.0,
        paper_trading=True
    )
    
    status = coordinator.get_portfolio_status()
    print(json.dumps(status, indent=2))
