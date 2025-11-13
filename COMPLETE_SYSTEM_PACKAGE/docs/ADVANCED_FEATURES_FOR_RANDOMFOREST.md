# Advanced Features for RandomForest Stock Prediction

## 📊 Current Features in Stock Tracker (Basic)

```python
# Current implementation uses only:
feature_cols = ['Open', 'High', 'Low', 'Volume', 'returns', 
                'sma_5', 'sma_20', 'rsi', 'macd', 'macd_signal', 
                'bb_high', 'bb_low']  # Only 12 features!
```

## 🚀 Advanced Features That Can Improve Predictions

### 1. **Technical Indicators (Extended)**

```python
# Momentum Indicators
'rsi_14', 'rsi_30'                    # Multiple RSI periods
'stochastic_k', 'stochastic_d'        # Stochastic oscillator
'williams_r'                           # Williams %R
'cci'                                  # Commodity Channel Index
'mfi'                                  # Money Flow Index
'roc'                                  # Rate of Change
'ultimate_oscillator'                  # Ultimate Oscillator

# Trend Indicators
'adx'                                  # Average Directional Index
'adx_pos', 'adx_neg'                  # Directional indicators
'aroon_up', 'aroon_down'              # Aroon indicators
'psar'                                 # Parabolic SAR
'supertrend'                           # Supertrend
'ichimoku_a', 'ichimoku_b'            # Ichimoku Cloud

# Volume Indicators
'obv'                                  # On-Balance Volume
'ad'                                   # Accumulation/Distribution
'cmf'                                  # Chaikin Money Flow
'vwap'                                 # Volume Weighted Average Price
'volume_sma_ratio'                     # Volume/SMA ratio
'volume_trend'                         # Volume trend score

# Volatility Indicators
'atr'                                  # Average True Range
'keltner_high', 'keltner_low'         # Keltner Channels
'donchian_high', 'donchian_low'       # Donchian Channels
'volatility_30d', 'volatility_60d'    # Historical volatility
'garman_klass_volatility'              # Garman-Klass volatility
```

### 2. **Market Microstructure Features**

```python
# Spread and Liquidity
'bid_ask_spread'                      # Bid-ask spread
'spread_percentage'                    # Spread as % of price
'avg_trade_size'                      # Average trade size
'trades_per_minute'                   # Trading frequency
'liquidity_ratio'                     # Volume/Market Cap

# Order Book (if available)
'order_imbalance'                     # Buy orders - Sell orders
'bid_depth'                           # Total bid volume
'ask_depth'                           # Total ask volume
'book_pressure'                       # Bid depth / Ask depth
```

### 3. **Price Action Patterns**

```python
# Candlestick Patterns (as binary features)
'doji'                                # Doji candle
'hammer'                              # Hammer pattern
'shooting_star'                       # Shooting star
'engulfing_bullish'                   # Bullish engulfing
'engulfing_bearish'                   # Bearish engulfing
'morning_star'                        # Morning star pattern
'evening_star'                        # Evening star pattern
'three_white_soldiers'                # Three white soldiers
'three_black_crows'                   # Three black crows

# Support/Resistance
'distance_to_resistance'               # Distance to nearest resistance
'distance_to_support'                  # Distance to nearest support
'pivot_point'                         # Pivot point
'pivot_r1', 'pivot_r2'                # Resistance levels
'pivot_s1', 'pivot_s2'                # Support levels

# Price Patterns
'higher_high'                         # Made higher high
'lower_low'                           # Made lower low
'inside_bar'                          # Inside bar pattern
'outside_bar'                         # Outside bar pattern
```

### 4. **Time-Based Features**

```python
# Calendar Effects
'day_of_week'                        # Monday=0, Friday=4
'day_of_month'                       # 1-31
'week_of_year'                       # 1-52
'month'                               # 1-12
'quarter'                             # 1-4
'is_month_start'                     # First trading day
'is_month_end'                       # Last trading day
'is_quarter_end'                     # Quarter end
'days_to_earnings'                   # Days until earnings
'days_from_earnings'                 # Days since earnings

# Market Hours (for intraday)
'hour_of_day'                        # 9-16 for market hours
'minutes_from_open'                  # Minutes since market open
'minutes_to_close'                   # Minutes until close
'is_first_hour'                      # First trading hour
'is_last_hour'                       # Last trading hour
'is_lunch_hour'                      # Lunch hour (lower volume)
```

### 5. **Fundamental Features**

```python
# Valuation Metrics
'pe_ratio'                           # Price-to-Earnings
'forward_pe'                         # Forward P/E
'peg_ratio'                          # PEG Ratio
'price_to_book'                      # P/B Ratio
'price_to_sales'                     # P/S Ratio
'ev_to_ebitda'                       # EV/EBITDA
'dividend_yield'                     # Dividend Yield

# Financial Health
'current_ratio'                      # Current Assets/Liabilities
'quick_ratio'                        # Quick Ratio
'debt_to_equity'                     # D/E Ratio
'roe'                                # Return on Equity
'roa'                                # Return on Assets
'profit_margin'                      # Net Profit Margin
'operating_margin'                   # Operating Margin

# Growth Metrics
'revenue_growth_yoy'                 # Year-over-year growth
'earnings_growth_yoy'                # Earnings growth
'revenue_growth_qoq'                 # Quarter-over-quarter
'estimate_revision'                  # Analyst estimate changes
```

### 6. **Market Context Features**

```python
# Index/Sector Performance
'sp500_return_1d'                    # S&P 500 daily return
'sp500_return_5d'                    # S&P 500 5-day return
'sector_return_1d'                   # Sector performance
'industry_return_1d'                 # Industry performance
'relative_to_market'                 # Stock return - Market return
'beta_30d'                           # 30-day beta
'correlation_to_spy'                 # Correlation with S&P 500

# Market Regime
'vix_level'                          # Volatility index
'vix_change'                         # VIX daily change
'market_trend'                       # Bull/Bear/Sideways
'market_volatility_regime'           # High/Medium/Low vol

# Breadth Indicators
'advance_decline_ratio'              # Market breadth
'new_highs_lows'                    # 52-week highs - lows
'percent_above_200ma'                # % stocks above 200 MA
```

### 7. **Sentiment Features**

```python
# News Sentiment
'news_sentiment_1d'                  # Daily news sentiment
'news_sentiment_7d'                  # Weekly average
'news_volume'                        # Number of articles
'news_buzz'                          # Relative news volume

# Social Media
'twitter_sentiment'                  # Twitter sentiment score
'twitter_volume'                     # Tweet volume
'stocktwits_sentiment'               # StockTwits bull/bear
'reddit_mentions'                    # WSB mentions
'google_trends'                      # Search interest

# Analyst Sentiment
'analyst_rating'                     # Average analyst rating
'rating_changes'                     # Recent upgrades/downgrades
'price_target_ratio'                 # Price/Average Target
'analyst_consensus'                  # Buy/Hold/Sell consensus
```

### 8. **Options Market Features**

```python
# Options Flow
'put_call_ratio'                     # Put/Call ratio
'implied_volatility'                 # IV from options
'iv_rank'                           # IV percentile
'iv_change'                         # IV daily change
'skew'                              # Options skew
'term_structure'                    # IV term structure

# Options Activity
'unusual_options_activity'          # Unusual volume flag
'call_volume'                       # Call option volume
'put_volume'                        # Put option volume
'open_interest_change'              # OI change
```

### 9. **Macro Economic Features**

```python
# Interest Rates
'fed_funds_rate'                    # Federal funds rate
'10y_treasury_yield'                # 10-year yield
'2y_10y_spread'                     # Yield curve
'real_interest_rate'                # Nominal - Inflation

# Economic Indicators
'gdp_growth'                        # GDP growth rate
'unemployment_rate'                 # Unemployment
'inflation_rate'                    # CPI
'consumer_confidence'               # Consumer confidence
'manufacturing_pmi'                 # PMI index

# Currency/Commodities
'dxy_index'                         # Dollar index
'gold_price_change'                 # Gold price change
'oil_price_change'                  # Oil price change
'btc_price_change'                  # Bitcoin change
```

### 10. **Cross-Asset Correlations**

```python
# Correlation Features
'correlation_bonds'                 # Correlation with bonds
'correlation_gold'                  # Correlation with gold
'correlation_oil'                   # Correlation with oil
'correlation_vix'                   # Correlation with VIX
'correlation_dollar'                # Correlation with DXY

# Lead-Lag Relationships
'futures_basis'                     # Futures - Spot
'etf_premium'                       # ETF premium/discount
'sector_rotation_score'             # Sector rotation signal
```

## 💻 Implementation Example

```python
import pandas as pd
import numpy as np
import yfinance as yf
import ta  # Technical Analysis library
from sklearn.ensemble import RandomForestRegressor

def create_advanced_features(df):
    """Create comprehensive feature set"""
    
    # Price-based features
    df['returns'] = df['Close'].pct_change()
    df['log_returns'] = np.log(df['Close'] / df['Close'].shift(1))
    df['high_low_ratio'] = df['High'] / df['Low']
    df['close_open_ratio'] = df['Close'] / df['Open']
    
    # Volume features
    df['volume_sma_20'] = df['Volume'].rolling(20).mean()
    df['volume_ratio'] = df['Volume'] / df['volume_sma_20']
    df['dollar_volume'] = df['Close'] * df['Volume']
    
    # Volatility features
    df['volatility_20'] = df['returns'].rolling(20).std()
    df['volatility_60'] = df['returns'].rolling(60).std()
    
    # Technical indicators using 'ta' library
    # RSI
    df['rsi_14'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()
    df['rsi_30'] = ta.momentum.RSIIndicator(df['Close'], window=30).rsi()
    
    # MACD
    macd = ta.trend.MACD(df['Close'])
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()
    df['macd_diff'] = macd.macd_diff()
    
    # Bollinger Bands
    bb = ta.volatility.BollingerBands(df['Close'], window=20)
    df['bb_high'] = bb.bollinger_hband()
    df['bb_low'] = bb.bollinger_lband()
    df['bb_width'] = df['bb_high'] - df['bb_low']
    df['bb_position'] = (df['Close'] - df['bb_low']) / (df['bb_high'] - df['bb_low'])
    
    # ATR
    df['atr'] = ta.volatility.AverageTrueRange(df['High'], df['Low'], df['Close']).average_true_range()
    
    # ADX
    adx = ta.trend.ADXIndicator(df['High'], df['Low'], df['Close'])
    df['adx'] = adx.adx()
    df['adx_pos'] = adx.adx_pos()
    df['adx_neg'] = adx.adx_neg()
    
    # Stochastic
    stoch = ta.momentum.StochasticOscillator(df['High'], df['Low'], df['Close'])
    df['stoch_k'] = stoch.stoch()
    df['stoch_d'] = stoch.stoch_signal()
    
    # OBV
    df['obv'] = ta.volume.OnBalanceVolumeIndicator(df['Close'], df['Volume']).on_balance_volume()
    
    # MFI
    df['mfi'] = ta.volume.MFIIndicator(df['High'], df['Low'], df['Close'], df['Volume']).money_flow_index()
    
    # Time features
    df['day_of_week'] = pd.to_datetime(df.index).dayofweek
    df['day_of_month'] = pd.to_datetime(df.index).day
    df['month'] = pd.to_datetime(df.index).month
    df['quarter'] = pd.to_datetime(df.index).quarter
    
    # Price patterns
    df['higher_high'] = (df['High'] > df['High'].shift(1)) & (df['High'].shift(1) > df['High'].shift(2))
    df['lower_low'] = (df['Low'] < df['Low'].shift(1)) & (df['Low'].shift(1) < df['Low'].shift(2))
    
    # Moving averages (multiple periods)
    for period in [5, 10, 20, 50, 100, 200]:
        df[f'sma_{period}'] = df['Close'].rolling(period).mean()
        df[f'sma_{period}_ratio'] = df['Close'] / df[f'sma_{period}']
    
    # Support/Resistance levels
    df['resistance_20d'] = df['High'].rolling(20).max()
    df['support_20d'] = df['Low'].rolling(20).min()
    df['distance_to_resistance'] = (df['resistance_20d'] - df['Close']) / df['Close']
    df['distance_to_support'] = (df['Close'] - df['support_20d']) / df['Close']
    
    # Lag features (previous values)
    for lag in [1, 2, 3, 5, 10]:
        df[f'returns_lag_{lag}'] = df['returns'].shift(lag)
        df[f'volume_lag_{lag}'] = df['Volume'].shift(lag)
    
    # Rolling statistics
    for window in [5, 10, 20, 60]:
        df[f'return_mean_{window}'] = df['returns'].rolling(window).mean()
        df[f'return_std_{window}'] = df['returns'].rolling(window).std()
        df[f'return_skew_{window}'] = df['returns'].rolling(window).skew()
        df[f'return_kurt_{window}'] = df['returns'].rolling(window).kurt()
    
    return df

def add_market_features(df, symbol):
    """Add market-wide features"""
    
    # Download market index
    spy = yf.download('SPY', start=df.index[0], end=df.index[-1])
    spy['spy_returns'] = spy['Close'].pct_change()
    
    # Merge with main dataframe
    df = df.merge(spy[['spy_returns']], left_index=True, right_index=True, how='left')
    
    # Calculate relative performance
    df['relative_to_spy'] = df['returns'] - df['spy_returns']
    
    # Download VIX
    vix = yf.download('^VIX', start=df.index[0], end=df.index[-1])
    df = df.merge(vix[['Close']], left_index=True, right_index=True, how='left', suffixes=('', '_vix'))
    df.rename(columns={'Close_vix': 'vix'}, inplace=True)
    df['vix_change'] = df['vix'].pct_change()
    
    # Market regime
    df['high_volatility'] = (df['vix'] > 20).astype(int)
    df['bull_market'] = (df['spy_returns'].rolling(60).mean() > 0).astype(int)
    
    return df

def add_fundamental_features(df, symbol):
    """Add fundamental data"""
    
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # Add static fundamental features
        df['pe_ratio'] = info.get('trailingPE', np.nan)
        df['forward_pe'] = info.get('forwardPE', np.nan)
        df['peg_ratio'] = info.get('pegRatio', np.nan)
        df['price_to_book'] = info.get('priceToBook', np.nan)
        df['dividend_yield'] = info.get('dividendYield', np.nan)
        df['beta'] = info.get('beta', np.nan)
        df['market_cap'] = info.get('marketCap', np.nan)
        
    except:
        print(f"Could not fetch fundamental data for {symbol}")
    
    return df

# Example usage
def train_advanced_model(symbol='AAPL', days_back=730):
    """Train RandomForest with advanced features"""
    
    # Download data
    df = yf.download(symbol, period=f'{days_back}d')
    
    # Create all features
    df = create_advanced_features(df)
    df = add_market_features(df, symbol)
    df = add_fundamental_features(df, symbol)
    
    # Clean up
    df = df.dropna()
    
    # Select features (can be 100+ features now!)
    feature_cols = [col for col in df.columns if col not in ['Close', 'Adj Close']]
    
    X = df[feature_cols].values
    y = df['Close'].values
    
    # Train model
    model = RandomForestRegressor(
        n_estimators=500,
        max_depth=20,
        min_samples_split=5,
        min_samples_leaf=2,
        max_features='sqrt',  # Important with many features
        random_state=42,
        n_jobs=-1
    )
    
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
    
    model.fit(X_train, y_train)
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': feature_cols,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print(f"Top 20 Most Important Features:")
    print(feature_importance.head(20))
    
    return model, feature_importance
```

## 🎯 Feature Selection Strategy

### 1. **Start with Everything**
- Create 100-200+ features
- Let RandomForest determine importance

### 2. **Feature Importance Analysis**
```python
# After training
importances = pd.DataFrame({
    'feature': feature_names,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

# Keep top 50 features
top_features = importances.head(50)['feature'].tolist()
```

### 3. **Recursive Feature Elimination**
```python
from sklearn.feature_selection import RFE

rfe = RFE(estimator=model, n_features_to_select=50)
rfe.fit(X_train, y_train)
selected_features = [f for f, s in zip(feature_names, rfe.support_) if s]
```

### 4. **Cross-Validation Selection**
```python
from sklearn.model_selection import cross_val_score

scores = {}
for n_features in [20, 30, 50, 70, 100]:
    selector = SelectKBest(f_regression, k=n_features)
    X_selected = selector.fit_transform(X, y)
    cv_scores = cross_val_score(model, X_selected, y, cv=5)
    scores[n_features] = cv_scores.mean()
```

## ⚠️ Important Considerations

### 1. **Feature Engineering > More Data**
- Good features matter more than more training data
- 50 good features > 200 random features

### 2. **Avoid Overfitting**
```python
# With many features, use:
max_features='sqrt'  # or 'log2'
min_samples_leaf=5   # Higher than default
max_depth=15         # Limit depth
```

### 3. **Handle Missing Data**
```python
# Forward fill for time series
df.fillna(method='ffill', inplace=True)

# Or use imputation
from sklearn.impute import SimpleImputer
imputer = SimpleImputer(strategy='median')
```

### 4. **Feature Scaling**
```python
# RandomForest doesn't need scaling, but if mixing models:
from sklearn.preprocessing import RobustScaler
scaler = RobustScaler()  # Better for outliers
```

## ✅ Recommended Feature Set for Stock Tracker V8

Add these features to significantly improve predictions:

1. **Multiple RSI periods** (14, 30, 60)
2. **ATR for volatility**
3. **OBV for volume analysis**
4. **Multiple SMA ratios** (price/SMA)
5. **VIX level** (market fear gauge)
6. **Relative to SPY** (market-adjusted returns)
7. **Day of week** (calendar effects)
8. **Lag features** (returns_lag_1, 2, 3)
9. **Rolling statistics** (mean, std, skew)
10. **Support/Resistance distances**

These alone could improve accuracy by 10-20%!