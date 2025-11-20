# Future Enhancements - Event Risk Guard v1.2+

## 📋 Overview

This document outlines potential future enhancements for Event Risk Guard beyond v1.1. These are **design specifications** for future development, not implemented features.

**Status**: Design Phase  
**Target Version**: v1.2, v2.0, and beyond  
**Priority**: Low (current v1.1 is feature-complete)

---

## 🎨 Enhancement 1: Dashboard Factor View Widget

### Objective
Add interactive factor analysis section to web dashboard for real-time factor exploration.

### Current State
- Factor analysis outputs available as CSV/JSON files
- Manual analysis required (Excel/Python)
- No real-time visualization

### Proposed Implementation

#### A. Dashboard Section Layout

```html
<!-- New section in dashboard.html after Top Opportunities -->
<div class="factor-analysis-section">
    <h2>Factor Analysis</h2>
    
    <!-- Factor Overview Cards -->
    <div class="factor-cards">
        <div class="card">
            <h3>Average Beta XJO</h3>
            <span class="metric">0.95</span>
            <span class="label">Market Sensitivity</span>
        </div>
        <div class="card">
            <h3>Defensive Stocks</h3>
            <span class="metric">12</span>
            <span class="label">Beta < 0.8</span>
        </div>
        <div class="card">
            <h3>Aggressive Stocks</h3>
            <span class="metric">8</span>
            <span class="label">Beta > 1.2</span>
        </div>
    </div>
    
    <!-- Factor Distribution Chart -->
    <div class="factor-chart">
        <h3>Beta Distribution</h3>
        <canvas id="betaDistributionChart"></canvas>
    </div>
    
    <!-- Sector Comparison Table -->
    <div class="sector-table">
        <h3>Sector Comparison</h3>
        <table id="sectorComparisonTable">
            <thead>
                <tr>
                    <th>Sector</th>
                    <th>Avg Opp Score</th>
                    <th>Avg Beta XJO</th>
                    <th>Stock Count</th>
                    <th>Buy Signals</th>
                </tr>
            </thead>
            <tbody id="sectorTableBody"></tbody>
        </table>
    </div>
    
    <!-- Interactive Stock Filter -->
    <div class="stock-filter">
        <h3>Filter by Factors</h3>
        <div class="filter-controls">
            <label>Beta XJO:</label>
            <select id="betaFilter">
                <option value="all">All</option>
                <option value="defensive">&lt; 0.8 (Defensive)</option>
                <option value="moderate">0.8-1.2 (Moderate)</option>
                <option value="aggressive">&gt; 1.2 (Aggressive)</option>
            </select>
            
            <label>Sector:</label>
            <select id="sectorFilter">
                <option value="all">All Sectors</option>
                <!-- Dynamically populated -->
            </select>
            
            <button id="applyFilters">Apply Filters</button>
        </div>
        <div id="filteredStocks"></div>
    </div>
</div>
```

#### B. Backend API Endpoints

Add to `web_ui.py`:

```python
@app.route('/api/factor_analysis')
def get_factor_analysis():
    """Return latest factor analysis data"""
    # Read latest factor_view JSON
    factor_files = sorted(FACTOR_VIEW_DIR.glob('*_factor_view_summary.json'))
    if not factor_files:
        return jsonify({'error': 'No factor analysis available'}), 404
    
    with open(factor_files[-1], 'r') as f:
        data = json.load(f)
    
    return jsonify(data)

@app.route('/api/factor_stocks')
def get_factor_stocks():
    """Return per-stock factor data"""
    factor_files = sorted(FACTOR_VIEW_DIR.glob('*_factor_view_stocks.csv'))
    if not factor_files:
        return jsonify({'error': 'No factor stocks available'}), 404
    
    df = pd.read_csv(factor_files[-1])
    return jsonify(df.to_dict('records'))

@app.route('/api/factor_sectors')
def get_factor_sectors():
    """Return sector summary data"""
    factor_files = sorted(FACTOR_VIEW_DIR.glob('*_factor_view_sector_summary.csv'))
    if not factor_files:
        return jsonify({'error': 'No sector summary available'}), 404
    
    df = pd.read_csv(factor_files[-1])
    return jsonify(df.to_dict('records'))
```

#### C. Frontend JavaScript

Add to `dashboard.js`:

```javascript
// Load factor analysis data
function loadFactorAnalysis() {
    fetch('/api/factor_analysis')
        .then(response => response.json())
        .then(data => {
            updateFactorCards(data);
            updateBetaChart(data);
            updateSectorTable(data);
        })
        .catch(error => console.error('Error loading factor analysis:', error));
}

// Update factor overview cards
function updateFactorCards(data) {
    const avgBetaXJO = data.overall.avg_beta_xjo;
    document.querySelector('.avg-beta-metric').textContent = avgBetaXJO.toFixed(2);
    
    // Count defensive/aggressive stocks
    const defensive = Object.values(data.sectors)
        .filter(s => s.avg_beta_xjo < 0.8).length;
    document.querySelector('.defensive-count').textContent = defensive;
}

// Create beta distribution chart using Chart.js
function updateBetaChart(data) {
    fetch('/api/factor_stocks')
        .then(response => response.json())
        .then(stocks => {
            const betas = stocks.map(s => s.beta_xjo);
            
            const ctx = document.getElementById('betaDistributionChart').getContext('2d');
            new Chart(ctx, {
                type: 'histogram',
                data: {
                    datasets: [{
                        label: 'Beta Distribution',
                        data: betas,
                        backgroundColor: 'rgba(54, 162, 235, 0.5)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    scales: {
                        x: { title: { display: true, text: 'Beta XJO' }},
                        y: { title: { display: true, text: 'Stock Count' }}
                    }
                }
            });
        });
}

// Update sector comparison table
function updateSectorTable(data) {
    const tbody = document.getElementById('sectorTableBody');
    tbody.innerHTML = '';
    
    for (const [sector, info] of Object.entries(data.sectors)) {
        const row = tbody.insertRow();
        row.innerHTML = `
            <td>${sector}</td>
            <td>${info.avg_score.toFixed(1)}</td>
            <td>${info.avg_beta_xjo.toFixed(2)}</td>
            <td>${info.count}</td>
            <td>${info.buy_count}</td>
        `;
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    loadFactorAnalysis();
    setInterval(loadFactorAnalysis, 30000); // Refresh every 30 seconds
});
```

#### D. Styling

Add to `dashboard.css`:

```css
.factor-analysis-section {
    margin: 20px 0;
    padding: 20px;
    background: #f9f9f9;
    border-radius: 8px;
}

.factor-cards {
    display: flex;
    gap: 15px;
    margin-bottom: 20px;
}

.factor-cards .card {
    flex: 1;
    padding: 15px;
    background: white;
    border-radius: 5px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.factor-cards .metric {
    display: block;
    font-size: 2em;
    font-weight: bold;
    color: #2c3e50;
}

.factor-chart {
    margin: 20px 0;
    background: white;
    padding: 15px;
    border-radius: 5px;
}

.sector-table table {
    width: 100%;
    border-collapse: collapse;
}

.sector-table th,
.sector-table td {
    padding: 10px;
    text-align: left;
    border-bottom: 1px solid #ddd;
}

.sector-table th {
    background: #34495e;
    color: white;
}
```

#### E. Implementation Steps

1. Add Chart.js library to dashboard.html
2. Create new API endpoints in web_ui.py
3. Add JavaScript functions to dashboard.js
4. Add CSS styling to dashboard.css
5. Test with real factor analysis data
6. Add error handling for missing data

**Estimated Effort**: 8-12 hours  
**Dependencies**: Chart.js library

---

## 📈 Enhancement 2: Additional Factor Definitions

### Objective
Expand macro factor coverage beyond XJO and Lithium to include gold, oil, interest rates, and currencies.

### Proposed Additional Factors

#### A. Commodity Factors

**Gold**:
```python
FactorDefinition(name="gold", symbol="GLD")  # SPDR Gold Trust ETF
# or
FactorDefinition(name="gold_aud", symbol="GOLD.AX")  # ASX gold ETF
```
**Use case**: Identify gold-sensitive stocks (gold miners, defensive plays)

**Oil**:
```python
FactorDefinition(name="oil", symbol="CL=F")  # WTI Crude Oil Futures
# or
FactorDefinition(name="oil_aud", symbol="OOO.AX")  # BetaShares Crude Oil ETF
```
**Use case**: Identify energy sector exposure

**Iron Ore**:
```python
FactorDefinition(name="iron_ore", symbol="TIOA.AX")  # ASX iron ore index
```
**Use case**: Major export commodity for ASX Materials sector

#### B. Currency Factors

**AUD/USD**:
```python
FactorDefinition(name="aud_usd", symbol="AUDUSD=X")
```
**Use case**: Export-dependent stocks benefit from weaker AUD

**AUD/JPY**:
```python
FactorDefinition(name="aud_jpy", symbol="AUDJPY=X")
```
**Use case**: Correlates with risk-on/risk-off sentiment

**AUD/CNY**:
```python
FactorDefinition(name="aud_cny", symbol="AUDCNY=X")
```
**Use case**: China trade exposure

#### C. Interest Rate Factors

**US 10-Year Treasury**:
```python
FactorDefinition(name="us_10y", symbol="^TNX")
```
**Use case**: Global interest rate sensitivity

**Australian Government Bonds**:
```python
FactorDefinition(name="au_10y", symbol="YTC.AX")  # iShares Australian Bond ETF
```
**Use case**: Domestic interest rate exposure

#### D. Market Breadth Factors

**VIX (Volatility Index)**:
```python
FactorDefinition(name="vix", symbol="^VIX")
```
**Use case**: Fear gauge - inverse correlation with risk assets

**NASDAQ**:
```python
FactorDefinition(name="nasdaq", symbol="^IXIC")
```
**Use case**: Tech sector correlation

#### E. Configuration Example

Create `models/config/custom_factors.json`:

```json
{
  "default_factors": [
    {"name": "xjo", "symbol": "^AXJO"},
    {"name": "lithium", "symbol": "LIT.AX"}
  ],
  "commodity_factors": [
    {"name": "gold", "symbol": "GLD"},
    {"name": "oil", "symbol": "CL=F"},
    {"name": "iron_ore", "symbol": "TIOA.AX"}
  ],
  "currency_factors": [
    {"name": "aud_usd", "symbol": "AUDUSD=X"},
    {"name": "aud_jpy", "symbol": "AUDJPY=X"}
  ],
  "rate_factors": [
    {"name": "us_10y", "symbol": "^TNX"},
    {"name": "au_bonds", "symbol": "YTC.AX"}
  ],
  "enabled_groups": ["default_factors", "commodity_factors"]
}
```

#### F. Dynamic Factor Loading

Modify `macro_beta.py`:

```python
class MacroBetaCalculator:
    def __init__(self, ..., config_file: Optional[Path] = None):
        if config_file:
            self.factors = self._load_factors_from_config(config_file)
        else:
            self.factors = [...]  # Default factors
    
    def _load_factors_from_config(self, config_file: Path) -> List[FactorDefinition]:
        """Load factor definitions from JSON config"""
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        factors = []
        for group in config.get('enabled_groups', []):
            for factor_def in config.get(group, []):
                factors.append(FactorDefinition(
                    name=factor_def['name'],
                    symbol=factor_def['symbol']
                ))
        
        return factors
```

**Estimated Effort**: 4-6 hours  
**Benefits**: Richer factor analysis, more investment strategies

---

## 🔬 Enhancement 3: Advanced Analytics

### Objective
Implement sophisticated statistical analysis including multi-factor regression and rolling betas.

### A. Multi-Factor Regression Model

#### Concept
Instead of individual betas, estimate multiple factors simultaneously:

**Model**: `R_stock = α + β1*R_xjo + β2*R_lithium + β3*R_gold + ε`

#### Implementation

Create `models/screening/multi_factor_model.py`:

```python
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class MultiFactorResult:
    """Results from multi-factor regression"""
    alpha: float  # Intercept (stock-specific return)
    betas: Dict[str, float]  # Factor loadings
    r_squared: float  # Model fit quality
    residual_std: float  # Unexplained variance

class MultiFactorModel:
    """
    Multi-factor regression model
    
    Estimates simultaneous exposure to multiple factors:
    R_stock = α + Σ(βi * R_factori) + ε
    """
    
    def __init__(self, lookback_days: int = 90):
        self.lookback_days = lookback_days
    
    def fit_model(
        self,
        stock_returns: pd.Series,
        factor_returns: Dict[str, pd.Series]
    ) -> MultiFactorResult:
        """
        Fit multi-factor regression model
        
        Args:
            stock_returns: Daily returns for stock
            factor_returns: Dict of factor name -> daily returns
        
        Returns:
            MultiFactorResult with alpha, betas, and fit statistics
        """
        # Align all data on common dates
        data = pd.DataFrame({
            'stock': stock_returns,
            **factor_returns
        }).dropna()
        
        # Separate dependent and independent variables
        y = data['stock'].values
        X = data.drop('stock', axis=1).values
        factor_names = list(factor_returns.keys())
        
        # Fit regression
        model = LinearRegression()
        model.fit(X, y)
        
        # Calculate R-squared
        y_pred = model.predict(X)
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot)
        
        # Calculate residual standard deviation
        residuals = y - y_pred
        residual_std = np.std(residuals)
        
        # Extract betas
        betas = {name: coef for name, coef in zip(factor_names, model.coef_)}
        
        return MultiFactorResult(
            alpha=model.intercept_,
            betas=betas,
            r_squared=r_squared,
            residual_std=residual_std
        )
    
    def interpret_alpha(self, alpha: float) -> str:
        """Interpret alpha (stock-specific return)"""
        if alpha > 0.001:  # > 0.1% daily
            return "Positive alpha (outperforms factors)"
        elif alpha < -0.001:
            return "Negative alpha (underperforms factors)"
        else:
            return "Neutral alpha (explained by factors)"
    
    def dominant_factor(self, betas: Dict[str, float]) -> str:
        """Identify which factor has strongest influence"""
        abs_betas = {k: abs(v) for k, v in betas.items()}
        dominant = max(abs_betas, key=abs_betas.get)
        return dominant
```

#### Usage Example

```python
# Fit multi-factor model for CBA.AX
model = MultiFactorModel()

stock_returns = get_stock_returns('CBA.AX', days=90)
factor_returns = {
    'xjo': get_factor_returns('^AXJO', days=90),
    'lithium': get_factor_returns('LIT.AX', days=90),
    'gold': get_factor_returns('GLD', days=90)
}

result = model.fit_model(stock_returns, factor_returns)

print(f"Alpha: {result.alpha:.4f}")
print(f"Betas: {result.betas}")
print(f"R-squared: {result.r_squared:.3f}")
print(f"Dominant factor: {model.dominant_factor(result.betas)}")
```

**Benefits**:
- More accurate factor attribution
- Identify stock-specific alpha
- Understand factor interactions

---

### B. Rolling Beta Calculation

#### Concept
Calculate betas over sliding time windows to detect changing market sensitivity.

#### Implementation

Add to `macro_beta.py`:

```python
class MacroBetaCalculator:
    # ... existing code ...
    
    def compute_rolling_betas(
        self,
        symbol: str,
        factor_symbol: str,
        window_days: int = 60,
        step_days: int = 5
    ) -> pd.DataFrame:
        """
        Calculate rolling betas over time
        
        Args:
            symbol: Stock symbol
            factor_symbol: Factor symbol (e.g., '^AXJO')
            window_days: Rolling window size
            step_days: Step size between windows
        
        Returns:
            DataFrame with columns: date, beta, std_error
        """
        # Download extended historical data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=self.lookback_days * 2)
        
        stock_data = yf.download(symbol, start=start_date, end=end_date)
        factor_data = yf.download(factor_symbol, start=start_date, end=end_date)
        
        # Calculate returns
        stock_returns = stock_data['Close'].pct_change().dropna()
        factor_returns = factor_data['Close'].pct_change().dropna()
        
        # Calculate rolling betas
        results = []
        
        for i in range(0, len(stock_returns) - window_days, step_days):
            window_stock = stock_returns.iloc[i:i+window_days]
            window_factor = factor_returns.iloc[i:i+window_days]
            
            # Align on common dates
            joined = pd.concat([window_stock, window_factor], axis=1, join='inner')
            if len(joined) < self.min_obs:
                continue
            
            # Calculate beta
            cov = np.cov(joined.iloc[:, 0], joined.iloc[:, 1])[0, 1]
            var = np.var(joined.iloc[:, 1])
            beta = cov / var
            
            # Calculate standard error
            residuals = joined.iloc[:, 0] - (beta * joined.iloc[:, 1])
            std_error = np.std(residuals) / np.sqrt(len(joined))
            
            results.append({
                'date': window_stock.index[i + window_days],
                'beta': beta,
                'std_error': std_error
            })
        
        return pd.DataFrame(results)
    
    def beta_trend(self, rolling_betas: pd.DataFrame) -> str:
        """Analyze beta trend over time"""
        if len(rolling_betas) < 2:
            return "Insufficient data"
        
        # Linear regression on beta values
        x = np.arange(len(rolling_betas))
        y = rolling_betas['beta'].values
        
        slope = np.polyfit(x, y, 1)[0]
        
        if slope > 0.01:
            return "Increasing sensitivity"
        elif slope < -0.01:
            return "Decreasing sensitivity"
        else:
            return "Stable sensitivity"
```

#### Visualization

```python
import matplotlib.pyplot as plt

# Calculate rolling betas
rolling_betas = calculator.compute_rolling_betas('CBA.AX', '^AXJO')

# Plot
plt.figure(figsize=(12, 6))
plt.plot(rolling_betas['date'], rolling_betas['beta'], label='Beta XJO')
plt.fill_between(
    rolling_betas['date'],
    rolling_betas['beta'] - rolling_betas['std_error'],
    rolling_betas['beta'] + rolling_betas['std_error'],
    alpha=0.3,
    label='Confidence interval'
)
plt.axhline(y=1.0, color='r', linestyle='--', label='Market beta')
plt.xlabel('Date')
plt.ylabel('Beta')
plt.title('CBA.AX Rolling Beta vs ASX 200')
plt.legend()
plt.grid(True)
plt.savefig('reports/factor_view/rolling_beta_CBA.png')
```

**Benefits**:
- Detect regime changes
- Time-varying risk assessment
- More adaptive portfolio management

**Estimated Effort**: 12-16 hours  
**Dependencies**: scikit-learn, matplotlib

---

## 🤖 Enhancement 4: Machine Learning Integration

### Objective
Use factor scores as inputs to LSTM models and implement factor-based model training.

### A. Factor-Enhanced LSTM

#### Concept
Current LSTM uses price/volume data. Add factor scores as additional features.

#### Architecture

```
Input Layer:
  - Price features (60 days × 5 features = 300 inputs)
    - Open, High, Low, Close, Volume
  - Factor features (60 days × 8 factors = 480 inputs)
    - prediction_confidence, technical_strength, spi_alignment
    - liquidity, volatility, sector_momentum
    - beta_xjo, beta_lithium
  
  Total: 780 input features

Hidden Layers:
  - LSTM(128) with dropout(0.2)
  - LSTM(64) with dropout(0.2)
  - Dense(32) with ReLU
  
Output Layer:
  - Dense(3) with softmax (BUY/HOLD/SELL)
```

#### Implementation

Create `models/train_factor_lstm.py`:

```python
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import pandas as pd
import numpy as np

class FactorEnhancedLSTM:
    """
    LSTM model that incorporates factor scores
    """
    
    def __init__(self, sequence_length: int = 60):
        self.sequence_length = sequence_length
        self.model = None
    
    def build_model(
        self,
        price_features: int = 5,
        factor_features: int = 8
    ):
        """Build factor-enhanced LSTM model"""
        
        # Input layers
        price_input = layers.Input(
            shape=(self.sequence_length, price_features),
            name='price_input'
        )
        factor_input = layers.Input(
            shape=(self.sequence_length, factor_features),
            name='factor_input'
        )
        
        # Price branch - LSTM
        price_lstm = layers.LSTM(128, return_sequences=True)(price_input)
        price_lstm = layers.Dropout(0.2)(price_lstm)
        price_lstm = layers.LSTM(64)(price_lstm)
        price_lstm = layers.Dropout(0.2)(price_lstm)
        
        # Factor branch - Dense
        factor_flat = layers.Flatten()(factor_input)
        factor_dense = layers.Dense(64, activation='relu')(factor_flat)
        factor_dense = layers.Dropout(0.2)(factor_dense)
        
        # Combine branches
        combined = layers.concatenate([price_lstm, factor_dense])
        
        # Final layers
        dense = layers.Dense(32, activation='relu')(combined)
        output = layers.Dense(3, activation='softmax', name='output')(dense)
        
        # Create model
        self.model = keras.Model(
            inputs=[price_input, factor_input],
            outputs=output
        )
        
        # Compile
        self.model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return self.model
    
    def prepare_sequences(
        self,
        price_data: pd.DataFrame,
        factor_data: pd.DataFrame,
        labels: np.ndarray
    ):
        """Prepare training sequences with both price and factor data"""
        
        price_sequences = []
        factor_sequences = []
        sequence_labels = []
        
        for i in range(len(price_data) - self.sequence_length):
            price_seq = price_data.iloc[i:i+self.sequence_length].values
            factor_seq = factor_data.iloc[i:i+self.sequence_length].values
            label = labels[i + self.sequence_length]
            
            price_sequences.append(price_seq)
            factor_sequences.append(factor_seq)
            sequence_labels.append(label)
        
        return (
            np.array(price_sequences),
            np.array(factor_sequences),
            np.array(sequence_labels)
        )
    
    def train(
        self,
        price_sequences: np.ndarray,
        factor_sequences: np.ndarray,
        labels: np.ndarray,
        epochs: int = 50,
        batch_size: int = 32
    ):
        """Train the model"""
        
        history = self.model.fit(
            [price_sequences, factor_sequences],
            labels,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=0.2,
            verbose=1
        )
        
        return history
```

#### Usage

```python
# Build model
model = FactorEnhancedLSTM(sequence_length=60)
model.build_model()

# Prepare data
price_data = get_price_history('CBA.AX', days=500)
factor_data = get_factor_history('CBA.AX', days=500)
labels = create_labels(price_data)

price_seq, factor_seq, label_seq = model.prepare_sequences(
    price_data, factor_data, labels
)

# Train
history = model.train(price_seq, factor_seq, label_seq, epochs=50)

# Save model
model.model.save('models/lstm_models/CBA_AX_factor_enhanced.keras')
```

**Benefits**:
- Richer input features
- Potentially higher accuracy
- Better risk-adjusted predictions

---

### B. Factor-Based Model Selection

#### Concept
Train separate models for different factor regimes (high beta vs low beta, defensive vs aggressive).

#### Implementation

```python
class RegimeBasedModelSelector:
    """
    Select LSTM model based on current factor regime
    """
    
    def __init__(self):
        self.models = {
            'high_beta': None,  # For aggressive stocks (beta > 1.2)
            'medium_beta': None,  # For moderate stocks (0.8 < beta < 1.2)
            'low_beta': None     # For defensive stocks (beta < 0.8)
        }
    
    def classify_regime(self, beta_xjo: float) -> str:
        """Classify stock into regime based on beta"""
        if beta_xjo > 1.2:
            return 'high_beta'
        elif beta_xjo < 0.8:
            return 'low_beta'
        else:
            return 'medium_beta'
    
    def select_model(self, stock: Dict) -> keras.Model:
        """Select appropriate model for stock"""
        regime = self.classify_regime(stock.get('beta_xjo', 1.0))
        return self.models.get(regime)
    
    def train_regime_models(self, stocks_by_regime: Dict[str, List]):
        """Train separate models for each regime"""
        for regime, stocks in stocks_by_regime.items():
            print(f"Training model for {regime} regime ({len(stocks)} stocks)...")
            
            # Combine data from all stocks in regime
            combined_data = aggregate_stock_data(stocks)
            
            # Train model
            model = FactorEnhancedLSTM()
            model.build_model()
            # ... training code ...
            
            self.models[regime] = model.model
```

**Benefits**:
- Specialized models for different market conditions
- Better performance in specific regimes
- More nuanced predictions

**Estimated Effort**: 20-30 hours  
**Dependencies**: TensorFlow 2.0+, significant training data

---

## 🎯 Summary

| Enhancement | Priority | Effort | Benefit |
|-------------|----------|--------|---------|
| **Dashboard Widget** | Medium | 8-12 hrs | Better UX, real-time visualization |
| **Additional Factors** | Low | 4-6 hrs | Richer analysis, more strategies |
| **Advanced Analytics** | Low | 12-16 hrs | Deeper insights, time-varying risk |
| **ML Integration** | Low | 20-30 hrs | Potentially higher prediction accuracy |

**Total Effort**: 44-64 hours of development

**Recommendation**: 
- Implement Dashboard Widget first (highest user value)
- Add additional factors as needed by users
- Advanced analytics and ML integration are research-level enhancements for v2.0+

---

## 📝 Notes

These enhancements are **design specifications** only. Current v1.1 is feature-complete and production-ready. Future versions will be driven by user feedback and feature requests.

For questions or suggestions, see main documentation in `README.md` and `CHANGELOG.md`.
