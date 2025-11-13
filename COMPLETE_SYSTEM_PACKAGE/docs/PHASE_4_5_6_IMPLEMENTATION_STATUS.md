# Phases 4-6 Implementation Status

**Date**: November 1, 2025  
**Current Progress**: Ensemble Model Complete, Starting Visualization & Advanced Features

---

## ✅ COMPLETED: Synthetic FinBERT Removal & New Ensemble

### What Was Done:

#### 1. **Removed Synthetic FinBERT** ✅
- Deleted `_predict_finbert()` method from prediction_engine.py
- Removed price momentum "sentiment proxy" approach
- Updated documentation to reflect removal

#### 2. **Created New 3-Model Ensemble** ✅
The new ensemble combines:

**A. LSTM Model (40% weight)**
- Moving average crossovers (SMA-20, SMA-50)
- Trend continuation signals
- Momentum indicators (5-day, 20-day)
- Volatility adjustment

**B. Technical Analysis Model (35% weight)** - NEW
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands position
- Multiple moving averages
- Comprehensive technical scoring

**C. Momentum Model (25% weight)** - NEW
- Short/medium/long-term momentum
- Rate of Change (ROC-10, ROC-20)
- Trend strength (linear regression)
- Acceleration (second derivative)
- Multi-timeframe analysis

#### 3. **Consensus Bonus Feature** ✅
- When all 3 models agree on BUY or SELL
- Confidence increased by 15%
- Ensemble score boosted by 10%
- More decisive signals

#### 4. **Updated UI & API** ✅
- Removed "FinBERT" option from dropdown
- Added "Technical Analysis" option
- Added "Momentum Strategy" option
- Updated Ensemble description: "LSTM + Technical + Momentum"
- Updated API endpoints to reflect new models

---

## 📊 PHASE 4: Advanced Analytics & Visualization

### Status: **IMPLEMENTATION REQUIRED**

These features require modifications to:
1. `trading_simulator.py` - Track additional data
2. `app_finbert_v4_dev.py` - Return chart data in API
3. `finbert_v4_enhanced_ui.html` - Display charts using ECharts

---

### 4.1 Equity Curve Chart ⏳ (Highest Priority)

**Purpose**: Visualize portfolio value over time

**Implementation Steps:**

#### A. Backend Changes (trading_simulator.py)

```python
# Add to TradingSimulator.__init__:
self.equity_history = []  # List of (timestamp, equity_value) tuples

# Add to execute_signal method (after trade execution):
current_equity = self.current_capital + sum([
    pos['shares'] * price for pos in self.positions
])
self.equity_history.append({
    'timestamp': timestamp.strftime('%Y-%m-%d'),
    'equity': round(current_equity, 2),
    'cash': round(self.current_capital, 2),
    'positions_value': round(current_equity - self.current_capital, 2)
})

# Add to calculate_performance_metrics():
return_data = {
    # ... existing metrics ...
    'equity_curve': self.equity_history
}
```

#### B. API Changes (app_finbert_v4_dev.py)

```python
# In run_backtest() endpoint, add to response:
response = {
    # ... existing fields ...
    'charts': {
        'equity_curve': metrics.get('equity_curve', [])
    }
}
```

#### C. Frontend Changes (finbert_v4_enhanced_ui.html)

```javascript
// Add after results display
if (result.charts && result.charts.equity_curve) {
    displayEquityCurve(result.charts.equity_curve);
}

function displayEquityCurve(data) {
    const chartDiv = document.getElementById('equityCurveChart');
    const chart = echarts.init(chartDiv);
    
    const option = {
        title: { text: 'Equity Curve', left: 'center' },
        tooltip: { trigger: 'axis' },
        xAxis: {
            type: 'category',
            data: data.map(d => d.timestamp)
        },
        yAxis: {
            type: 'value',
            axisLabel: { formatter: '${value}' }
        },
        series: [{
            name: 'Portfolio Value',
            type: 'line',
            data: data.map(d => d.equity),
            smooth: true,
            lineStyle: { color: '#10B981', width: 2 }
        }]
    };
    
    chart.setOption(option);
}
```

**Files to Modify:**
- `/home/user/webapp/FinBERT_v4.0_Windows11_ENHANCED/models/backtesting/trading_simulator.py` (lines ~75, ~150, ~400)
- `/home/user/webapp/FinBERT_v4.0_Windows11_ENHANCED/app_finbert_v4_dev.py` (line ~700)
- `/home/user/webapp/FinBERT_v4.0_Windows11_ENHANCED/templates/finbert_v4_enhanced_ui.html` (lines ~650, ~1600)

**Estimated Time**: 1-2 hours

---

### 4.2 Drawdown Chart ⏳

**Purpose**: Show peak-to-trough declines

**Implementation:**

```python
# In trading_simulator.py - calculate_performance_metrics():
def calculate_drawdown_series(equity_curve):
    """Calculate drawdown at each point"""
    drawdowns = []
    peak = equity_curve[0]['equity']
    
    for point in equity_curve:
        equity = point['equity']
        if equity > peak:
            peak = equity
        drawdown = (equity - peak) / peak * 100
        drawdowns.append({
            'timestamp': point['timestamp'],
            'drawdown': round(drawdown, 2),
            'peak': round(peak, 2)
        })
    
    return drawdowns

# Add to return metrics:
'drawdown_curve': calculate_drawdown_series(self.equity_history)
```

**ECharts Configuration:**
```javascript
series: [{
    name: 'Drawdown',
    type: 'line',
    data: drawdowns.map(d => d.drawdown),
    areaStyle: { color: 'rgba(239, 68, 68, 0.2)' },
    lineStyle: { color: '#EF4444' }
}]
```

**Estimated Time**: 1 hour

---

### 4.3 Trade Distribution Chart ⏳

**Purpose**: Visualize win/loss distribution

**Implementation:**

```python
# In trading_simulator.py:
def get_trade_distribution(self):
    """Get P&L distribution by buckets"""
    buckets = {
        'large_loss': 0,    # < -5%
        'medium_loss': 0,   # -5% to -2%
        'small_loss': 0,    # -2% to 0%
        'small_win': 0,     # 0% to +2%
        'medium_win': 0,    # +2% to +5%
        'large_win': 0      # > +5%
    }
    
    for trade in self.closed_trades:
        if trade.return_pct is None:
            continue
        
        ret = trade.return_pct * 100
        if ret < -5:
            buckets['large_loss'] += 1
        elif ret < -2:
            buckets['medium_loss'] += 1
        elif ret < 0:
            buckets['small_loss'] += 1
        elif ret < 2:
            buckets['small_win'] += 1
        elif ret < 5:
            buckets['medium_win'] += 1
        else:
            buckets['large_win'] += 1
    
    return buckets
```

**ECharts Bar Chart:**
```javascript
{
    type: 'bar',
    data: [
        buckets.large_loss,
        buckets.medium_loss,
        buckets.small_loss,
        buckets.small_win,
        buckets.medium_win,
        buckets.large_win
    ],
    itemStyle: {
        color: function(params) {
            const colors = ['#DC2626', '#EF4444', '#F87171', 
                           '#34D399', '#10B981', '#059669'];
            return colors[params.dataIndex];
        }
    }
}
```

**Estimated Time**: 1 hour

---

### 4.4 Monthly Returns Heatmap ⏳

**Purpose**: Show performance by month

**Implementation:**

```python
# In trading_simulator.py:
def get_monthly_returns(self):
    """Calculate monthly returns"""
    monthly_data = {}
    
    # Group equity by month
    for i in range(1, len(self.equity_history)):
        prev = self.equity_history[i-1]
        curr = self.equity_history[i]
        
        prev_date = datetime.strptime(prev['timestamp'], '%Y-%m-%d')
        curr_date = datetime.strptime(curr['timestamp'], '%Y-%m-%d')
        
        if prev_date.month != curr_date.month:
            # Month changed - calculate return
            month_key = curr_date.strftime('%Y-%m')
            ret = (curr['equity'] - prev['equity']) / prev['equity'] * 100
            monthly_data[month_key] = round(ret, 2)
    
    return monthly_data
```

**ECharts Heatmap:**
```javascript
{
    type: 'heatmap',
    data: monthlyData.map((val, idx) => [idx, 0, val]),
    label: { show: true, formatter: '{c}%' },
    itemStyle: {
        color: function(params) {
            const value = params.value[2];
            if (value > 5) return '#059669';  // Dark green
            if (value > 2) return '#10B981';  // Green
            if (value > 0) return '#34D399';  // Light green
            if (value > -2) return '#F87171'; // Light red
            if (value > -5) return '#EF4444'; // Red
            return '#DC2626';                 // Dark red
        }
    }
}
```

**Estimated Time**: 2 hours

---

## 📊 PHASE 5: Portfolio Backtesting

### Status: **DESIGN COMPLETE, IMPLEMENTATION REQUIRED**

---

### 5.1 Multi-Stock Portfolio Backtesting ⏳ (HIGH PRIORITY)

**Purpose**: Test multiple stocks simultaneously with capital allocation

**New File Required**: `portfolio_backtest.py`

**Key Components:**

```python
class PortfolioBacktester:
    def __init__(self, 
                 symbols: List[str],
                 allocations: Dict[str, float],  # symbol -> weight
                 initial_capital: float,
                 rebalance_frequency: str = 'monthly'):
        """
        Portfolio backtester for multiple stocks
        
        Args:
            symbols: List of stock symbols
            allocations: Capital allocation per stock (must sum to 1.0)
            initial_capital: Total starting capital
            rebalance_frequency: 'monthly', 'quarterly', 'never'
        """
        self.symbols = symbols
        self.allocations = allocations
        self.initial_capital = initial_capital
        self.rebalance_frequency = rebalance_frequency
        
        # Individual stock simulators
        self.stock_simulators = {}
        for symbol in symbols:
            capital = initial_capital * allocations[symbol]
            self.stock_simulators[symbol] = TradingSimulator(
                initial_capital=capital
            )
    
    def run_portfolio_backtest(self, 
                               start_date: str,
                               end_date: str,
                               model_type: str = 'ensemble') -> Dict:
        """
        Run backtest for entire portfolio
        
        Returns:
            {
                'total_return': float,
                'sharpe_ratio': float,
                'max_drawdown': float,
                'stock_returns': Dict[str, float],
                'portfolio_equity_curve': List[Dict],
                'correlation_matrix': np.ndarray
            }
        """
        results = {}
        
        # Run backtest for each stock
        for symbol in self.symbols:
            # Load data
            loader = HistoricalDataLoader(symbol)
            data = loader.load_price_data(start_date, end_date)
            
            # Generate predictions
            engine = BacktestPredictionEngine(model_type=model_type)
            predictions = engine.walk_forward_backtest(data, start_date, end_date)
            
            # Simulate trading
            simulator = self.stock_simulators[symbol]
            for _, row in predictions.iterrows():
                simulator.execute_signal(
                    timestamp=row['timestamp'],
                    signal=row['prediction'],
                    price=row['actual_price'],
                    confidence=row['confidence']
                )
            
            # Store results
            results[symbol] = simulator.calculate_performance_metrics()
        
        # Calculate portfolio-level metrics
        portfolio_metrics = self._calculate_portfolio_metrics(results)
        
        return portfolio_metrics
    
    def _calculate_portfolio_metrics(self, stock_results: Dict) -> Dict:
        """Aggregate results across all stocks"""
        total_initial = sum(
            self.allocations[s] * self.initial_capital 
            for s in self.symbols
        )
        
        total_final = sum(
            stock_results[s]['final_equity'] 
            for s in self.symbols
        )
        
        total_return = (total_final - total_initial) / total_initial * 100
        
        # Weighted Sharpe ratio
        weighted_sharpe = sum(
            stock_results[s]['sharpe_ratio'] * self.allocations[s]
            for s in self.symbols
        )
        
        return {
            'total_return': round(total_return, 2),
            'sharpe_ratio': round(weighted_sharpe, 2),
            'initial_capital': total_initial,
            'final_capital': round(total_final, 2),
            'stock_results': stock_results,
            'allocations': self.allocations
        }
```

**API Endpoint:**
```python
@app.route('/api/backtest/portfolio', methods=['POST'])
def run_portfolio_backtest():
    """
    Run portfolio backtest
    
    Request body:
    {
        "symbols": ["AAPL", "MSFT", "GOOGL"],
        "allocations": {"AAPL": 0.4, "MSFT": 0.4, "GOOGL": 0.2},
        "start_date": "2023-01-01",
        "end_date": "2024-01-01",
        "initial_capital": 10000,
        "model_type": "ensemble"
    }
    """
    data = request.get_json()
    
    portfol io = PortfolioBacktester(
        symbols=data['symbols'],
        allocations=data['allocations'],
        initial_capital=data['initial_capital']
    )
    
    results = portfolio.run_portfolio_backtest(
        start_date=data['start_date'],
        end_date=data['end_date'],
        model_type=data.get('model_type', 'ensemble')
    )
    
    return jsonify(results)
```

**Estimated Time**: 3-4 hours

---

### 5.2 Correlation Analysis ⏳

**Purpose**: Analyze stock correlations for diversification

**Implementation:**

```python
def calculate_correlation_matrix(self, stock_returns: Dict[str, List[float]]) -> np.ndarray:
    """Calculate correlation matrix between stocks"""
    # Convert to pandas DataFrame
    returns_df = pd.DataFrame(stock_returns)
    
    # Calculate correlation
    correlation_matrix = returns_df.corr()
    
    return correlation_matrix.values

def get_diversification_score(self, correlation_matrix: np.ndarray) -> float:
    """
    Calculate diversification score (lower correlation = better)
    
    Returns score from 0-100 (higher is more diversified)
    """
    # Average absolute correlation (excluding diagonal)
    n = len(correlation_matrix)
    total_corr = 0
    count = 0
    
    for i in range(n):
        for j in range(i+1, n):
            total_corr += abs(correlation_matrix[i][j])
            count += 1
    
    avg_corr = total_corr / count if count > 0 else 0
    
    # Convert to diversification score (0-100)
    diversification_score = (1 - avg_corr) * 100
    
    return round(diversification_score, 1)
```

**Frontend Visualization:**
```javascript
// Correlation heatmap
{
    type: 'heatmap',
    data: correlationData,
    label: { show: true, formatter: '{c}' },
    visualMap: {
        min: -1,
        max: 1,
        inRange: {
            color: ['#DC2626', '#FFF', '#10B981']  // Red -> White -> Green
        }
    }
}
```

**Estimated Time**: 2 hours

---

## 🔧 PHASE 6: Strategy Optimization

### Status: **DESIGN COMPLETE, IMPLEMENTATION REQUIRED**

---

### 6.1 Parameter Optimization (Grid Search) ⏳ (HIGH PRIORITY)

**Purpose**: Find optimal parameters automatically

**New File**: `parameter_optimizer.py`

```python
class ParameterOptimizer:
    """
    Optimize backtest parameters using grid search
    """
    
    def __init__(self, symbol: str, start_date: str, end_date: str):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
    
    def optimize_parameters(self, 
                          param_grid: Dict[str, List],
                          optimization_metric: str = 'sharpe_ratio') -> Dict:
        """
        Grid search over parameters
        
        Args:
            param_grid: {
                'confidence_threshold': [0.5, 0.6, 0.7],
                'lookback_days': [30, 60, 90],
                'max_position_size': [0.15, 0.20, 0.25]
            }
            optimization_metric: 'sharpe_ratio', 'total_return', 'win_rate'
        
        Returns:
            Best parameters and all results
        """
        results = []
        
        # Generate all combinations
        from itertools import product
        param_names = list(param_grid.keys())
        param_values = list(param_grid.values())
        
        for combination in product(*param_values):
            params = dict(zip(param_names, combination))
            
            # Run backtest with these parameters
            score = self._run_backtest_with_params(params)
            
            results.append({
                'params': params,
                'score': score[optimization_metric],
                'full_results': score
            })
        
        # Find best parameters
        best = max(results, key=lambda x: x['score'])
        
        return {
            'best_params': best['params'],
            'best_score': best['score'],
            'all_results': sorted(results, key=lambda x: x['score'], reverse=True)
        }
    
    def _run_backtest_with_params(self, params: Dict) -> Dict:
        """Run single backtest with given parameters"""
        # Load data
        loader = HistoricalDataLoader(self.symbol)
        data = loader.load_price_data(self.start_date, self.end_date)
        
        # Run backtest
        engine = BacktestPredictionEngine(
            model_type='ensemble',
            confidence_threshold=params['confidence_threshold']
        )
        
        predictions = engine.walk_forward_backtest(
            data, 
            self.start_date, 
            self.end_date,
            lookback_days=params['lookback_days']
        )
        
        simulator = TradingSimulator(
            max_position_size=params['max_position_size']
        )
        
        for _, row in predictions.iterrows():
            simulator.execute_signal(
                timestamp=row['timestamp'],
                signal=row['prediction'],
                price=row['actual_price'],
                confidence=row['confidence']
            )
        
        return simulator.calculate_performance_metrics()
```

**API Endpoint:**
```python
@app.route('/api/backtest/optimize', methods=['POST'])
def optimize_parameters():
    """
    Optimize backtest parameters
    
    Request:
    {
        "symbol": "AAPL",
        "start_date": "2023-01-01",
        "end_date": "2024-01-01",
        "param_grid": {
            "confidence_threshold": [0.5, 0.6, 0.7],
            "lookback_days": [30, 60, 90]
        },
        "optimization_metric": "sharpe_ratio"
    }
    """
    data = request.get_json()
    
    optimizer = ParameterOptimizer(
        symbol=data['symbol'],
        start_date=data['start_date'],
        end_date=data['end_date']
    )
    
    results = optimizer.optimize_parameters(
        param_grid=data['param_grid'],
        optimization_metric=data.get('optimization_metric', 'sharpe_ratio')
    )
    
    return jsonify(results)
```

**Estimated Time**: 4-6 hours

---

### 6.2 Walk-Forward Optimization ⏳

**Purpose**: Prevent overfitting by testing on out-of-sample data

**Implementation:**

```python
class WalkForwardOptimizer:
    """
    Walk-forward optimization to prevent overfitting
    """
    
    def __init__(self, 
                 symbol: str,
                 full_start: str,
                 full_end: str,
                 train_period_months: int = 12,
                 test_period_months: int = 3):
        """
        Args:
            train_period_months: Months to use for optimization
            test_period_months: Months to test optimized parameters
        """
        self.symbol = symbol
        self.full_start = full_start
        self.full_end = full_end
        self.train_period = train_period_months
        self.test_period = test_period_months
    
    def run_walk_forward(self, param_grid: Dict) -> Dict:
        """
        Run walk-forward optimization
        
        Process:
        1. Split data into train/test windows
        2. Optimize on train window
        3. Test on out-of-sample test window
        4. Roll window forward
        5. Repeat
        
        Returns:
            {
                'windows': List of results per window,
                'avg_in_sample_score': float,
                'avg_out_sample_score': float,
                'degradation': float  # How much performance drops OOS
            }
        """
        windows = self._create_windows()
        results = []
        
        for window in windows:
            # Optimize on training period
            optimizer = ParameterOptimizer(
                self.symbol,
                window['train_start'],
                window['train_end']
            )
            
            opt_result = optimizer.optimize_parameters(param_grid)
            best_params = opt_result['best_params']
            
            # Test on validation period
            test_score = self._test_parameters(
                best_params,
                window['test_start'],
                window['test_end']
            )
            
            results.append({
                'window': window,
                'train_score': opt_result['best_score'],
                'test_score': test_score,
                'best_params': best_params
            })
        
        # Calculate summary statistics
        avg_train = np.mean([r['train_score'] for r in results])
        avg_test = np.mean([r['test_score'] for r in results])
        degradation = (avg_train - avg_test) / avg_train * 100 if avg_train > 0 else 0
        
        return {
            'windows': results,
            'avg_in_sample': round(avg_train, 2),
            'avg_out_sample': round(avg_test, 2),
            'degradation_pct': round(degradation, 1),
            'robust': degradation < 20  # Less than 20% degradation is good
        }
```

**Estimated Time**: 2-3 hours

---

## 📈 Implementation Priority & Timeline

### **Week 1: Phase 4 - Visualizations**
- Day 1-2: Equity Curve Chart (2 hours)
- Day 2: Drawdown Chart (1 hour)
- Day 3: Trade Distribution (1 hour)
- Day 3-4: Monthly Returns Heatmap (2 hours)
- **Total: 6 hours**

### **Week 2: Phase 5 - Portfolio Backtesting**
- Day 1-2: Multi-Stock Portfolio (4 hours)
- Day 3: Correlation Analysis (2 hours)
- **Total: 6 hours**

### **Week 3: Phase 6 - Optimization**
- Day 1-3: Parameter Optimization (6 hours)
- Day 4: Walk-Forward Optimization (3 hours)
- **Total: 9 hours**

### **Week 4: Testing & Documentation**
- Integration testing (4 hours)
- Documentation updates (2 hours)
- Bug fixes (2 hours)
- **Total: 8 hours**

**Grand Total: ~29 hours of development work**

---

## 🎯 Recommended Next Action

**Start with Phase 4.1 - Equity Curve Chart**

This provides:
- Immediate visual value
- Foundation for other charts
- User can see their backtest performance graphically
- Easiest to implement (1-2 hours)

Would you like me to implement this first?

---

## 📝 Files That Will Be Modified/Created

### Modified:
1. `/home/user/webapp/FinBERT_v4.0_Windows11_ENHANCED/models/backtesting/trading_simulator.py`
2. `/home/user/webapp/FinBERT_v4.0_Windows11_ENHANCED/app_finbert_v4_dev.py`
3. `/home/user/webapp/FinBERT_v4.0_Windows11_ENHANCED/templates/finbert_v4_enhanced_ui.html`

### Created:
4. `/home/user/webapp/FinBERT_v4.0_Windows11_ENHANCED/models/backtesting/portfolio_backtest.py`
5. `/home/user/webapp/FinBERT_v4.0_Windows11_ENHANCED/models/backtesting/parameter_optimizer.py`

---

**Ready to proceed with implementation?**
