"""
Risk Management Module for Trading Predictions
Implements portfolio risk assessment, position sizing, and risk metrics
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
import yfinance as yf

logger = logging.getLogger(__name__)


@dataclass
class RiskMetrics:
    """Container for risk metrics"""
    value_at_risk: float  # VaR
    conditional_var: float  # CVaR
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    volatility: float
    beta: float
    correlation: float
    risk_score: float  # Overall risk score 0-100


class RiskManager:
    """Comprehensive risk management system"""
    
    def __init__(self, risk_free_rate: float = 0.03):
        self.risk_free_rate = risk_free_rate
        self.confidence_level = 0.95
        self.lookback_period = 252  # Trading days
        
    async def calculate_risk_metrics(
        self,
        symbol: str,
        position_size: float,
        portfolio_value: float,
        holding_period: int = 5
    ) -> RiskMetrics:
        """Calculate comprehensive risk metrics for a position"""
        
        try:
            # Fetch historical data
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1y")
            
            if hist.empty:
                logger.warning(f"No data for {symbol}")
                return self._get_default_metrics()
            
            # Calculate returns
            returns = hist['Close'].pct_change().dropna()
            
            # Value at Risk (VaR)
            var = self._calculate_var(returns, position_size, holding_period)
            
            # Conditional VaR (CVaR)
            cvar = self._calculate_cvar(returns, position_size, holding_period)
            
            # Sharpe Ratio
            sharpe = self._calculate_sharpe_ratio(returns)
            
            # Sortino Ratio
            sortino = self._calculate_sortino_ratio(returns)
            
            # Maximum Drawdown
            max_dd = self._calculate_max_drawdown(hist['Close'])
            
            # Volatility
            volatility = returns.std() * np.sqrt(252)
            
            # Beta (relative to S&P 500)
            beta = await self._calculate_beta(returns, symbol)
            
            # Correlation with market
            correlation = await self._calculate_market_correlation(returns)
            
            # Overall risk score (0-100, higher is riskier)
            risk_score = self._calculate_risk_score(
                var, cvar, sharpe, volatility, max_dd, position_size / portfolio_value
            )
            
            return RiskMetrics(
                value_at_risk=var,
                conditional_var=cvar,
                sharpe_ratio=sharpe,
                sortino_ratio=sortino,
                max_drawdown=max_dd,
                volatility=volatility,
                beta=beta,
                correlation=correlation,
                risk_score=risk_score
            )
            
        except Exception as e:
            logger.error(f"Risk calculation error: {e}")
            return self._get_default_metrics()
    
    def _calculate_var(
        self,
        returns: pd.Series,
        position_size: float,
        holding_period: int
    ) -> float:
        """Calculate Value at Risk"""
        # Historical VaR
        var_percentile = np.percentile(returns, (1 - self.confidence_level) * 100)
        
        # Scale to holding period
        var_scaled = var_percentile * np.sqrt(holding_period)
        
        # Apply to position size
        var_dollar = position_size * var_scaled
        
        return abs(var_dollar)
    
    def _calculate_cvar(
        self,
        returns: pd.Series,
        position_size: float,
        holding_period: int
    ) -> float:
        """Calculate Conditional Value at Risk (Expected Shortfall)"""
        var_threshold = np.percentile(returns, (1 - self.confidence_level) * 100)
        
        # Get returns worse than VaR threshold
        tail_returns = returns[returns <= var_threshold]
        
        if len(tail_returns) == 0:
            return self._calculate_var(returns, position_size, holding_period) * 1.2
        
        # Average of tail returns
        cvar = tail_returns.mean() * np.sqrt(holding_period)
        
        return abs(position_size * cvar)
    
    def _calculate_sharpe_ratio(self, returns: pd.Series) -> float:
        """Calculate Sharpe Ratio"""
        excess_returns = returns.mean() * 252 - self.risk_free_rate
        
        if returns.std() == 0:
            return 0
        
        return excess_returns / (returns.std() * np.sqrt(252))
    
    def _calculate_sortino_ratio(self, returns: pd.Series) -> float:
        """Calculate Sortino Ratio (uses downside deviation)"""
        excess_returns = returns.mean() * 252 - self.risk_free_rate
        
        # Downside returns only
        downside_returns = returns[returns < 0]
        
        if len(downside_returns) == 0:
            return self._calculate_sharpe_ratio(returns) * 1.5  # Bonus for no downside
        
        downside_std = downside_returns.std() * np.sqrt(252)
        
        if downside_std == 0:
            return 0
        
        return excess_returns / downside_std
    
    def _calculate_max_drawdown(self, prices: pd.Series) -> float:
        """Calculate maximum drawdown"""
        cumulative = (1 + prices.pct_change()).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        
        return abs(drawdown.min())
    
    async def _calculate_beta(self, returns: pd.Series, symbol: str) -> float:
        """Calculate beta relative to market (S&P 500)"""
        try:
            # Get S&P 500 data
            spy = yf.Ticker("SPY")
            spy_hist = spy.history(period="1y")
            
            if spy_hist.empty:
                return 1.0
            
            spy_returns = spy_hist['Close'].pct_change().dropna()
            
            # Align dates
            aligned = pd.DataFrame({
                'stock': returns,
                'market': spy_returns
            }).dropna()
            
            if len(aligned) < 20:
                return 1.0
            
            # Calculate beta (covariance / variance)
            covariance = aligned['stock'].cov(aligned['market'])
            market_variance = aligned['market'].var()
            
            if market_variance == 0:
                return 1.0
            
            return covariance / market_variance
            
        except Exception as e:
            logger.error(f"Beta calculation error: {e}")
            return 1.0
    
    async def _calculate_market_correlation(self, returns: pd.Series) -> float:
        """Calculate correlation with market"""
        try:
            spy = yf.Ticker("SPY")
            spy_hist = spy.history(period="1y")
            
            if spy_hist.empty:
                return 0.5
            
            spy_returns = spy_hist['Close'].pct_change().dropna()
            
            # Calculate correlation
            correlation = returns.corr(spy_returns)
            
            return correlation if not pd.isna(correlation) else 0.5
            
        except Exception as e:
            logger.error(f"Correlation calculation error: {e}")
            return 0.5
    
    def _calculate_risk_score(
        self,
        var: float,
        cvar: float,
        sharpe: float,
        volatility: float,
        max_dd: float,
        position_ratio: float
    ) -> float:
        """Calculate overall risk score (0-100)"""
        
        # Normalize metrics to 0-1 scale
        var_score = min(var / 10000, 1)  # Assume $10k is max acceptable VaR
        cvar_score = min(cvar / 15000, 1)  # CVaR slightly higher threshold
        vol_score = min(volatility / 0.5, 1)  # 50% annual vol is very high
        dd_score = min(max_dd / 0.3, 1)  # 30% drawdown is severe
        position_score = min(position_ratio / 0.2, 1)  # 20% position is large
        
        # Sharpe ratio (inverted - lower is worse)
        sharpe_score = 1 - min(max(sharpe + 2, 0) / 4, 1)  # Range -2 to 2
        
        # Weighted average
        weights = {
            'var': 0.2,
            'cvar': 0.15,
            'volatility': 0.2,
            'drawdown': 0.15,
            'position': 0.15,
            'sharpe': 0.15
        }
        
        risk_score = (
            var_score * weights['var'] +
            cvar_score * weights['cvar'] +
            vol_score * weights['volatility'] +
            dd_score * weights['drawdown'] +
            position_score * weights['position'] +
            sharpe_score * weights['sharpe']
        )
        
        return min(risk_score * 100, 100)
    
    def _get_default_metrics(self) -> RiskMetrics:
        """Return default risk metrics when calculation fails"""
        return RiskMetrics(
            value_at_risk=0,
            conditional_var=0,
            sharpe_ratio=0,
            sortino_ratio=0,
            max_drawdown=0,
            volatility=0.2,
            beta=1.0,
            correlation=0.5,
            risk_score=50
        )
    
    def calculate_position_size(
        self,
        portfolio_value: float,
        risk_per_trade: float,
        stop_loss_percent: float,
        confidence: float = 0.5
    ) -> Dict[str, float]:
        """Calculate optimal position size using Kelly Criterion and risk management rules"""
        
        # Basic position sizing (risk-based)
        risk_amount = portfolio_value * risk_per_trade
        position_size_risk = risk_amount / stop_loss_percent
        
        # Kelly Criterion
        win_probability = 0.5 + (confidence - 0.5) * 0.3  # Adjust win prob based on confidence
        avg_win = 0.02  # Assume 2% average win
        avg_loss = stop_loss_percent
        
        kelly_fraction = 0
        if avg_loss > 0:
            kelly_fraction = (win_probability * avg_win - (1 - win_probability) * avg_loss) / avg_win
            kelly_fraction = max(0, min(kelly_fraction, 0.25))  # Cap at 25% of portfolio
        
        position_size_kelly = portfolio_value * kelly_fraction
        
        # Use the more conservative estimate
        recommended_size = min(position_size_risk, position_size_kelly)
        
        # Apply maximum position size limit (10% of portfolio)
        max_position = portfolio_value * 0.1
        final_size = min(recommended_size, max_position)
        
        return {
            'recommended_size': final_size,
            'risk_based_size': position_size_risk,
            'kelly_size': position_size_kelly,
            'max_allowed': max_position,
            'position_percent': (final_size / portfolio_value) * 100
        }
    
    def assess_portfolio_risk(
        self,
        positions: List[Dict[str, Any]],
        portfolio_value: float
    ) -> Dict[str, Any]:
        """Assess overall portfolio risk"""
        
        if not positions:
            return {
                'total_exposure': 0,
                'diversification_score': 0,
                'concentration_risk': 'low',
                'recommendations': ['Add positions to build portfolio']
            }
        
        # Calculate total exposure
        total_exposure = sum(p.get('value', 0) for p in positions)
        exposure_ratio = total_exposure / portfolio_value
        
        # Calculate concentration
        position_weights = [p.get('value', 0) / total_exposure for p in positions if total_exposure > 0]
        
        # Herfindahl-Hirschman Index for concentration
        hhi = sum(w**2 for w in position_weights) if position_weights else 0
        
        # Diversification score (inverse of HHI)
        diversification_score = 1 - hhi if hhi < 1 else 0
        
        # Determine concentration risk level
        if hhi > 0.5:
            concentration_risk = 'high'
        elif hhi > 0.25:
            concentration_risk = 'medium'
        else:
            concentration_risk = 'low'
        
        # Generate recommendations
        recommendations = []
        
        if exposure_ratio > 0.95:
            recommendations.append('Consider keeping some cash reserves')
        
        if hhi > 0.5:
            recommendations.append('Portfolio is highly concentrated, consider diversifying')
        
        if len(positions) < 5:
            recommendations.append('Consider adding more positions for better diversification')
        
        # Check for correlated positions
        sectors = [p.get('sector', 'unknown') for p in positions]
        sector_counts = pd.Series(sectors).value_counts()
        
        if any(count / len(positions) > 0.4 for count in sector_counts):
            recommendations.append('High sector concentration detected, consider sector diversification')
        
        return {
            'total_exposure': total_exposure,
            'exposure_ratio': exposure_ratio,
            'diversification_score': diversification_score,
            'concentration_risk': concentration_risk,
            'position_count': len(positions),
            'average_position_size': total_exposure / len(positions) if positions else 0,
            'recommendations': recommendations
        }
    
    def calculate_stop_loss(
        self,
        entry_price: float,
        atr: float,
        risk_tolerance: str = 'moderate'
    ) -> Dict[str, float]:
        """Calculate stop loss levels based on ATR and risk tolerance"""
        
        multipliers = {
            'conservative': 1.5,
            'moderate': 2.0,
            'aggressive': 2.5
        }
        
        multiplier = multipliers.get(risk_tolerance, 2.0)
        
        stop_loss = entry_price - (atr * multiplier)
        stop_loss_percent = (entry_price - stop_loss) / entry_price
        
        # Calculate trailing stop
        trailing_stop = atr * multiplier
        
        return {
            'stop_loss': stop_loss,
            'stop_loss_percent': stop_loss_percent,
            'trailing_stop_distance': trailing_stop,
            'risk_reward_ratio': 2.0,  # Aim for 2:1 reward:risk
            'take_profit': entry_price + (atr * multiplier * 2)
        }


# Global instance
risk_manager = RiskManager()


class PortfolioOptimizer:
    """Portfolio optimization using Modern Portfolio Theory"""
    
    def __init__(self):
        self.lookback_period = 252
        
    async def optimize_portfolio(
        self,
        symbols: List[str],
        target_return: Optional[float] = None
    ) -> Dict[str, Any]:
        """Optimize portfolio weights using Markowitz optimization"""
        
        try:
            # Fetch data for all symbols
            returns_data = {}
            
            for symbol in symbols:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1y")
                
                if not hist.empty:
                    returns = hist['Close'].pct_change().dropna()
                    returns_data[symbol] = returns
            
            if not returns_data:
                return self._get_equal_weights(symbols)
            
            # Create returns dataframe
            returns_df = pd.DataFrame(returns_data)
            
            # Calculate expected returns and covariance
            expected_returns = returns_df.mean() * 252
            cov_matrix = returns_df.cov() * 252
            
            # Optimize for maximum Sharpe ratio
            weights = self._optimize_sharpe(expected_returns, cov_matrix)
            
            # Calculate portfolio metrics
            portfolio_return = np.dot(weights, expected_returns)
            portfolio_std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            sharpe = (portfolio_return - 0.03) / portfolio_std
            
            return {
                'weights': {symbol: weight for symbol, weight in zip(symbols, weights)},
                'expected_return': portfolio_return,
                'volatility': portfolio_std,
                'sharpe_ratio': sharpe
            }
            
        except Exception as e:
            logger.error(f"Portfolio optimization error: {e}")
            return self._get_equal_weights(symbols)
    
    def _optimize_sharpe(
        self,
        expected_returns: pd.Series,
        cov_matrix: pd.DataFrame
    ) -> np.ndarray:
        """Optimize for maximum Sharpe ratio (simplified)"""
        
        n = len(expected_returns)
        
        # Start with equal weights
        weights = np.ones(n) / n
        
        # Simple optimization (in practice, use scipy.optimize)
        # This is a simplified version
        best_sharpe = -np.inf
        best_weights = weights
        
        # Try different weight combinations
        for _ in range(1000):
            # Random weights
            w = np.random.random(n)
            w = w / w.sum()
            
            # Calculate Sharpe
            ret = np.dot(w, expected_returns)
            std = np.sqrt(np.dot(w.T, np.dot(cov_matrix, w)))
            sharpe = (ret - 0.03) / std if std > 0 else -np.inf
            
            if sharpe > best_sharpe:
                best_sharpe = sharpe
                best_weights = w
        
        return best_weights
    
    def _get_equal_weights(self, symbols: List[str]) -> Dict[str, Any]:
        """Return equal weights as fallback"""
        n = len(symbols)
        weight = 1.0 / n if n > 0 else 0
        
        return {
            'weights': {symbol: weight for symbol in symbols},
            'expected_return': 0.08,  # Assume 8% average
            'volatility': 0.15,  # Assume 15% volatility
            'sharpe_ratio': 0.33
        }


# Global portfolio optimizer
portfolio_optimizer = PortfolioOptimizer()