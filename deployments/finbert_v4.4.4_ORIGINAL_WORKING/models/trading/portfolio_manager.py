"""
Portfolio Manager
Handles portfolio-level operations and analytics
"""

import logging
from datetime import datetime
from typing import Dict, List
from .trade_database import TradingDatabase
from .paper_trading_engine import PaperTradingEngine

logger = logging.getLogger(__name__)


class PortfolioManager:
    """Manages portfolio-level operations"""
    
    def __init__(self, paper_engine: PaperTradingEngine):
        """Initialize portfolio manager"""
        self.engine = paper_engine
        self.db = paper_engine.db
        logger.info("Portfolio manager initialized")
    
    def get_portfolio_summary(self) -> Dict:
        """
        Get complete portfolio summary
        
        Returns:
            Portfolio summary with all metrics
        """
        return self.engine.get_account_summary()
    
    def get_portfolio_allocation(self) -> Dict:
        """
        Get portfolio allocation by symbol
        
        Returns:
            Allocation percentages
        """
        positions = self.db.get_positions()
        account = self.db.get_account()
        
        total_value = account['total_value']
        
        allocations = []
        for position in positions:
            allocation_percent = (position['market_value'] / total_value) * 100 if total_value > 0 else 0
            allocations.append({
                'symbol': position['symbol'],
                'market_value': position['market_value'],
                'allocation_percent': allocation_percent
            })
        
        # Add cash allocation
        cash_percent = (account['cash_balance'] / total_value) * 100 if total_value > 0 else 100
        allocations.append({
            'symbol': 'CASH',
            'market_value': account['cash_balance'],
            'allocation_percent': cash_percent
        })
        
        return {
            'success': True,
            'allocations': allocations,
            'total_value': total_value
        }
    
    def get_performance_metrics(self) -> Dict:
        """
        Calculate portfolio performance metrics
        
        Returns:
            Performance metrics
        """
        account = self.db.get_account()
        stats = self.db.get_trade_statistics()
        
        # Calculate metrics
        total_return = account['total_pnl']
        total_return_percent = account['total_pnl_percent']
        
        return {
            'success': True,
            'metrics': {
                'total_return': total_return,
                'total_return_percent': total_return_percent,
                'total_trades': stats['total_trades'],
                'win_rate': stats['win_rate'],
                'profit_factor': stats['profit_factor'],
                'largest_win': stats['largest_win'],
                'largest_loss': stats['largest_loss'],
                'average_pnl': stats['avg_pnl']
            }
        }
    
    def get_trade_history(self, limit: int = 50) -> Dict:
        """
        Get trade history with filtering
        
        Args:
            limit: Maximum trades to return
            
        Returns:
            Trade history
        """
        trades = self.db.get_trades(limit=limit)
        
        return {
            'success': True,
            'trades': trades,
            'count': len(trades)
        }
    
    def reset_portfolio(self, initial_capital: float = 10000) -> Dict:
        """
        Reset entire portfolio
        
        Args:
            initial_capital: Starting capital
            
        Returns:
            Reset confirmation
        """
        return self.engine.reset_account(initial_capital)
