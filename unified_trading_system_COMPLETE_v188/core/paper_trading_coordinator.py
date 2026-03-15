"""
Paper Trading Coordinator - v1.3.15.188
Coordinates paper trading execution with v188 confidence threshold fix.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os

logger = logging.getLogger(__name__)


class PaperTradingCoordinator:
    """
    Coordinates paper trading operations with proper confidence thresholds.
    v188: Fixed min_confidence from 52.0 to 48.0
    """
    
    def __init__(
        self,
        config_path: str = "config/live_trading_config.json",
        portfolio_path: str = "state/portfolio.json",
        ui_min_confidence: Optional[float] = None
    ):
        """
        Initialize paper trading coordinator.
        
        Args:
            config_path: Path to trading configuration
            portfolio_path: Path to portfolio state file
            ui_min_confidence: Optional UI override for minimum confidence
        """
        self.config_path = config_path
        self.portfolio_path = portfolio_path
        self.ui_min_confidence = ui_min_confidence
        
        # Load configuration
        self.config = self._load_config()
        
        # v188 FIX: Use 48.0 instead of 52.0 as fallback
        # Check confidence (FIX v1.3.15.160: Use UI value if provided)
        self.min_confidence = self.ui_min_confidence if self.ui_min_confidence is not None else 48.0
        
        # Load portfolio state
        self.portfolio = self._load_portfolio()
        
        # Trading state
        self.active_positions = {}
        self.pending_orders = []
        self.trade_history = []
        
        logger.info(
            f"PaperTradingCoordinator initialized: "
            f"min_confidence={self.min_confidence}%, "
            f"cash=${self.portfolio.get('cash', 0):,.2f}"
        )
    
    def _load_config(self) -> Dict:
        """Load trading configuration from JSON file."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                logger.info(f"Loaded config from {self.config_path}")
                return config
            else:
                logger.warning(f"Config file not found: {self.config_path}, using defaults")
                return self._default_config()
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return self._default_config()
    
    def _default_config(self) -> Dict:
        """Return default configuration."""
        return {
            "trading": {
                "enabled": True,
                "mode": "paper",
                "max_positions": 10,
                "position_size_percent": 10
            },
            "risk_management": {
                "stop_loss_percent": 3.0,
                "take_profit_percent": 8.0
            },
            "swing_trading": {
                "confidence_threshold": 45.0  # v188
            }
        }
    
    def _load_portfolio(self) -> Dict:
        """Load portfolio state from JSON file."""
        try:
            if os.path.exists(self.portfolio_path):
                with open(self.portfolio_path, 'r') as f:
                    portfolio = json.load(f)
                logger.info(f"Loaded portfolio: ${portfolio.get('cash', 0):,.2f} cash")
                return portfolio
            else:
                logger.info("No existing portfolio, initializing new one")
                return {
                    "cash": 100000.0,
                    "positions": {},
                    "trades": [],
                    "initialized": datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Error loading portfolio: {e}")
            return {"cash": 100000.0, "positions": {}, "trades": []}
    
    def evaluate_entry_with_intraday(
        self,
        symbol: str,
        signal: str,
        confidence: float,
        price: float,
        intraday_data: Optional[Dict] = None
    ) -> Dict:
        """
        Evaluate whether to enter a trade based on signal and confidence.
        v188: Uses 48.0% minimum confidence threshold.
        
        Args:
            symbol: Stock symbol
            signal: Trade signal (BUY/SELL/HOLD)
            confidence: Signal confidence (0-100)
            price: Current price
            intraday_data: Optional intraday market data
            
        Returns:
            Evaluation result dictionary
        """
        # Convert confidence to percentage if needed
        conf_pct = confidence * 100 if confidence <= 1.0 else confidence
        
        # v188 FIX: Check against 48.0 threshold
        if conf_pct < self.min_confidence:
            logger.info(
                f"{symbol}: Confidence {conf_pct:.1f}% < {self.min_confidence}% - SKIP"
            )
            return {
                'approved': False,
                'reason': f'Confidence {conf_pct:.1f}% below threshold {self.min_confidence}%',
                'symbol': symbol
            }
        
        # Also check config threshold
        threshold = self.config.get('swing_trading', {}).get('confidence_threshold', 45.0)
        if conf_pct < threshold:
            logger.info(
                f"{symbol}: Confidence {conf_pct:.1f}% < config threshold {threshold}% - SKIP"
            )
            return {
                'approved': False,
                'reason': f'Below config threshold {threshold}%',
                'symbol': symbol
            }
        
        # Check if signal is actionable
        if signal not in ['BUY', 'SELL']:
            return {
                'approved': False,
                'reason': f'Non-actionable signal: {signal}',
                'symbol': symbol
            }
        
        # Check if we already have a position
        if symbol in self.portfolio.get('positions', {}):
            return {
                'approved': False,
                'reason': 'Position already exists',
                'symbol': symbol
            }
        
        # Check max positions
        max_positions = self.config.get('trading', {}).get('max_positions', 10)
        current_positions = len(self.portfolio.get('positions', {}))
        if current_positions >= max_positions:
            return {
                'approved': False,
                'reason': f'Max positions reached ({max_positions})',
                'symbol': symbol
            }
        
        # Calculate position size
        position_size_pct = self.config.get('trading', {}).get('position_size_percent', 10)
        cash_available = self.portfolio.get('cash', 0)
        position_value = cash_available * (position_size_pct / 100.0)
        shares = int(position_value / price) if price > 0 else 0
        
        if shares < 1:
            return {
                'approved': False,
                'reason': 'Insufficient cash for minimum position',
                'symbol': symbol
            }
        
        # Adjust holding period based on confidence
        base_holding = 14  # days
        if conf_pct > 70:
            holding_days = min(15, base_holding + 3)
        elif conf_pct < 55:
            holding_days = max(3, base_holding - 2)
        else:
            holding_days = base_holding
        
        # All checks passed
        logger.info(
            f"{symbol}: APPROVED - {signal} at {conf_pct:.1f}% confidence "
            f"(>= {self.min_confidence}%), {shares} shares @ ${price:.2f}"
        )
        
        return {
            'approved': True,
            'symbol': symbol,
            'action': signal,
            'confidence': conf_pct,
            'price': price,
            'shares': shares,
            'position_value': shares * price,
            'holding_days': holding_days,
            'stop_loss': price * (1 - self.config.get('risk_management', {}).get('stop_loss_percent', 3.0) / 100.0),
            'take_profit': price * (1 + self.config.get('risk_management', {}).get('take_profit_percent', 8.0) / 100.0)
        }
    
    def execute_trade(self, trade_params: Dict) -> Dict:
        """Execute a paper trade."""
        if not trade_params.get('approved', False):
            return {'success': False, 'reason': 'Trade not approved'}
        
        symbol = trade_params['symbol']
        action = trade_params['action']
        shares = trade_params['shares']
        price = trade_params['price']
        
        # Calculate costs
        trade_value = shares * price
        commission = 0.0  # Paper trading, no commission
        total_cost = trade_value + commission
        
        # Check cash
        if total_cost > self.portfolio['cash']:
            return {'success': False, 'reason': 'Insufficient cash'}
        
        # Execute trade
        self.portfolio['cash'] -= total_cost
        
        if 'positions' not in self.portfolio:
            self.portfolio['positions'] = {}
        
        self.portfolio['positions'][symbol] = {
            'shares': shares,
            'entry_price': price,
            'entry_date': datetime.now().isoformat(),
            'confidence': trade_params.get('confidence', 0),
            'stop_loss': trade_params.get('stop_loss', 0),
            'take_profit': trade_params.get('take_profit', 0),
            'holding_days': trade_params.get('holding_days', 14)
        }
        
        # Record trade
        trade_record = {
            'symbol': symbol,
            'action': action,
            'shares': shares,
            'price': price,
            'value': trade_value,
            'timestamp': datetime.now().isoformat(),
            'confidence': trade_params.get('confidence', 0)
        }
        
        if 'trades' not in self.portfolio:
            self.portfolio['trades'] = []
        self.portfolio['trades'].append(trade_record)
        
        # Save portfolio
        self._save_portfolio()
        
        logger.info(
            f"TRADE EXECUTED: {action} {shares} {symbol} @ ${price:.2f} "
            f"(${trade_value:,.2f}, conf={trade_params.get('confidence', 0):.1f}%)"
        )
        
        return {
            'success': True,
            'trade': trade_record,
            'portfolio_value': self.get_portfolio_value()
        }
    
    def _save_portfolio(self):
        """Save portfolio state to file."""
        try:
            os.makedirs(os.path.dirname(self.portfolio_path), exist_ok=True)
            with open(self.portfolio_path, 'w') as f:
                json.dump(self.portfolio, f, indent=2)
            logger.debug(f"Portfolio saved to {self.portfolio_path}")
        except Exception as e:
            logger.error(f"Error saving portfolio: {e}")
    
    def get_portfolio_value(self, current_prices: Optional[Dict[str, float]] = None) -> float:
        """Calculate total portfolio value."""
        cash = self.portfolio.get('cash', 0)
        positions_value = 0
        
        if current_prices:
            for symbol, position in self.portfolio.get('positions', {}).items():
                if symbol in current_prices:
                    positions_value += position['shares'] * current_prices[symbol]
        
        return cash + positions_value


if __name__ == '__main__':
    print("PaperTradingCoordinator v1.3.15.188")
    print("v188 patch: min_confidence = 48.0%")
    
    coordinator = PaperTradingCoordinator()
    print(f"Min confidence: {coordinator.min_confidence}%")
    print(f"Portfolio cash: ${coordinator.portfolio.get('cash', 0):,.2f}")
