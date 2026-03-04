"""
Risk Manager
Handles risk controls and validation
"""

import logging
from typing import Dict
from .trade_database import TradingDatabase

logger = logging.getLogger(__name__)


class RiskManager:
    """Manages risk controls and limits"""
    
    def __init__(self, db: TradingDatabase,
                 max_position_size: float = 0.20,
                 max_portfolio_risk: float = 0.02,
                 max_positions: int = 10):
        """
        Initialize risk manager
        
        Args:
            db: TradingDatabase instance
            max_position_size: Maximum position as % of portfolio (0.20 = 20%)
            max_portfolio_risk: Maximum risk per trade as % of portfolio (0.02 = 2%)
            max_positions: Maximum number of concurrent positions
        """
        self.db = db
        self.max_position_size = max_position_size
        self.max_portfolio_risk = max_portfolio_risk
        self.max_positions = max_positions
        logger.info(f"Risk manager initialized (max_position: {max_position_size*100}%, max_risk: {max_portfolio_risk*100}%, max_positions: {max_positions})")
    
    def validate_order(self, symbol: str, side: str, quantity: int, price: float) -> Dict:
        """
        Validate order against risk limits
        
        Args:
            symbol: Stock symbol
            side: 'BUY' or 'SELL'
            quantity: Number of shares
            price: Order price
            
        Returns:
            Validation result
        """
        account = self.db.get_account()
        positions = self.db.get_positions()
        
        warnings = []
        errors = []
        
        if side == 'BUY':
            # Check position size limit
            order_value = price * quantity
            position_percent = order_value / account['total_value'] if account['total_value'] > 0 else 1
            
            if position_percent > self.max_position_size:
                errors.append(f'Position size {position_percent*100:.1f}% exceeds limit {self.max_position_size*100:.1f}%')
            elif position_percent > self.max_position_size * 0.8:
                warnings.append(f'Position size {position_percent*100:.1f}% approaching limit {self.max_position_size*100:.1f}%')
            
            # Check max positions limit
            # Count as new position if symbol not in portfolio
            existing_position = self.db.get_position(symbol)
            if existing_position is None:
                if len(positions) >= self.max_positions:
                    errors.append(f'Already at maximum {self.max_positions} positions')
                elif len(positions) >= self.max_positions - 1:
                    warnings.append(f'Approaching maximum {self.max_positions} positions')
            
            # Check sufficient funds
            if order_value > account['cash_balance']:
                errors.append(f'Insufficient funds. Need ${order_value:.2f}, have ${account["cash_balance"]:.2f}')
        
        elif side == 'SELL':
            # Check if position exists
            position = self.db.get_position(symbol)
            if position is None:
                errors.append(f'No position in {symbol} to sell')
            elif position['quantity'] < quantity:
                errors.append(f'Insufficient shares. Have {position["quantity"]}, trying to sell {quantity}')
        
        # Calculate risk score (0-100, lower is better)
        risk_score = self.calculate_risk_score()
        
        if risk_score > 80:
            warnings.append(f'Portfolio risk score high: {risk_score}/100')
        
        return {
            'valid': len(errors) == 0,
            'warnings': warnings,
            'errors': errors,
            'risk_score': risk_score
        }
    
    def calculate_position_size(self, symbol: str, price: float,
                                stop_loss_percent: float) -> Dict:
        """
        Calculate optimal position size based on risk
        
        Args:
            symbol: Stock symbol
            price: Current price
            stop_loss_percent: Stop-loss as decimal (0.03 = 3%)
            
        Returns:
            Position size recommendation
        """
        account = self.db.get_account()
        total_value = account['total_value']
        
        # Risk-based position sizing
        max_risk_amount = total_value * self.max_portfolio_risk
        position_value = max_risk_amount / stop_loss_percent if stop_loss_percent > 0 else 0
        
        # Apply max position size limit
        max_position_value = total_value * self.max_position_size
        position_value = min(position_value, max_position_value)
        
        # Apply cash limit
        position_value = min(position_value, account['cash_balance'])
        
        # Calculate shares
        shares = int(position_value / price) if price > 0 else 0
        actual_position_value = shares * price
        actual_position_percent = (actual_position_value / total_value) * 100 if total_value > 0 else 0
        
        return {
            'success': True,
            'recommended_shares': shares,
            'position_value': actual_position_value,
            'position_percent': actual_position_percent,
            'max_risk_amount': max_risk_amount,
            'stop_loss_percent': stop_loss_percent * 100
        }
    
    def calculate_risk_score(self) -> float:
        """
        Calculate overall portfolio risk score (0-100)
        
        Returns:
            Risk score (0 = no risk, 100 = maximum risk)
        """
        account = self.db.get_account()
        positions = self.db.get_positions()
        
        score = 0
        
        # Factor 1: Number of positions (more positions = lower risk due to diversification)
        if len(positions) == 0:
            position_score = 0
        elif len(positions) >= self.max_positions:
            position_score = 30  # Max positions = higher concentration risk
        else:
            position_score = 10  # Some diversification
        
        score += position_score
        
        # Factor 2: Concentration risk (largest position %)
        if positions:
            largest_position_pct = max([p['market_value'] / account['total_value'] * 100 
                                       for p in positions]) if account['total_value'] > 0 else 0
            if largest_position_pct > self.max_position_size * 100:
                score += 40
            elif largest_position_pct > self.max_position_size * 80:
                score += 20
            else:
                score += 10
        
        # Factor 3: Drawdown risk (how much is at risk)
        if account['total_pnl'] < 0:
            drawdown_pct = abs(account['total_pnl_percent'])
            if drawdown_pct > 10:
                score += 30
            elif drawdown_pct > 5:
                score += 15
            else:
                score += 5
        
        return min(score, 100)
    
    def get_risk_limits(self) -> Dict:
        """
        Get current risk limits
        
        Returns:
            Risk limit configuration
        """
        return {
            'success': True,
            'limits': {
                'max_position_size': self.max_position_size,
                'max_position_size_percent': self.max_position_size * 100,
                'max_portfolio_risk': self.max_portfolio_risk,
                'max_portfolio_risk_percent': self.max_portfolio_risk * 100,
                'max_positions': self.max_positions
            }
        }
    
    def update_risk_limits(self, max_position_size: float = None,
                          max_portfolio_risk: float = None,
                          max_positions: int = None) -> Dict:
        """
        Update risk limits
        
        Args:
            max_position_size: New max position size (optional)
            max_portfolio_risk: New max portfolio risk (optional)
            max_positions: New max positions (optional)
            
        Returns:
            Update confirmation
        """
        if max_position_size is not None:
            if 0 < max_position_size <= 1:
                self.max_position_size = max_position_size
            else:
                return {'success': False, 'error': 'max_position_size must be between 0 and 1'}
        
        if max_portfolio_risk is not None:
            if 0 < max_portfolio_risk <= 0.1:
                self.max_portfolio_risk = max_portfolio_risk
            else:
                return {'success': False, 'error': 'max_portfolio_risk must be between 0 and 0.1'}
        
        if max_positions is not None:
            if max_positions > 0:
                self.max_positions = max_positions
            else:
                return {'success': False, 'error': 'max_positions must be positive'}
        
        logger.info(f"Risk limits updated: position={self.max_position_size*100}%, risk={self.max_portfolio_risk*100}%, positions={self.max_positions}")
        
        return {
            'success': True,
            'limits': self.get_risk_limits()['limits']
        }
