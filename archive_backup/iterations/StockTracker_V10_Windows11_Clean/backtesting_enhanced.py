"""
Enhanced Backtesting Backend with Real Trading Simulation
Features:
- $100,000 starting capital
- Realistic commission and slippage
- Multiple strategy testing
- Risk management (stop-loss, take-profit)
- Performance analytics
- Integration with ML predictions and sentiment
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import logging
import json
import sqlite3
from contextlib import contextmanager
import requests

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Enhanced Backtesting Backend", version="2.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database for backtesting results
DB_PATH = "backtest_results.db"

def init_database():
    """Initialize database for storing backtest results"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS backtest_results (
            backtest_id TEXT PRIMARY KEY,
            symbol TEXT NOT NULL,
            strategy TEXT NOT NULL,
            start_date TEXT,
            end_date TEXT,
            initial_capital REAL,
            final_value REAL,
            total_return REAL,
            sharpe_ratio REAL,
            max_drawdown REAL,
            win_rate REAL,
            total_trades INTEGER,
            profitable_trades INTEGER,
            trade_history TEXT,
            performance_metrics TEXT,
            timestamp INTEGER
        )
    """)
    
    conn.commit()
    conn.close()

init_database()

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

class BacktestRequest(BaseModel):
    symbol: str
    strategy: str = "ml_sentiment"  # ml_sentiment, momentum, mean_reversion, buy_hold
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    initial_capital: float = 100000.0
    position_size: float = 0.95  # Use 95% of available capital
    stop_loss: float = 0.05  # 5% stop loss
    take_profit: float = 0.15  # 15% take profit
    use_ml_predictions: bool = True
    use_sentiment: bool = True
    commission: float = 0.001  # 0.1% commission
    slippage: float = 0.0005  # 0.05% slippage

class Trade(BaseModel):
    date: str
    action: str  # buy, sell
    price: float
    shares: int
    value: float
    commission: float
    portfolio_value: float
    reason: str

class BacktestResponse(BaseModel):
    symbol: str
    strategy: str
    start_date: str
    end_date: str
    initial_capital: float
    final_value: float
    total_return: float
    annualized_return: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    win_rate: float
    total_trades: int
    profitable_trades: int
    avg_win: float
    avg_loss: float
    profit_factor: float
    trades: List[Trade]
    equity_curve: List[Dict[str, Any]]
    performance_summary: Dict[str, Any]

def fetch_stock_data(symbol: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """Fetch historical stock data"""
    try:
        stock = yf.Ticker(symbol)
        
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        
        df = stock.history(start=start_date, end=end_date)
        
        if df.empty:
            raise ValueError(f"No data found for {symbol}")
        
        return df
        
    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        raise HTTPException(status_code=404, detail=str(e))

def get_ml_predictions(symbol: str) -> Dict[str, float]:
    """Get ML predictions from ML backend"""
    try:
        response = requests.post(
            "http://localhost:8002/predict",
            json={
                "symbol": symbol,
                "days": 5,
                "model_type": "random_forest",
                "use_sentiment": True
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                "predicted_return": data.get("predicted_change", 0),
                "confidence": data.get("confidence", 50),
                "sentiment_score": data.get("sentiment_analysis", {})
                                      .get("global", {})
                                      .get("sentiment_score", 0)
            }
    except:
        pass
    
    return {"predicted_return": 0, "confidence": 50, "sentiment_score": 0}

def get_sentiment_signal(symbol: str) -> float:
    """Get sentiment signal from web scraper"""
    try:
        response = requests.post(
            "http://localhost:8006/scrape",
            json={
                "symbol": symbol,
                "sources": [],
                "include_global": True,
                "cache_minutes": 5
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            global_sentiment = data.get("global_sentiment", {})
            
            # Calculate composite sentiment signal
            sentiment_score = global_sentiment.get("sentiment_score", 0)
            positive_ratio = global_sentiment.get("positive_ratio", 0.33)
            negative_ratio = global_sentiment.get("negative_ratio", 0.33)
            
            # Weight by market risk
            risk_level = global_sentiment.get("market_risk_level", "medium")
            risk_multiplier = {
                "low": 1.2,
                "medium": 1.0,
                "high": 0.8,
                "critical": 0.5
            }.get(risk_level, 1.0)
            
            signal = (sentiment_score + (positive_ratio - negative_ratio)) * risk_multiplier
            return signal
            
    except:
        pass
    
    return 0.0

def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate technical indicators for strategies"""
    # Moving averages
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
    
    # MACD
    df['MACD'] = df['EMA_12'] - df['EMA_26']
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
    
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # Bollinger Bands
    df['BB_Middle'] = df['SMA_20']
    bb_std = df['Close'].rolling(window=20).std()
    df['BB_Upper'] = df['BB_Middle'] + (2 * bb_std)
    df['BB_Lower'] = df['BB_Middle'] - (2 * bb_std)
    
    # Volume indicators
    df['Volume_Ratio'] = df['Volume'] / df['Volume'].rolling(window=20).mean()
    
    # Momentum
    df['Momentum'] = df['Close'].pct_change(periods=10)
    
    return df

class TradingStrategy:
    """Base trading strategy class"""
    
    def __init__(self, initial_capital: float, commission: float, slippage: float):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.position = 0
        self.commission = commission
        self.slippage = slippage
        self.trades = []
        self.equity_curve = []
        
    def execute_trade(self, date: datetime, action: str, price: float, 
                     shares: int, reason: str):
        """Execute a trade with commission and slippage"""
        # Apply slippage
        if action == "buy":
            execution_price = price * (1 + self.slippage)
        else:
            execution_price = price * (1 - self.slippage)
        
        trade_value = shares * execution_price
        commission_cost = trade_value * self.commission
        
        if action == "buy":
            total_cost = trade_value + commission_cost
            if total_cost <= self.cash:
                self.cash -= total_cost
                self.position += shares
                
                trade = Trade(
                    date=date.strftime('%Y-%m-%d'),
                    action=action,
                    price=execution_price,
                    shares=shares,
                    value=trade_value,
                    commission=commission_cost,
                    portfolio_value=self.get_portfolio_value(price),
                    reason=reason
                )
                self.trades.append(trade)
                return True
        
        elif action == "sell" and self.position >= shares:
            self.cash += trade_value - commission_cost
            self.position -= shares
            
            trade = Trade(
                date=date.strftime('%Y-%m-%d'),
                action=action,
                price=execution_price,
                shares=shares,
                value=trade_value,
                commission=commission_cost,
                portfolio_value=self.get_portfolio_value(price),
                reason=reason
            )
            self.trades.append(trade)
            return True
        
        return False
    
    def get_portfolio_value(self, current_price: float) -> float:
        """Calculate total portfolio value"""
        return self.cash + (self.position * current_price)

class MLSentimentStrategy(TradingStrategy):
    """Strategy using ML predictions and sentiment analysis"""
    
    def __init__(self, symbol: str, **kwargs):
        super().__init__(**kwargs)
        self.symbol = symbol
        self.last_signal_date = None
        
    def generate_signals(self, df: pd.DataFrame, use_ml: bool, use_sentiment: bool) -> pd.DataFrame:
        """Generate trading signals based on ML and sentiment"""
        df = calculate_technical_indicators(df)
        df['Signal'] = 0
        
        for i in range(50, len(df)):  # Start after indicators are calculated
            current_date = df.index[i]
            
            # Skip if we already traded today
            if self.last_signal_date == current_date:
                continue
            
            # Get ML prediction
            ml_signal = 0
            if use_ml and i % 5 == 0:  # Check ML every 5 days
                ml_pred = get_ml_predictions(self.symbol)
                if ml_pred["confidence"] > 60:
                    ml_signal = 1 if ml_pred["predicted_return"] > 2 else -1 if ml_pred["predicted_return"] < -2 else 0
            
            # Get sentiment signal
            sentiment_signal = 0
            if use_sentiment and i % 3 == 0:  # Check sentiment every 3 days
                sent_score = get_sentiment_signal(self.symbol)
                sentiment_signal = 1 if sent_score > 0.2 else -1 if sent_score < -0.2 else 0
            
            # Technical signals
            tech_signal = 0
            
            # MACD crossover
            if df['MACD_Histogram'].iloc[i] > 0 and df['MACD_Histogram'].iloc[i-1] <= 0:
                tech_signal += 1
            elif df['MACD_Histogram'].iloc[i] < 0 and df['MACD_Histogram'].iloc[i-1] >= 0:
                tech_signal -= 1
            
            # RSI signals
            if df['RSI'].iloc[i] < 30:
                tech_signal += 1
            elif df['RSI'].iloc[i] > 70:
                tech_signal -= 1
            
            # Bollinger Band signals
            if df['Close'].iloc[i] < df['BB_Lower'].iloc[i]:
                tech_signal += 1
            elif df['Close'].iloc[i] > df['BB_Upper'].iloc[i]:
                tech_signal -= 1
            
            # Combine signals with weights
            combined_signal = (
                ml_signal * 0.4 +
                sentiment_signal * 0.3 +
                tech_signal * 0.3
            )
            
            # Generate trade signal
            if combined_signal > 0.5:
                df.loc[df.index[i], 'Signal'] = 1
                self.last_signal_date = current_date
            elif combined_signal < -0.5:
                df.loc[df.index[i], 'Signal'] = -1
                self.last_signal_date = current_date
        
        return df

class MomentumStrategy(TradingStrategy):
    """Momentum trading strategy"""
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate momentum-based signals"""
        df = calculate_technical_indicators(df)
        df['Signal'] = 0
        
        for i in range(50, len(df)):
            # Momentum signal
            if df['Momentum'].iloc[i] > 0.05 and df['SMA_20'].iloc[i] > df['SMA_50'].iloc[i]:
                df.loc[df.index[i], 'Signal'] = 1
            elif df['Momentum'].iloc[i] < -0.05 and df['SMA_20'].iloc[i] < df['SMA_50'].iloc[i]:
                df.loc[df.index[i], 'Signal'] = -1
        
        return df

class MeanReversionStrategy(TradingStrategy):
    """Mean reversion trading strategy"""
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate mean reversion signals"""
        df = calculate_technical_indicators(df)
        df['Signal'] = 0
        
        for i in range(50, len(df)):
            # Mean reversion signal
            if df['RSI'].iloc[i] < 30 and df['Close'].iloc[i] < df['BB_Lower'].iloc[i]:
                df.loc[df.index[i], 'Signal'] = 1
            elif df['RSI'].iloc[i] > 70 and df['Close'].iloc[i] > df['BB_Upper'].iloc[i]:
                df.loc[df.index[i], 'Signal'] = -1
        
        return df

def run_backtest(request: BacktestRequest) -> BacktestResponse:
    """Run backtest simulation"""
    try:
        # Fetch historical data
        df = fetch_stock_data(request.symbol, request.start_date, request.end_date)
        
        # Initialize strategy
        if request.strategy == "ml_sentiment":
            strategy = MLSentimentStrategy(
                request.symbol,
                initial_capital=request.initial_capital,
                commission=request.commission,
                slippage=request.slippage
            )
            df = strategy.generate_signals(df, request.use_ml_predictions, request.use_sentiment)
        
        elif request.strategy == "momentum":
            strategy = MomentumStrategy(
                initial_capital=request.initial_capital,
                commission=request.commission,
                slippage=request.slippage
            )
            df = strategy.generate_signals(df)
        
        elif request.strategy == "mean_reversion":
            strategy = MeanReversionStrategy(
                initial_capital=request.initial_capital,
                commission=request.commission,
                slippage=request.slippage
            )
            df = strategy.generate_signals(df)
        
        else:  # buy_hold
            strategy = TradingStrategy(
                initial_capital=request.initial_capital,
                commission=request.commission,
                slippage=request.slippage
            )
            df['Signal'] = 0
            df.loc[df.index[0], 'Signal'] = 1  # Buy on first day
        
        # Execute trades based on signals
        position_open = False
        entry_price = 0
        
        for i in range(len(df)):
            current_price = df['Close'].iloc[i]
            signal = df['Signal'].iloc[i]
            
            # Buy signal
            if signal == 1 and not position_open:
                # Calculate position size
                available_capital = strategy.cash * request.position_size
                shares = int(available_capital / current_price)
                
                if shares > 0:
                    success = strategy.execute_trade(
                        df.index[i],
                        "buy",
                        current_price,
                        shares,
                        f"Buy signal: {request.strategy}"
                    )
                    if success:
                        position_open = True
                        entry_price = current_price
            
            # Sell signal or stop loss/take profit
            elif position_open:
                sell_reason = None
                
                # Check stop loss
                if current_price <= entry_price * (1 - request.stop_loss):
                    sell_reason = f"Stop loss triggered at {request.stop_loss*100}%"
                
                # Check take profit
                elif current_price >= entry_price * (1 + request.take_profit):
                    sell_reason = f"Take profit triggered at {request.take_profit*100}%"
                
                # Regular sell signal
                elif signal == -1:
                    sell_reason = f"Sell signal: {request.strategy}"
                
                if sell_reason:
                    success = strategy.execute_trade(
                        df.index[i],
                        "sell",
                        current_price,
                        strategy.position,
                        sell_reason
                    )
                    if success:
                        position_open = False
                        entry_price = 0
            
            # Record equity curve
            portfolio_value = strategy.get_portfolio_value(current_price)
            strategy.equity_curve.append({
                "date": df.index[i].strftime('%Y-%m-%d'),
                "value": portfolio_value,
                "return": (portfolio_value / request.initial_capital - 1) * 100
            })
        
        # Close any remaining position
        if position_open and strategy.position > 0:
            strategy.execute_trade(
                df.index[-1],
                "sell",
                df['Close'].iloc[-1],
                strategy.position,
                "End of backtest period"
            )
        
        # Calculate performance metrics
        final_value = strategy.get_portfolio_value(df['Close'].iloc[-1])
        total_return = (final_value / request.initial_capital - 1) * 100
        
        # Calculate returns series
        equity_df = pd.DataFrame(strategy.equity_curve)
        equity_df['daily_return'] = equity_df['value'].pct_change()
        
        # Annualized return
        days = (df.index[-1] - df.index[0]).days
        annualized_return = ((final_value / request.initial_capital) ** (365/days) - 1) * 100
        
        # Sharpe ratio
        risk_free_rate = 0.02  # 2% annual risk-free rate
        daily_rf = risk_free_rate / 252
        excess_returns = equity_df['daily_return'] - daily_rf
        sharpe_ratio = np.sqrt(252) * excess_returns.mean() / excess_returns.std() if excess_returns.std() > 0 else 0
        
        # Sortino ratio
        downside_returns = excess_returns[excess_returns < 0]
        sortino_ratio = np.sqrt(252) * excess_returns.mean() / downside_returns.std() if len(downside_returns) > 0 else 0
        
        # Max drawdown
        cumulative = (1 + equity_df['daily_return']).cumprod()
        running_max = cumulative.cummax()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min() * 100
        
        # Win rate and profit factor
        profitable_trades = [t for t in strategy.trades if t.action == "sell"]
        wins = []
        losses = []
        
        for i, trade in enumerate(profitable_trades):
            # Find corresponding buy trade
            buy_trades = [t for t in strategy.trades[:strategy.trades.index(trade)] if t.action == "buy"]
            if buy_trades:
                buy_trade = buy_trades[-1]
                profit = (trade.price - buy_trade.price) * trade.shares - trade.commission - buy_trade.commission
                if profit > 0:
                    wins.append(profit)
                else:
                    losses.append(abs(profit))
        
        win_rate = len(wins) / len(profitable_trades) * 100 if profitable_trades else 0
        avg_win = np.mean(wins) if wins else 0
        avg_loss = np.mean(losses) if losses else 0
        profit_factor = sum(wins) / sum(losses) if losses and sum(losses) > 0 else 0
        
        return BacktestResponse(
            symbol=request.symbol,
            strategy=request.strategy,
            start_date=df.index[0].strftime('%Y-%m-%d'),
            end_date=df.index[-1].strftime('%Y-%m-%d'),
            initial_capital=request.initial_capital,
            final_value=final_value,
            total_return=total_return,
            annualized_return=annualized_return,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            max_drawdown=max_drawdown,
            win_rate=win_rate,
            total_trades=len(strategy.trades),
            profitable_trades=len(wins),
            avg_win=avg_win,
            avg_loss=avg_loss,
            profit_factor=profit_factor,
            trades=strategy.trades,
            equity_curve=strategy.equity_curve[-100:],  # Last 100 points
            performance_summary={
                "best_trade": max(wins) if wins else 0,
                "worst_trade": -max(losses) if losses else 0,
                "total_commission": sum(t.commission for t in strategy.trades),
                "avg_trade_duration": "N/A",  # Would need to calculate
                "exposure_time": len([t for t in strategy.trades if t.action == "buy"]) / len(df) * 100
            }
        )
        
    except Exception as e:
        logger.error(f"Backtest error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Enhanced Backtesting Backend",
        "version": "2.0",
        "features": [
            "$100,000 starting capital",
            "ML and sentiment integration",
            "Multiple strategies",
            "Risk management",
            "Realistic commission and slippage"
        ],
        "strategies": [
            "ml_sentiment",
            "momentum",
            "mean_reversion",
            "buy_hold"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/backtest")
async def run_backtest_endpoint(request: BacktestRequest):
    """Run backtest simulation"""
    return run_backtest(request)

@app.get("/results/{symbol}")
async def get_backtest_results(symbol: str):
    """Get historical backtest results for a symbol"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM backtest_results 
            WHERE symbol = ? 
            ORDER BY timestamp DESC 
            LIMIT 10
        """, (symbol,))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "backtest_id": row["backtest_id"],
                "strategy": row["strategy"],
                "initial_capital": row["initial_capital"],
                "final_value": row["final_value"],
                "total_return": row["total_return"],
                "sharpe_ratio": row["sharpe_ratio"],
                "max_drawdown": row["max_drawdown"],
                "win_rate": row["win_rate"],
                "total_trades": row["total_trades"]
            })
    
    return {"symbol": symbol, "results": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)