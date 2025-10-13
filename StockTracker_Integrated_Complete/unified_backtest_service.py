#!/usr/bin/env python3
"""
Unified Backtesting Service
Centralized backtesting engine that serves all modules
Provides consistent backtesting results across the entire application
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import logging
import json
import sqlite3
from pathlib import Path
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BacktestResult:
    """Unified backtest result structure"""
    symbol: str
    start_date: str
    end_date: str
    model_name: str
    
    # Performance metrics
    total_return: float
    annualized_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    
    # Prediction accuracy
    direction_accuracy: float
    mae: float  # Mean Absolute Error
    rmse: float  # Root Mean Square Error
    mape: float  # Mean Absolute Percentage Error
    
    # Risk metrics
    volatility: float
    var_95: float  # Value at Risk 95%
    cvar_95: float  # Conditional VaR 95%
    
    # Trade statistics
    total_trades: int
    winning_trades: int
    losing_trades: int
    avg_win: float
    avg_loss: float
    
    # Additional metrics
    profit_factor: float
    recovery_factor: float
    calmar_ratio: float
    
    # Metadata
    backtest_timestamp: str
    execution_time: float
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

class UnifiedBacktestService:
    """
    Centralized backtesting service for all modules
    Provides consistent backtesting across the application
    """
    
    def __init__(self, db_path: str = "backtest_results.db"):
        self.db_path = db_path
        self.executor = ThreadPoolExecutor(max_workers=4)
        self._init_database()
        
    def _init_database(self):
        """Initialize SQLite database for storing backtest results"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS backtest_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                model_name TEXT,
                start_date TEXT,
                end_date TEXT,
                total_return REAL,
                sharpe_ratio REAL,
                max_drawdown REAL,
                direction_accuracy REAL,
                win_rate REAL,
                total_trades INTEGER,
                result_json TEXT,
                backtest_timestamp TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, model_name, start_date, end_date)
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_symbol_model 
            ON backtest_results(symbol, model_name)
        ''')
        
        conn.commit()
        conn.close()
    
    async def run_backtest(
        self,
        symbol: str,
        model: Any,  # Can be any model object with predict method
        start_date: str,
        end_date: str,
        model_name: str = "ensemble",
        initial_capital: float = 100000,
        use_cache: bool = True
    ) -> BacktestResult:
        """
        Run backtesting for a given model and time period
        
        Args:
            symbol: Stock symbol to backtest
            model: Model object with predict method
            start_date: Start date for backtesting
            end_date: End date for backtesting
            model_name: Name of the model for identification
            initial_capital: Starting capital for simulation
            use_cache: Whether to use cached results if available
        
        Returns:
            BacktestResult object with comprehensive metrics
        """
        
        start_time = datetime.now()
        
        # Check cache if enabled
        if use_cache:
            cached_result = self._get_cached_result(symbol, model_name, start_date, end_date)
            if cached_result:
                logger.info(f"Using cached backtest result for {symbol} - {model_name}")
                return cached_result
        
        try:
            # Fetch historical data
            data = await self._fetch_historical_data(symbol, start_date, end_date)
            
            if data is None or len(data) < 20:
                logger.error(f"Insufficient data for backtesting {symbol}")
                return self._create_empty_result(symbol, start_date, end_date, model_name)
            
            # Run the backtest simulation
            result = await self._simulate_trading(
                data, model, symbol, model_name, initial_capital
            )
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            result.execution_time = execution_time
            result.backtest_timestamp = datetime.now().isoformat()
            
            # Store result in database
            self._store_result(result)
            
            logger.info(f"Backtest completed for {symbol} - {model_name}: "
                       f"Return: {result.total_return:.2%}, "
                       f"Sharpe: {result.sharpe_ratio:.2f}, "
                       f"Accuracy: {result.direction_accuracy:.2%}")
            
            return result
            
        except Exception as e:
            logger.error(f"Backtest failed for {symbol}: {str(e)}")
            return self._create_empty_result(symbol, start_date, end_date, model_name)
    
    async def _fetch_historical_data(
        self, 
        symbol: str, 
        start_date: str, 
        end_date: str
    ) -> Optional[pd.DataFrame]:
        """Fetch historical data for backtesting"""
        try:
            # Convert string dates to datetime
            start_dt = pd.to_datetime(start_date)
            end_dt = pd.to_datetime(end_date)
            
            # Fetch data using yfinance
            stock = yf.Ticker(symbol)
            data = stock.history(start=start_dt, end=end_dt)
            
            if data.empty:
                logger.warning(f"No data available for {symbol} between {start_date} and {end_date}")
                return None
            
            # Add technical indicators
            data = self._add_technical_indicators(data)
            
            return data
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return None
    
    def _add_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add technical indicators for backtesting"""
        # Simple Moving Averages
        data['SMA_20'] = data['Close'].rolling(window=20).mean()
        data['SMA_50'] = data['Close'].rolling(window=50).mean()
        
        # Relative Strength Index
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        data['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = data['Close'].ewm(span=12, adjust=False).mean()
        exp2 = data['Close'].ewm(span=26, adjust=False).mean()
        data['MACD'] = exp1 - exp2
        data['Signal'] = data['MACD'].ewm(span=9, adjust=False).mean()
        
        # Bollinger Bands
        data['BB_middle'] = data['Close'].rolling(window=20).mean()
        bb_std = data['Close'].rolling(window=20).std()
        data['BB_upper'] = data['BB_middle'] + (bb_std * 2)
        data['BB_lower'] = data['BB_middle'] - (bb_std * 2)
        
        # Volume indicators
        data['Volume_SMA'] = data['Volume'].rolling(window=20).mean()
        data['Volume_Ratio'] = data['Volume'] / data['Volume_SMA']
        
        return data
    
    async def _simulate_trading(
        self,
        data: pd.DataFrame,
        model: Any,
        symbol: str,
        model_name: str,
        initial_capital: float
    ) -> BacktestResult:
        """Simulate trading based on model predictions"""
        
        # Initialize portfolio
        capital = initial_capital
        position = 0
        trades = []
        equity_curve = [initial_capital]
        
        # Generate predictions for the entire period
        predictions = []
        actual_returns = []
        
        for i in range(20, len(data) - 1):  # Start from 20 to have enough history
            # Prepare features for prediction
            features = self._prepare_features(data.iloc[:i+1])
            
            # Get model prediction
            try:
                if hasattr(model, 'predict'):
                    pred = model.predict(features)
                else:
                    # Fallback to simple trend following
                    pred = 1 if data['Close'].iloc[i] > data['SMA_20'].iloc[i] else -1
                
                predictions.append(pred)
                
                # Calculate actual return
                actual_return = (data['Close'].iloc[i+1] - data['Close'].iloc[i]) / data['Close'].iloc[i]
                actual_returns.append(actual_return)
                
                # Execute trade based on prediction
                if pred > 0 and position == 0:  # Buy signal
                    position = capital / data['Close'].iloc[i]
                    trades.append({
                        'date': data.index[i],
                        'type': 'BUY',
                        'price': data['Close'].iloc[i],
                        'shares': position
                    })
                elif pred < 0 and position > 0:  # Sell signal
                    capital = position * data['Close'].iloc[i]
                    trades.append({
                        'date': data.index[i],
                        'type': 'SELL',
                        'price': data['Close'].iloc[i],
                        'shares': position
                    })
                    position = 0
                
                # Update equity
                if position > 0:
                    equity = position * data['Close'].iloc[i]
                else:
                    equity = capital
                equity_curve.append(equity)
                
            except Exception as e:
                logger.warning(f"Prediction failed at index {i}: {str(e)}")
                predictions.append(0)
                actual_returns.append(0)
        
        # Close final position if any
        if position > 0:
            capital = position * data['Close'].iloc[-1]
            trades.append({
                'date': data.index[-1],
                'type': 'SELL',
                'price': data['Close'].iloc[-1],
                'shares': position
            })
        
        # Calculate metrics
        metrics = self._calculate_metrics(
            equity_curve,
            trades,
            predictions,
            actual_returns,
            initial_capital,
            data
        )
        
        # Create result
        result = BacktestResult(
            symbol=symbol,
            start_date=data.index[0].strftime('%Y-%m-%d'),
            end_date=data.index[-1].strftime('%Y-%m-%d'),
            model_name=model_name,
            **metrics
        )
        
        return result
    
    def _prepare_features(self, data: pd.DataFrame) -> np.ndarray:
        """Prepare features for model prediction"""
        # Use last row of data for features
        last_row = data.iloc[-1]
        
        features = [
            last_row['Close'],
            last_row['Volume'],
            last_row['RSI'] if 'RSI' in data.columns else 50,
            last_row['MACD'] if 'MACD' in data.columns else 0,
            last_row['Volume_Ratio'] if 'Volume_Ratio' in data.columns else 1,
        ]
        
        # Add price change features
        if len(data) > 1:
            features.extend([
                (last_row['Close'] - data.iloc[-2]['Close']) / data.iloc[-2]['Close'],
                (last_row['High'] - last_row['Low']) / last_row['Close'],
            ])
        else:
            features.extend([0, 0])
        
        return np.array(features).reshape(1, -1)
    
    def _calculate_metrics(
        self,
        equity_curve: List[float],
        trades: List[Dict],
        predictions: List[float],
        actual_returns: List[float],
        initial_capital: float,
        data: pd.DataFrame
    ) -> Dict:
        """Calculate comprehensive backtest metrics"""
        
        equity_array = np.array(equity_curve)
        returns = np.diff(equity_array) / equity_array[:-1]
        
        # Remove NaN and inf values
        returns = returns[np.isfinite(returns)]
        
        # Basic metrics
        total_return = (equity_array[-1] - initial_capital) / initial_capital
        
        # Annualized return (assuming 252 trading days)
        n_days = len(data)
        annualized_return = (1 + total_return) ** (252 / n_days) - 1 if n_days > 0 else 0
        
        # Sharpe ratio
        if len(returns) > 0 and np.std(returns) > 0:
            sharpe_ratio = np.sqrt(252) * np.mean(returns) / np.std(returns)
        else:
            sharpe_ratio = 0
        
        # Maximum drawdown
        peak = np.maximum.accumulate(equity_array)
        drawdown = (equity_array - peak) / peak
        max_drawdown = np.min(drawdown) if len(drawdown) > 0 else 0
        
        # Win rate
        winning_trades = sum(1 for t in trades if t['type'] == 'SELL' and 
                           any(b['type'] == 'BUY' and b['price'] < t['price'] 
                               for b in trades))
        total_trades = len([t for t in trades if t['type'] == 'SELL'])
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        # Direction accuracy
        if len(predictions) > 0 and len(actual_returns) > 0:
            pred_direction = np.sign(predictions)
            actual_direction = np.sign(actual_returns)
            direction_accuracy = np.mean(pred_direction == actual_direction)
        else:
            direction_accuracy = 0.5
        
        # Error metrics
        if len(predictions) > 0 and len(actual_returns) > 0:
            mae = np.mean(np.abs(np.array(predictions) - np.array(actual_returns)))
            rmse = np.sqrt(np.mean((np.array(predictions) - np.array(actual_returns))**2))
            mape = np.mean(np.abs((np.array(actual_returns) - np.array(predictions)) / 
                                 (np.array(actual_returns) + 1e-10))) * 100
        else:
            mae = rmse = mape = 0
        
        # Risk metrics
        volatility = np.std(returns) * np.sqrt(252) if len(returns) > 0 else 0
        var_95 = np.percentile(returns, 5) if len(returns) > 0 else 0
        cvar_95 = np.mean(returns[returns <= var_95]) if len(returns) > 0 else 0
        
        # Trade statistics
        avg_win = np.mean([r for r in returns if r > 0]) if any(returns > 0) else 0
        avg_loss = np.mean([r for r in returns if r < 0]) if any(returns < 0) else 0
        
        # Additional metrics
        profit_factor = abs(sum(r for r in returns if r > 0) / 
                          sum(r for r in returns if r < 0)) if any(returns < 0) else 0
        
        recovery_factor = abs(total_return / max_drawdown) if max_drawdown != 0 else 0
        
        calmar_ratio = annualized_return / abs(max_drawdown) if max_drawdown != 0 else 0
        
        return {
            'total_return': total_return,
            'annualized_return': annualized_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'direction_accuracy': direction_accuracy,
            'mae': mae,
            'rmse': rmse,
            'mape': mape,
            'volatility': volatility,
            'var_95': var_95,
            'cvar_95': cvar_95,
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': total_trades - winning_trades,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'recovery_factor': recovery_factor,
            'calmar_ratio': calmar_ratio,
            'backtest_timestamp': '',
            'execution_time': 0
        }
    
    def _store_result(self, result: BacktestResult):
        """Store backtest result in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO backtest_results 
                (symbol, model_name, start_date, end_date, total_return,
                 sharpe_ratio, max_drawdown, direction_accuracy, win_rate,
                 total_trades, result_json, backtest_timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                result.symbol,
                result.model_name,
                result.start_date,
                result.end_date,
                result.total_return,
                result.sharpe_ratio,
                result.max_drawdown,
                result.direction_accuracy,
                result.win_rate,
                result.total_trades,
                json.dumps(result.to_dict()),
                result.backtest_timestamp
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"Error storing backtest result: {str(e)}")
        finally:
            conn.close()
    
    def _get_cached_result(
        self, 
        symbol: str, 
        model_name: str, 
        start_date: str, 
        end_date: str
    ) -> Optional[BacktestResult]:
        """Retrieve cached backtest result from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT result_json FROM backtest_results
                WHERE symbol = ? AND model_name = ? 
                AND start_date = ? AND end_date = ?
                AND datetime(created_at) > datetime('now', '-1 day')
            ''', (symbol, model_name, start_date, end_date))
            
            row = cursor.fetchone()
            if row:
                result_dict = json.loads(row[0])
                return BacktestResult(**result_dict)
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving cached result: {str(e)}")
            return None
        finally:
            conn.close()
    
    def _create_empty_result(
        self, 
        symbol: str, 
        start_date: str, 
        end_date: str, 
        model_name: str
    ) -> BacktestResult:
        """Create empty result for failed backtests"""
        return BacktestResult(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            model_name=model_name,
            total_return=0,
            annualized_return=0,
            sharpe_ratio=0,
            max_drawdown=0,
            win_rate=0,
            direction_accuracy=0.5,
            mae=0,
            rmse=0,
            mape=0,
            volatility=0,
            var_95=0,
            cvar_95=0,
            total_trades=0,
            winning_trades=0,
            losing_trades=0,
            avg_win=0,
            avg_loss=0,
            profit_factor=0,
            recovery_factor=0,
            calmar_ratio=0,
            backtest_timestamp=datetime.now().isoformat(),
            execution_time=0
        )
    
    async def get_historical_backtests(
        self, 
        symbol: Optional[str] = None,
        model_name: Optional[str] = None,
        limit: int = 10
    ) -> List[BacktestResult]:
        """Retrieve historical backtest results"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT result_json FROM backtest_results WHERE 1=1"
        params = []
        
        if symbol:
            query += " AND symbol = ?"
            params.append(symbol)
        
        if model_name:
            query += " AND model_name = ?"
            params.append(model_name)
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        try:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            results = []
            for row in rows:
                result_dict = json.loads(row[0])
                results.append(BacktestResult(**result_dict))
            
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving historical backtests: {str(e)}")
            return []
        finally:
            conn.close()
    
    async def compare_models(
        self,
        symbol: str,
        models: Dict[str, Any],  # {"model_name": model_object}
        start_date: str,
        end_date: str
    ) -> Dict[str, BacktestResult]:
        """Compare multiple models on the same data"""
        results = {}
        
        for model_name, model in models.items():
            logger.info(f"Backtesting {model_name} for {symbol}")
            result = await self.run_backtest(
                symbol, model, start_date, end_date, model_name
            )
            results[model_name] = result
        
        return results

# Create global instance
backtest_service = UnifiedBacktestService()

# API endpoint functions for use by other modules
async def run_backtest_api(
    symbol: str,
    model_name: str = "ensemble",
    start_date: str = None,
    end_date: str = None
) -> Dict:
    """API function for running backtests from other modules"""
    
    # Default to last 6 months if dates not provided
    if not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')
    if not start_date:
        start_date = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
    
    # For API calls without model object, use a simple trend-following strategy
    class SimpleModel:
        def predict(self, features):
            # Simple momentum strategy for demonstration
            return 1 if features[0, 0] > features[0, 2] else -1
    
    model = SimpleModel()
    result = await backtest_service.run_backtest(
        symbol, model, start_date, end_date, model_name
    )
    
    return result.to_dict()

async def get_backtest_history_api(
    symbol: Optional[str] = None,
    model_name: Optional[str] = None,
    limit: int = 10
) -> List[Dict]:
    """API function for retrieving backtest history"""
    results = await backtest_service.get_historical_backtests(
        symbol, model_name, limit
    )
    return [r.to_dict() for r in results]