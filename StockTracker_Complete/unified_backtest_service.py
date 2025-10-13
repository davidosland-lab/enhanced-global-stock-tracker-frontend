"""
Unified Backtesting Service
Centralized backtesting engine for all modules
Can be run standalone or imported by other services
"""

import os
import sys
import json
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import yfinance as yf
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DB_PATH = "unified_backtest.db"

def init_database():
    """Initialize SQLite database for backtest results"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS backtest_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            symbol TEXT NOT NULL,
            model_name TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            initial_capital REAL NOT NULL,
            final_value REAL NOT NULL,
            total_return REAL NOT NULL,
            sharpe_ratio REAL,
            max_drawdown REAL,
            win_rate REAL,
            num_trades INTEGER,
            avg_return_per_trade REAL,
            volatility REAL,
            alpha REAL,
            beta REAL,
            trades TEXT,
            equity_curve TEXT,
            parameters TEXT,
            UNIQUE(symbol, model_name, start_date, end_date)
        )
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_symbol_model 
        ON backtest_results(symbol, model_name)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_timestamp 
        ON backtest_results(timestamp DESC)
    ''')
    
    conn.commit()
    conn.close()
    logger.info(f"Database initialized at {DB_PATH}")

class BacktestResult:
    """Container for backtest results"""
    def __init__(self, **kwargs):
        self.symbol = kwargs.get('symbol')
        self.model_name = kwargs.get('model_name')
        self.start_date = kwargs.get('start_date')
        self.end_date = kwargs.get('end_date')
        self.initial_capital = kwargs.get('initial_capital', 100000)
        self.final_value = kwargs.get('final_value', 0)
        self.total_return = kwargs.get('total_return', 0)
        self.sharpe_ratio = kwargs.get('sharpe_ratio', 0)
        self.max_drawdown = kwargs.get('max_drawdown', 0)
        self.win_rate = kwargs.get('win_rate', 0)
        self.num_trades = kwargs.get('num_trades', 0)
        self.avg_return_per_trade = kwargs.get('avg_return_per_trade', 0)
        self.volatility = kwargs.get('volatility', 0)
        self.alpha = kwargs.get('alpha')
        self.beta = kwargs.get('beta')
        self.trades = kwargs.get('trades', [])
        self.equity_curve = kwargs.get('equity_curve', [])
        
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'symbol': self.symbol,
            'model_name': self.model_name,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'initial_capital': self.initial_capital,
            'final_value': self.final_value,
            'total_return': self.total_return,
            'sharpe_ratio': self.sharpe_ratio,
            'max_drawdown': self.max_drawdown,
            'win_rate': self.win_rate,
            'num_trades': self.num_trades,
            'avg_return_per_trade': self.avg_return_per_trade,
            'volatility': self.volatility,
            'alpha': self.alpha,
            'beta': self.beta,
            'trades': self.trades,
            'equity_curve': self.equity_curve
        }

class UnifiedBacktestService:
    """Centralized backtesting service for all modules"""
    
    def __init__(self):
        """Initialize the service"""
        init_database()
        self.cache = {}  # Simple in-memory cache
        
    def run_backtest(
        self,
        symbol: str,
        model_name: str,
        start_date: str = None,
        end_date: str = None,
        initial_capital: float = 100000,
        strategy_params: Dict = None,
        use_cache: bool = True
    ) -> BacktestResult:
        """Run a comprehensive backtest"""
        
        # Default dates if not provided
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        
        # Check cache
        cache_key = f"{symbol}_{model_name}_{start_date}_{end_date}"
        if use_cache and cache_key in self.cache:
            logger.info(f"Using cached backtest for {cache_key}")
            return self.cache[cache_key]
        
        try:
            # Fetch historical data
            logger.info(f"Fetching data for {symbol} from {start_date} to {end_date}")
            ticker = yf.Ticker(symbol)
            df = ticker.history(start=start_date, end=end_date)
            
            if df.empty:
                raise ValueError(f"No data available for {symbol}")
            
            # Calculate returns
            df['returns'] = df['Close'].pct_change()
            df['log_returns'] = np.log(df['Close'] / df['Close'].shift(1))
            
            # Calculate technical indicators
            df['sma_20'] = df['Close'].rolling(window=20).mean()
            df['sma_50'] = df['Close'].rolling(window=50).mean()
            df['rsi'] = self._calculate_rsi(df['Close'])
            
            # Generate trading signals based on strategy
            if strategy_params and strategy_params.get('strategy') == 'sma_crossover':
                # SMA crossover strategy
                df['signal'] = np.where(df['sma_20'] > df['sma_50'], 1, -1)
            elif strategy_params and strategy_params.get('strategy') == 'rsi':
                # RSI-based strategy
                df['signal'] = np.where(df['rsi'] < 30, 1, np.where(df['rsi'] > 70, -1, 0))
            else:
                # Default momentum strategy
                df['signal'] = np.where(df['returns'].rolling(20).mean() > 0, 1, -1)
            
            df['position'] = df['signal'].shift(1)
            df['strategy_returns'] = df['position'] * df['returns']
            
            # Calculate cumulative returns
            df['cumulative_returns'] = (1 + df['strategy_returns']).cumprod()
            df['cumulative_market_returns'] = (1 + df['returns']).cumprod()
            
            # Generate trades
            trades = self._generate_trades(df)
            
            # Calculate metrics
            result = self._calculate_metrics(
                df, trades, initial_capital, symbol, model_name,
                start_date, end_date
            )
            
            # Store in database
            self._store_result(result, strategy_params)
            
            # Cache result
            if use_cache:
                self.cache[cache_key] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Backtest error for {symbol}: {str(e)}")
            # Return empty result on error
            return BacktestResult(
                symbol=symbol,
                model_name=model_name,
                start_date=start_date,
                end_date=end_date,
                initial_capital=initial_capital
            )
    
    def _calculate_rsi(self, prices, period=14):
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def _generate_trades(self, df):
        """Generate trade list from signals"""
        trades = []
        position = 0
        entry_price = 0
        entry_date = None
        
        for idx, row in df.iterrows():
            current_position = row.get('position', 0)
            if pd.isna(current_position):
                continue
                
            if position == 0 and current_position != 0:
                # Enter position
                position = current_position
                entry_price = row['Close']
                entry_date = idx
            elif position != 0 and current_position != position:
                # Exit position
                exit_price = row['Close']
                trade_return = (exit_price - entry_price) / entry_price * position
                trades.append({
                    'entry_date': entry_date.isoformat() if hasattr(entry_date, 'isoformat') else str(entry_date),
                    'exit_date': idx.isoformat() if hasattr(idx, 'isoformat') else str(idx),
                    'entry_price': float(entry_price),
                    'exit_price': float(exit_price),
                    'position': 'long' if position > 0 else 'short',
                    'return': float(trade_return)
                })
                # Check if reversing position
                if current_position != 0:
                    position = current_position
                    entry_price = row['Close']
                    entry_date = idx
                else:
                    position = 0
        
        return trades
    
    def _calculate_metrics(self, df, trades, initial_capital, symbol, model_name, start_date, end_date):
        """Calculate comprehensive backtest metrics"""
        
        # Basic metrics
        final_value = initial_capital * float(df['cumulative_returns'].iloc[-1]) if not df.empty else initial_capital
        total_return = (final_value - initial_capital) / initial_capital
        
        # Sharpe ratio (annualized)
        if len(df) > 1 and df['strategy_returns'].std() != 0:
            sharpe_ratio = float(df['strategy_returns'].mean() / df['strategy_returns'].std() * np.sqrt(252))
        else:
            sharpe_ratio = 0.0
        
        # Max drawdown
        if len(df) > 1:
            cummax = df['cumulative_returns'].cummax()
            drawdown = (df['cumulative_returns'] - cummax) / cummax
            max_drawdown = float(drawdown.min())
        else:
            max_drawdown = 0.0
        
        # Trade statistics
        if trades:
            winning_trades = [t for t in trades if t['return'] > 0]
            win_rate = len(winning_trades) / len(trades)
            avg_return = sum(t['return'] for t in trades) / len(trades)
        else:
            win_rate = 0.0
            avg_return = 0.0
        
        # Volatility (annualized)
        volatility = float(df['strategy_returns'].std() * np.sqrt(252)) if len(df) > 1 else 0.0
        
        # Alpha and Beta (vs market)
        alpha, beta = None, None
        if len(df) > 60:  # Need sufficient data
            market_returns = df['returns'].dropna()
            strategy_returns = df['strategy_returns'].dropna()
            
            if len(market_returns) > 1 and len(strategy_returns) > 1:
                # Calculate beta
                covariance = np.cov(strategy_returns, market_returns)[0, 1]
                market_variance = np.var(market_returns)
                beta = float(covariance / market_variance) if market_variance != 0 else 1.0
                
                # Calculate alpha (using CAPM)
                risk_free_rate = 0.02  # Assume 2% risk-free rate
                market_annual_return = float(market_returns.mean() * 252)
                strategy_annual_return = float(strategy_returns.mean() * 252)
                alpha = float(strategy_annual_return - (risk_free_rate + beta * (market_annual_return - risk_free_rate)))
        
        # Create equity curve
        equity_curve = []
        for idx, row in df.iterrows():
            equity_curve.append({
                'date': idx.isoformat() if hasattr(idx, 'isoformat') else str(idx),
                'value': float(initial_capital * row['cumulative_returns']),
                'benchmark': float(initial_capital * row['cumulative_market_returns'])
            })
        
        return BacktestResult(
            symbol=symbol,
            model_name=model_name,
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_capital,
            final_value=final_value,
            total_return=total_return,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            win_rate=win_rate,
            num_trades=len(trades),
            avg_return_per_trade=avg_return,
            volatility=volatility,
            alpha=alpha,
            beta=beta,
            trades=trades,
            equity_curve=equity_curve
        )
    
    def _store_result(self, result: BacktestResult, strategy_params: Dict = None):
        """Store backtest result in database"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO backtest_results (
                    timestamp, symbol, model_name, start_date, end_date,
                    initial_capital, final_value, total_return, sharpe_ratio,
                    max_drawdown, win_rate, num_trades, avg_return_per_trade,
                    volatility, alpha, beta, trades, equity_curve, parameters
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                result.symbol, result.model_name, result.start_date, result.end_date,
                result.initial_capital, result.final_value, result.total_return, result.sharpe_ratio,
                result.max_drawdown, result.win_rate, result.num_trades, result.avg_return_per_trade,
                result.volatility, result.alpha, result.beta,
                json.dumps(result.trades), json.dumps(result.equity_curve),
                json.dumps(strategy_params or {})
            ))
            
            conn.commit()
            conn.close()
            logger.info(f"Stored backtest result for {result.symbol} - {result.model_name}")
            
        except Exception as e:
            logger.error(f"Error storing backtest result: {str(e)}")
    
    def get_backtest_history(
        self,
        symbol: Optional[str] = None,
        model_name: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """Retrieve historical backtest results"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            query = "SELECT * FROM backtest_results WHERE 1=1"
            params = []
            
            if symbol:
                query += " AND symbol = ?"
                params.append(symbol)
            
            if model_name:
                query += " AND model_name = ?"
                params.append(model_name)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            columns = [col[0] for col in cursor.description]
            results = []
            
            for row in cursor.fetchall():
                result = dict(zip(columns, row))
                # Parse JSON fields
                result['trades'] = json.loads(result.get('trades', '[]'))
                result['equity_curve'] = json.loads(result.get('equity_curve', '[]'))
                result['parameters'] = json.loads(result.get('parameters', '{}'))
                results.append(result)
            
            conn.close()
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving backtest history: {str(e)}")
            return []
    
    def compare_models(
        self,
        symbol: str,
        model_names: List[str],
        start_date: str = None,
        end_date: str = None,
        initial_capital: float = 100000
    ) -> Dict:
        """Compare multiple models on the same symbol"""
        try:
            comparison_results = []
            
            for model_name in model_names:
                logger.info(f"Running backtest for {model_name} on {symbol}")
                result = self.run_backtest(
                    symbol=symbol,
                    model_name=model_name,
                    start_date=start_date,
                    end_date=end_date,
                    initial_capital=initial_capital
                )
                
                comparison_results.append({
                    'model_name': model_name,
                    'total_return': result.total_return,
                    'sharpe_ratio': result.sharpe_ratio,
                    'max_drawdown': result.max_drawdown,
                    'win_rate': result.win_rate,
                    'volatility': result.volatility,
                    'alpha': result.alpha,
                    'beta': result.beta,
                    'num_trades': result.num_trades
                })
            
            # Sort by total return
            comparison_results.sort(key=lambda x: x['total_return'], reverse=True)
            
            return {
                'symbol': symbol,
                'comparison_date': datetime.now().isoformat(),
                'start_date': start_date,
                'end_date': end_date,
                'models': comparison_results,
                'best_model': comparison_results[0]['model_name'] if comparison_results else None
            }
            
        except Exception as e:
            logger.error(f"Error comparing models: {str(e)}")
            return {
                'symbol': symbol,
                'comparison_date': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def get_latest_backtest(self, symbol: str, model_name: str) -> Optional[Dict]:
        """Get the most recent backtest for a symbol/model combination"""
        results = self.get_backtest_history(symbol, model_name, limit=1)
        return results[0] if results else None
    
    def clear_cache(self):
        """Clear the in-memory cache"""
        self.cache.clear()
        logger.info("Cache cleared")

# Standalone service mode
if __name__ == "__main__":
    from fastapi import FastAPI, HTTPException, Query
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel, Field
    import uvicorn
    
    # Create FastAPI app for standalone service
    app = FastAPI(title="Unified Backtest Service", version="1.0.0")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Initialize service
    service = UnifiedBacktestService()
    
    # Request models
    class BacktestRequest(BaseModel):
        symbol: str
        model_name: str
        start_date: Optional[str] = None
        end_date: Optional[str] = None
        initial_capital: float = Field(default=100000, gt=0)
        strategy_params: Optional[Dict] = None
    
    class CompareRequest(BaseModel):
        symbol: str
        model_names: List[str]
        start_date: Optional[str] = None
        end_date: Optional[str] = None
        initial_capital: float = Field(default=100000, gt=0)
    
    @app.get("/")
    async def root():
        return {
            "service": "Unified Backtest Service",
            "version": "1.0.0",
            "status": "running",
            "database": DB_PATH
        }
    
    @app.get("/health")
    async def health():
        return {"status": "healthy", "timestamp": datetime.now().isoformat()}
    
    @app.post("/api/backtest")
    async def run_backtest(request: BacktestRequest):
        """Run a backtest"""
        try:
            result = service.run_backtest(
                symbol=request.symbol,
                model_name=request.model_name,
                start_date=request.start_date,
                end_date=request.end_date,
                initial_capital=request.initial_capital,
                strategy_params=request.strategy_params
            )
            return result.to_dict()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/backtest/history")
    async def get_history(
        symbol: Optional[str] = Query(None),
        model_name: Optional[str] = Query(None),
        limit: int = Query(10, ge=1, le=100)
    ):
        """Get backtest history"""
        results = service.get_backtest_history(symbol, model_name, limit)
        return {"results": results, "count": len(results)}
    
    @app.post("/api/backtest/compare")
    async def compare_models(request: CompareRequest):
        """Compare multiple models"""
        try:
            comparison = service.compare_models(
                symbol=request.symbol,
                model_names=request.model_names,
                start_date=request.start_date,
                end_date=request.end_date,
                initial_capital=request.initial_capital
            )
            return comparison
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.delete("/api/cache")
    async def clear_cache():
        """Clear the cache"""
        service.clear_cache()
        return {"message": "Cache cleared"}
    
    logger.info("Starting Unified Backtest Service on port 8004")
    uvicorn.run(app, host="0.0.0.0", port=8004)