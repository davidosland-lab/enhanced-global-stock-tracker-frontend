#!/usr/bin/env python3
"""
Advanced ML Portfolio System with Multiple Models and Optimization
Integrates: XGBoost, LSTM, Transformer, Portfolio Optimization, Risk Management
Based on professional finance ML techniques
"""

import os
import sys
import time
import json
import warnings
import traceback
import threading
from datetime import datetime, timedelta
from functools import lru_cache
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import yfinance as yf

# Suppress warnings
warnings.filterwarnings('ignore')
os.environ['FLASK_SKIP_DOTENV'] = '1'

# Import ML components
try:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import TimeSeriesSplit, train_test_split
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import accuracy_score, classification_report
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("WARNING: scikit-learn not available")

try:
    from xgboost import XGBClassifier, XGBRegressor
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    print("WARNING: XGBoost not available")

try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("WARNING: PyTorch not available")

try:
    import cvxpy as cp
    CVXPY_AVAILABLE = True
except ImportError:
    CVXPY_AVAILABLE = False
    print("WARNING: cvxpy not available")

print("=" * 80)
print("ADVANCED ML PORTFOLIO SYSTEM")
print("=" * 80)
print(f"✓ ML Available: {ML_AVAILABLE}")
print(f"✓ XGBoost Available: {XGBOOST_AVAILABLE}")
print(f"✓ PyTorch Available: {TORCH_AVAILABLE}")
print(f"✓ Portfolio Optimization Available: {CVXPY_AVAILABLE}")
print("=" * 80)

app = Flask(__name__)
CORS(app)

# Configuration
ALPHA_VANTAGE_KEY = "68ZFANK047DL0KSR"
YAHOO_REQUEST_DELAY = 3

# Rate limiting
last_yahoo_request = 0
request_lock = threading.Lock()

# Australian stocks
AUSTRALIAN_STOCKS = {
    'CBA', 'BHP', 'CSL', 'NAB', 'WBC', 'ANZ', 'WES', 'MQG', 
    'WOW', 'TLS', 'RIO', 'FMG', 'WDS', 'ALL', 'REA', 'COL'
}

class AdvancedTechnicalIndicators:
    """Extended technical indicators from the ChatGPT conversation"""
    
    @staticmethod
    def rsi(series: pd.Series, period: int = 14) -> pd.Series:
        """RSI with Wilder smoothing"""
        delta = series.diff()
        up = delta.clip(lower=0).ewm(alpha=1/period, adjust=False).mean()
        down = (-delta.clip(upper=0)).ewm(alpha=1/period, adjust=False).mean()
        rs = up / (down.replace(0, np.nan))
        out = 100 - (100 / (1 + rs))
        return out.fillna(50)
    
    @staticmethod
    def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Average True Range for volatility"""
        high = df['High']
        low = df['Low']
        close = df['Close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.ewm(alpha=1/period, adjust=False).mean()
        return atr
    
    @staticmethod
    def vwap(df: pd.DataFrame) -> pd.Series:
        """Volume Weighted Average Price"""
        typical_price = (df['High'] + df['Low'] + df['Close']) / 3
        vwap = (typical_price * df['Volume']).cumsum() / df['Volume'].cumsum()
        return vwap
    
    @staticmethod
    def obv(df: pd.DataFrame) -> pd.Series:
        """On-Balance Volume"""
        obv = (df['Volume'] * df['Close'].diff().apply(np.sign)).cumsum()
        return obv
    
    @staticmethod
    def stochastic(df: pd.DataFrame, k_period=14, d_period=3) -> dict:
        """Stochastic Oscillator"""
        low_min = df['Low'].rolling(window=k_period).min()
        high_max = df['High'].rolling(window=k_period).max()
        
        k_percent = 100 * ((df['Close'] - low_min) / (high_max - low_min))
        d_percent = k_percent.rolling(window=d_period).mean()
        
        return {
            'K': k_percent,
            'D': d_percent
        }
    
    @staticmethod
    def calculate_all_advanced(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all advanced features for ML"""
        features = pd.DataFrame(index=df.index)
        
        # Returns and volatility
        features['ret_1d'] = df['Close'].pct_change()
        features['ret_5d'] = df['Close'].pct_change(5)
        features['ret_20d'] = df['Close'].pct_change(20)
        features['vol_10'] = features['ret_1d'].rolling(10).std()
        features['vol_20'] = features['ret_1d'].rolling(20).std()
        
        # Moving averages and ratios
        features['sma_10'] = df['Close'].rolling(10).mean()
        features['sma_20'] = df['Close'].rolling(20).mean()
        features['sma_50'] = df['Close'].rolling(50).mean()
        features['ema_10'] = df['Close'].ewm(span=10, adjust=False).mean()
        features['ema_20'] = df['Close'].ewm(span=20, adjust=False).mean()
        
        features['px_sma10'] = df['Close'] / features['sma_10'] - 1
        features['px_sma20'] = df['Close'] / features['sma_20'] - 1
        features['px_sma50'] = df['Close'] / features['sma_50'] - 1
        
        # Momentum
        features['mom_10'] = df['Close'].pct_change(10)
        features['mom_20'] = df['Close'].pct_change(20)
        
        # Technical indicators
        features['rsi_14'] = AdvancedTechnicalIndicators.rsi(df['Close'], 14)
        features['atr_14'] = AdvancedTechnicalIndicators.atr(df, 14)
        
        # MACD
        ema_12 = df['Close'].ewm(span=12, adjust=False).mean()
        ema_26 = df['Close'].ewm(span=26, adjust=False).mean()
        features['macd'] = ema_12 - ema_26
        features['macd_signal'] = features['macd'].ewm(span=9, adjust=False).mean()
        features['macd_hist'] = features['macd'] - features['macd_signal']
        
        # Bollinger Bands
        bb_sma = df['Close'].rolling(20).mean()
        bb_std = df['Close'].rolling(20).std()
        features['bb_upper'] = bb_sma + (bb_std * 2)
        features['bb_lower'] = bb_sma - (bb_std * 2)
        features['bb_position'] = (df['Close'] - features['bb_lower']) / (features['bb_upper'] - features['bb_lower'])
        
        # Volume features
        if 'Volume' in df.columns:
            features['volume_ratio'] = df['Volume'] / df['Volume'].rolling(20).mean()
            features['volume_change'] = df['Volume'].pct_change()
            features['obv'] = AdvancedTechnicalIndicators.obv(df)
            features['vwap'] = AdvancedTechnicalIndicators.vwap(df)
        
        # Stochastic
        stoch = AdvancedTechnicalIndicators.stochastic(df)
        features['stoch_k'] = stoch['K']
        features['stoch_d'] = stoch['D']
        
        return features

# PyTorch Models (if available)
if TORCH_AVAILABLE:
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    class LSTMPredictor(nn.Module):
        """LSTM for time series prediction"""
        def __init__(self, n_features, hidden_size=64, num_layers=2, dropout=0.1):
            super().__init__()
            self.lstm = nn.LSTM(
                input_size=n_features,
                hidden_size=hidden_size,
                num_layers=num_layers,
                batch_first=True,
                dropout=dropout if num_layers > 1 else 0
            )
            self.fc = nn.Sequential(
                nn.Linear(hidden_size, 32),
                nn.ReLU(),
                nn.Dropout(dropout),
                nn.Linear(32, 1)
            )
        
        def forward(self, x):
            _, (h, _) = self.lstm(x)
            out = self.fc(h[-1])
            return out
    
    class TransformerPredictor(nn.Module):
        """Transformer for time series prediction"""
        def __init__(self, n_features, d_model=64, nhead=4, num_layers=2, dropout=0.1):
            super().__init__()
            self.proj = nn.Linear(n_features, d_model)
            self.pos_encoding = PositionalEncoding(d_model)
            
            encoder_layer = nn.TransformerEncoderLayer(
                d_model=d_model,
                nhead=nhead,
                dim_feedforward=128,
                dropout=dropout,
                batch_first=True
            )
            self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
            
            self.fc = nn.Sequential(
                nn.Linear(d_model, 32),
                nn.ReLU(),
                nn.Dropout(dropout),
                nn.Linear(32, 1)
            )
        
        def forward(self, x):
            x = self.proj(x)
            x = self.pos_encoding(x)
            x = self.encoder(x)
            # Global average pooling
            x = x.mean(dim=1)
            out = self.fc(x)
            return out
    
    class PositionalEncoding(nn.Module):
        def __init__(self, d_model, max_len=512):
            super().__init__()
            pe = torch.zeros(max_len, d_model)
            position = torch.arange(0, max_len).unsqueeze(1).float()
            
            div_term = torch.exp(torch.arange(0, d_model, 2).float() * 
                                -(np.log(10000.0) / d_model))
            
            pe[:, 0::2] = torch.sin(position * div_term)
            pe[:, 1::2] = torch.cos(position * div_term)
            
            self.register_buffer('pe', pe.unsqueeze(0))
        
        def forward(self, x):
            return x + self.pe[:, :x.size(1)]

class PortfolioOptimizer:
    """Advanced portfolio optimization techniques"""
    
    @staticmethod
    def mean_variance(returns, target_return=None, max_weight=0.4):
        """Markowitz mean-variance optimization"""
        if not CVXPY_AVAILABLE:
            return None
        
        n_assets = returns.shape[1]
        mu = returns.mean()
        sigma = returns.cov()
        
        w = cp.Variable(n_assets)
        
        # Objective: minimize portfolio variance
        portfolio_variance = cp.quad_form(w, sigma.values)
        
        # Constraints
        constraints = [
            cp.sum(w) == 1,  # Weights sum to 1
            w >= 0,  # Long only
            w <= max_weight  # Maximum position size
        ]
        
        if target_return is not None:
            constraints.append(mu.values @ w >= target_return)
        
        problem = cp.Problem(cp.Minimize(portfolio_variance), constraints)
        problem.solve()
        
        if problem.status == 'optimal':
            return pd.Series(w.value, index=returns.columns)
        return None
    
    @staticmethod
    def risk_parity(returns):
        """Risk Parity portfolio - equal risk contribution"""
        n_assets = returns.shape[1]
        cov = returns.cov()
        
        def risk_contribution(w, cov):
            portfolio_vol = np.sqrt(w @ cov @ w)
            marginal_contrib = cov @ w
            contrib = w * marginal_contrib / portfolio_vol
            return contrib
        
        def objective(w):
            rc = risk_contribution(w, cov.values)
            # Minimize variance of risk contributions
            return np.var(rc)
        
        from scipy.optimize import minimize
        
        w0 = np.ones(n_assets) / n_assets
        bounds = [(0.01, 0.5) for _ in range(n_assets)]
        constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
        
        result = minimize(objective, w0, method='SLSQP', 
                         bounds=bounds, constraints=constraints)
        
        if result.success:
            return pd.Series(result.x, index=returns.columns)
        return None
    
    @staticmethod
    def hierarchical_risk_parity(returns):
        """Hierarchical Risk Parity (HRP) - ML-based portfolio optimization"""
        from scipy.cluster.hierarchy import linkage, dendrogram, cut_tree
        from scipy.spatial.distance import squareform
        
        # Calculate correlation and distance matrix
        corr = returns.corr()
        dist = np.sqrt(0.5 * (1 - corr))
        
        # Hierarchical clustering
        condensed_dist = squareform(dist)
        Z = linkage(condensed_dist, 'single')
        
        # Get sorted list of assets
        def get_quasi_diag(link):
            link = link.astype(int)
            sort_ix = pd.Series([link[-1, 0], link[-1, 1]])
            num_items = link[-1, 3]
            
            while sort_ix.max() >= num_items:
                sort_ix.index = range(0, sort_ix.shape[0] * 2, 2)
                df0 = sort_ix[sort_ix >= num_items]
                i = df0.index
                j = df0.values - num_items
                sort_ix[i] = link[j, 0]
                df0 = pd.Series(link[j, 1], index=i + 1)
                sort_ix = pd.concat([sort_ix, df0])
                sort_ix = sort_ix.sort_index()
                sort_ix.index = range(sort_ix.shape[0])
            
            return sort_ix.tolist()
        
        sorted_idx = get_quasi_diag(Z)
        
        # Recursive bisection
        def rec_bisect(cov, sorted_ix):
            w = pd.Series(1, index=sorted_ix)
            cluster_items = [sorted_ix]
            
            while len(cluster_items) > 0:
                cluster_items = [i[j:k] for i in cluster_items 
                               for j, k in ((0, len(i) // 2), (len(i) // 2, len(i))) 
                               if len(i) > 1]
                
                for i in range(0, len(cluster_items), 2):
                    item0 = cluster_items[i]
                    item1 = cluster_items[i + 1] if i + 1 < len(cluster_items) else []
                    
                    if len(item1) > 0:
                        cluster0_var = cov.loc[item0, item0].values.flatten()
                        cluster1_var = cov.loc[item1, item1].values.flatten()
                        
                        alpha = 1 - cluster0_var.sum() / (cluster0_var.sum() + cluster1_var.sum())
                        
                        w[item0] *= alpha
                        w[item1] *= 1 - alpha
            
            return w
        
        cov = returns.cov()
        weights = rec_bisect(cov, sorted_idx)
        
        # Normalize
        weights = weights / weights.sum()
        
        return weights.reindex(returns.columns)
    
    @staticmethod
    def kelly_criterion(win_prob, win_return, loss_return):
        """Kelly Criterion for optimal bet sizing"""
        # f* = (p * b - q) / b
        # where p = win prob, q = 1-p, b = win/loss ratio
        q = 1 - win_prob
        b = abs(win_return / loss_return)
        
        f_star = (win_prob * b - q) / b
        
        # Apply Kelly fraction (usually 0.25 for safety)
        kelly_fraction = 0.25
        
        return max(0, min(f_star * kelly_fraction, 1))

class RiskManager:
    """Advanced risk management metrics"""
    
    @staticmethod
    def calculate_var(returns, confidence=0.95):
        """Value at Risk"""
        return np.percentile(returns, (1 - confidence) * 100)
    
    @staticmethod
    def calculate_cvar(returns, confidence=0.95):
        """Conditional Value at Risk (Expected Shortfall)"""
        var = RiskManager.calculate_var(returns, confidence)
        return returns[returns <= var].mean()
    
    @staticmethod
    def max_drawdown(cumulative_returns):
        """Maximum Drawdown calculation"""
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        return drawdown.min()
    
    @staticmethod
    def sharpe_ratio(returns, risk_free_rate=0.02, periods_per_year=252):
        """Sharpe Ratio calculation"""
        excess_returns = returns - risk_free_rate / periods_per_year
        return np.sqrt(periods_per_year) * excess_returns.mean() / returns.std()
    
    @staticmethod
    def sortino_ratio(returns, risk_free_rate=0.02, periods_per_year=252):
        """Sortino Ratio (only downside volatility)"""
        excess_returns = returns - risk_free_rate / periods_per_year
        downside_returns = returns[returns < 0]
        downside_std = downside_returns.std()
        
        if downside_std == 0:
            return np.inf if excess_returns.mean() > 0 else -np.inf
        
        return np.sqrt(periods_per_year) * excess_returns.mean() / downside_std
    
    @staticmethod
    def calmar_ratio(returns, periods_per_year=252):
        """Calmar Ratio (CAGR / Max Drawdown)"""
        cumulative = (1 + returns).cumprod()
        cagr = (cumulative.iloc[-1] ** (periods_per_year / len(returns))) - 1
        mdd = abs(RiskManager.max_drawdown(cumulative))
        
        if mdd == 0:
            return np.inf if cagr > 0 else -np.inf
        
        return cagr / mdd

class MultiModelPredictor:
    """Ensemble of multiple ML models"""
    
    def __init__(self):
        self.models = {}
        self.scaler = StandardScaler()
        self.sequence_length = 30
    
    def prepare_features(self, df, include_advanced=True):
        """Prepare features for ML models"""
        if include_advanced:
            features = AdvancedTechnicalIndicators.calculate_all_advanced(df)
        else:
            # Basic features only
            features = pd.DataFrame(index=df.index)
            features['returns'] = df['Close'].pct_change()
            features['sma_20'] = df['Close'].rolling(20).mean()
            features['rsi'] = AdvancedTechnicalIndicators.rsi(df['Close'])
        
        # Fill NaN values
        features = features.fillna(method='ffill').fillna(0)
        
        return features
    
    def train_xgboost(self, X, y):
        """Train XGBoost model with walk-forward validation"""
        if not XGBOOST_AVAILABLE:
            return None
        
        tscv = TimeSeriesSplit(n_splits=5)
        oof_predictions = np.zeros(len(y))
        
        for train_idx, val_idx in tscv.split(X):
            X_train, X_val = X[train_idx], X[val_idx]
            y_train, y_val = y[train_idx], y[val_idx]
            
            model = XGBClassifier(
                n_estimators=400,
                max_depth=4,
                learning_rate=0.05,
                subsample=0.9,
                colsample_bytree=0.9,
                reg_lambda=1.0,
                objective='binary:logistic',
                eval_metric='logloss',
                random_state=42
            )
            
            model.fit(X_train, y_train, 
                     eval_set=[(X_val, y_val)],
                     early_stopping_rounds=50,
                     verbose=False)
            
            oof_predictions[val_idx] = model.predict_proba(X_val)[:, 1]
        
        # Train final model on all data
        final_model = XGBClassifier(
            n_estimators=400,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.9,
            reg_lambda=1.0,
            random_state=42
        )
        final_model.fit(X, y)
        
        self.models['xgboost'] = final_model
        
        return oof_predictions
    
    def train_lstm(self, X_sequences, y):
        """Train LSTM model"""
        if not TORCH_AVAILABLE:
            return None
        
        # Convert to tensors
        X_tensor = torch.FloatTensor(X_sequences)
        y_tensor = torch.FloatTensor(y)
        
        # Create model
        n_features = X_sequences.shape[2]
        model = LSTMPredictor(n_features).to(device)
        
        # Training settings
        criterion = nn.BCEWithLogitsLoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
        
        # Create data loader
        dataset = torch.utils.data.TensorDataset(X_tensor, y_tensor)
        loader = torch.utils.data.DataLoader(dataset, batch_size=32, shuffle=False)
        
        # Train
        model.train()
        for epoch in range(20):
            for batch_x, batch_y in loader:
                batch_x = batch_x.to(device)
                batch_y = batch_y.to(device)
                
                optimizer.zero_grad()
                outputs = model(batch_x).squeeze()
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()
        
        model.eval()
        self.models['lstm'] = model
        
        # Get predictions
        with torch.no_grad():
            predictions = torch.sigmoid(model(X_tensor.to(device))).cpu().numpy().squeeze()
        
        return predictions
    
    def train_ensemble(self, df, target_column='target'):
        """Train ensemble of models"""
        # Prepare features
        features = self.prepare_features(df)
        
        # Create target (next day up/down)
        y = (df['Close'].pct_change().shift(-1) > 0).astype(int)
        
        # Align and clean
        valid_idx = ~(features.isna().any(axis=1) | y.isna())
        features = features[valid_idx]
        y = y[valid_idx].values
        
        # Scale features
        X_scaled = self.scaler.fit_transform(features)
        
        predictions = {}
        
        # Train XGBoost
        if XGBOOST_AVAILABLE:
            print("Training XGBoost...")
            xgb_preds = self.train_xgboost(X_scaled, y)
            predictions['xgboost'] = xgb_preds
        
        # Prepare sequences for LSTM/Transformer
        if TORCH_AVAILABLE and len(X_scaled) > self.sequence_length:
            print("Training LSTM...")
            X_sequences = []
            y_sequences = []
            
            for i in range(self.sequence_length, len(X_scaled)):
                X_sequences.append(X_scaled[i-self.sequence_length:i])
                y_sequences.append(y[i])
            
            X_sequences = np.array(X_sequences)
            y_sequences = np.array(y_sequences)
            
            lstm_preds = self.train_lstm(X_sequences, y_sequences)
            
            # Pad predictions to match original length
            lstm_preds_full = np.full(len(y), np.nan)
            lstm_preds_full[self.sequence_length:] = lstm_preds
            predictions['lstm'] = lstm_preds_full
        
        # Ensemble predictions (simple average)
        valid_predictions = [p for p in predictions.values() if p is not None]
        if valid_predictions:
            ensemble_preds = np.nanmean(valid_predictions, axis=0)
            predictions['ensemble'] = ensemble_preds
        
        return predictions
    
    def predict(self, features, model_type='ensemble'):
        """Make predictions with specified model"""
        if model_type not in self.models:
            return None
        
        model = self.models[model_type]
        
        if model_type == 'xgboost':
            X_scaled = self.scaler.transform(features.values.reshape(1, -1))
            return model.predict_proba(X_scaled)[0, 1]
        
        elif model_type == 'lstm' and TORCH_AVAILABLE:
            # Need sequence of features
            # This is simplified - in production you'd maintain a rolling window
            return 0.5  # Placeholder
        
        return None

class Backtester:
    """Walk-forward backtesting system"""
    
    @staticmethod
    def walk_forward_backtest(df, predictions, transaction_cost_bps=2):
        """Perform walk-forward backtest"""
        results = {}
        
        # Get returns
        returns = df['Close'].pct_change()
        
        # Create positions (1 = long, 0 = flat)
        positions = (predictions >= 0.5).astype(int)
        
        # Calculate turnover
        turnover = np.abs(np.diff(positions, prepend=positions[0]))
        
        # Transaction costs
        costs = turnover * (transaction_cost_bps / 10000)
        
        # Strategy returns
        strategy_returns = positions[:-1] * returns.iloc[1:].values - costs[:-1]
        
        # Calculate metrics
        cumulative_returns = (1 + pd.Series(strategy_returns)).cumprod()
        
        results['total_return'] = cumulative_returns.iloc[-1] - 1
        results['sharpe'] = RiskManager.sharpe_ratio(pd.Series(strategy_returns))
        results['sortino'] = RiskManager.sortino_ratio(pd.Series(strategy_returns))
        results['max_drawdown'] = RiskManager.max_drawdown(cumulative_returns)
        results['win_rate'] = (strategy_returns > 0).mean()
        results['avg_win'] = strategy_returns[strategy_returns > 0].mean()
        results['avg_loss'] = strategy_returns[strategy_returns < 0].mean()
        results['calmar'] = RiskManager.calmar_ratio(pd.Series(strategy_returns))
        
        # VaR and CVaR
        results['var_95'] = RiskManager.calculate_var(strategy_returns, 0.95)
        results['cvar_95'] = RiskManager.calculate_cvar(strategy_returns, 0.95)
        
        return results, cumulative_returns

# Data fetcher
class DataFetcher:
    """Unified data fetcher with rate limiting"""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    def fetch_yahoo(self, symbol, period='3mo'):
        """Fetch data from Yahoo Finance"""
        cache_key = f"{symbol}_{period}"
        
        # Check cache
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                return cached_data
        
        try:
            # Handle Australian stocks
            original_symbol = symbol.upper()
            if original_symbol in AUSTRALIAN_STOCKS and not original_symbol.endswith('.AX'):
                symbol = f"{original_symbol}.AX"
            
            # Rate limiting
            global last_yahoo_request
            with request_lock:
                now = time.time()
                elapsed = now - last_yahoo_request
                if elapsed < YAHOO_REQUEST_DELAY:
                    time.sleep(YAHOO_REQUEST_DELAY - elapsed)
                last_yahoo_request = time.time()
            
            # Fetch data
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period)
            
            if not df.empty:
                # Cache the result
                self.cache[cache_key] = (df, time.time())
                return df
            
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
        
        return None

# Global instances
data_fetcher = DataFetcher()
multi_model = MultiModelPredictor()
portfolio_optimizer = PortfolioOptimizer()

@app.route('/api/advanced/analyze/<symbol>')
def advanced_analysis(symbol):
    """Comprehensive analysis with multiple ML models"""
    try:
        period = request.args.get('period', '3mo')
        
        # Fetch data
        df = data_fetcher.fetch_yahoo(symbol, period)
        
        if df is None or df.empty:
            return jsonify({'error': f'Unable to fetch data for {symbol}'}), 404
        
        # Calculate advanced features
        features = AdvancedTechnicalIndicators.calculate_all_advanced(df)
        
        # Train ensemble models
        print(f"Training ensemble models for {symbol}...")
        predictions = multi_model.train_ensemble(df)
        
        # Backtest each model
        backtest_results = {}
        
        for model_name, preds in predictions.items():
            if preds is not None:
                # Remove NaN predictions
                valid_mask = ~np.isnan(preds)
                if valid_mask.any():
                    valid_preds = preds[valid_mask]
                    valid_df = df.iloc[valid_mask]
                    
                    results, equity_curve = Backtester.walk_forward_backtest(
                        valid_df, valid_preds
                    )
                    
                    backtest_results[model_name] = {
                        'metrics': results,
                        'equity_curve': equity_curve.tolist() if hasattr(equity_curve, 'tolist') else []
                    }
        
        # Prepare response
        current_price = float(df['Close'].iloc[-1])
        prev_close = float(df['Close'].iloc[-2]) if len(df) > 1 else current_price
        
        # Get latest prediction from ensemble
        ensemble_prediction = 0.5
        if 'ensemble' in predictions and predictions['ensemble'] is not None:
            valid_ensemble = predictions['ensemble'][~np.isnan(predictions['ensemble'])]
            if len(valid_ensemble) > 0:
                ensemble_prediction = valid_ensemble[-1]
        
        return jsonify({
            'symbol': symbol,
            'current_price': current_price,
            'price_change': current_price - prev_close,
            'price_change_pct': ((current_price - prev_close) / prev_close) * 100,
            'ensemble_prediction': float(ensemble_prediction),
            'signal': 'BUY' if ensemble_prediction > 0.55 else 'SELL' if ensemble_prediction < 0.45 else 'HOLD',
            'confidence': abs(ensemble_prediction - 0.5) * 200,
            'backtest_results': backtest_results,
            'models_available': list(predictions.keys())
        })
        
    except Exception as e:
        print(f"Error in advanced analysis: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio/optimize', methods=['POST'])
def optimize_portfolio():
    """Portfolio optimization endpoint"""
    try:
        data = request.json
        symbols = data.get('symbols', [])
        method = data.get('method', 'hrp')  # hrp, mean_variance, risk_parity
        
        if len(symbols) < 2:
            return jsonify({'error': 'Need at least 2 symbols for portfolio optimization'}), 400
        
        # Fetch data for all symbols
        returns_data = []
        valid_symbols = []
        
        for symbol in symbols:
            df = data_fetcher.fetch_yahoo(symbol, period='1y')
            if df is not None and not df.empty:
                returns = df['Close'].pct_change().dropna()
                returns_data.append(returns)
                valid_symbols.append(symbol)
        
        if len(valid_symbols) < 2:
            return jsonify({'error': 'Insufficient valid symbols'}), 400
        
        # Create returns DataFrame
        returns_df = pd.concat(returns_data, axis=1)
        returns_df.columns = valid_symbols
        returns_df = returns_df.dropna()
        
        # Optimize based on method
        weights = None
        
        if method == 'hrp':
            weights = portfolio_optimizer.hierarchical_risk_parity(returns_df)
        elif method == 'mean_variance':
            weights = portfolio_optimizer.mean_variance(returns_df)
        elif method == 'risk_parity':
            weights = portfolio_optimizer.risk_parity(returns_df)
        
        if weights is None:
            return jsonify({'error': 'Optimization failed'}), 500
        
        # Calculate portfolio metrics
        portfolio_returns = (returns_df * weights).sum(axis=1)
        
        metrics = {
            'expected_return': float(portfolio_returns.mean() * 252),
            'volatility': float(portfolio_returns.std() * np.sqrt(252)),
            'sharpe_ratio': float(RiskManager.sharpe_ratio(portfolio_returns)),
            'sortino_ratio': float(RiskManager.sortino_ratio(portfolio_returns)),
            'max_drawdown': float(RiskManager.max_drawdown((1 + portfolio_returns).cumprod())),
            'var_95': float(RiskManager.calculate_var(portfolio_returns, 0.95)),
            'cvar_95': float(RiskManager.calculate_cvar(portfolio_returns, 0.95))
        }
        
        # Convert weights to dict
        weights_dict = {symbol: float(weight) for symbol, weight in weights.items()}
        
        return jsonify({
            'method': method,
            'weights': weights_dict,
            'metrics': metrics,
            'symbols': valid_symbols
        })
        
    except Exception as e:
        print(f"Error in portfolio optimization: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/risk/analysis', methods=['POST'])
def risk_analysis():
    """Comprehensive risk analysis"""
    try:
        data = request.json
        symbol = data.get('symbol')
        position_size = data.get('position_size', 10000)
        
        # Fetch data
        df = data_fetcher.fetch_yahoo(symbol, period='1y')
        
        if df is None or df.empty:
            return jsonify({'error': f'Unable to fetch data for {symbol}'}), 404
        
        returns = df['Close'].pct_change().dropna()
        
        # Calculate risk metrics
        metrics = {
            'daily_var_95': float(RiskManager.calculate_var(returns, 0.95)),
            'daily_var_99': float(RiskManager.calculate_var(returns, 0.99)),
            'daily_cvar_95': float(RiskManager.calculate_cvar(returns, 0.95)),
            'daily_cvar_99': float(RiskManager.calculate_cvar(returns, 0.99)),
            'annualized_volatility': float(returns.std() * np.sqrt(252)),
            'max_drawdown': float(RiskManager.max_drawdown((1 + returns).cumprod())),
            'sharpe_ratio': float(RiskManager.sharpe_ratio(returns)),
            'sortino_ratio': float(RiskManager.sortino_ratio(returns)),
            'calmar_ratio': float(RiskManager.calmar_ratio(returns))
        }
        
        # Position risk
        position_risk = {
            'var_95_dollar': metrics['daily_var_95'] * position_size,
            'var_99_dollar': metrics['daily_var_99'] * position_size,
            'cvar_95_dollar': metrics['daily_cvar_95'] * position_size,
            'cvar_99_dollar': metrics['daily_cvar_99'] * position_size
        }
        
        # Kelly sizing
        win_rate = (returns > 0).mean()
        avg_win = returns[returns > 0].mean() if (returns > 0).any() else 0
        avg_loss = abs(returns[returns < 0].mean()) if (returns < 0).any() else 0
        
        if avg_loss > 0:
            kelly_size = portfolio_optimizer.kelly_criterion(win_rate, avg_win, avg_loss)
        else:
            kelly_size = 0
        
        return jsonify({
            'symbol': symbol,
            'risk_metrics': metrics,
            'position_risk': position_risk,
            'kelly_sizing': {
                'win_rate': float(win_rate),
                'avg_win': float(avg_win),
                'avg_loss': float(avg_loss),
                'kelly_fraction': float(kelly_size),
                'recommended_position': position_size * kelly_size
            }
        })
        
    except Exception as e:
        print(f"Error in risk analysis: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'ml_available': ML_AVAILABLE,
        'xgboost_available': XGBOOST_AVAILABLE,
        'pytorch_available': TORCH_AVAILABLE,
        'optimization_available': CVXPY_AVAILABLE,
        'version': '4.0-advanced'
    })

@app.route('/')
def index():
    """Advanced ML Portfolio Interface"""
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Advanced ML Portfolio System</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1600px;
            margin: 0 auto;
        }
        .header {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.2);
        }
        .header h1 {
            color: #1e3c72;
            font-size: 36px;
            margin-bottom: 10px;
        }
        .header p {
            color: #666;
            font-size: 16px;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 25px;
            margin-bottom: 25px;
        }
        .card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.15);
        }
        .card h2 {
            color: #1e3c72;
            font-size: 24px;
            margin-bottom: 20px;
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 10px;
        }
        .controls {
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        input, select, button {
            padding: 12px 20px;
            border-radius: 8px;
            border: 1px solid #ddd;
            font-size: 15px;
        }
        button {
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            color: white;
            border: none;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(30,60,114,0.3);
        }
        .metric {
            display: inline-block;
            margin: 10px;
            padding: 15px;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 10px;
            min-width: 150px;
        }
        .metric-label {
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .metric-value {
            font-size: 24px;
            font-weight: bold;
            color: #1e3c72;
            margin-top: 5px;
        }
        .positive { color: #4caf50; }
        .negative { color: #f44336; }
        .neutral { color: #ff9800; }
        .chart-container {
            position: relative;
            height: 400px;
            margin: 20px 0;
        }
        .portfolio-weights {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .weight-item {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }
        .weight-symbol {
            font-size: 18px;
            font-weight: bold;
        }
        .weight-value {
            font-size: 28px;
            margin-top: 5px;
        }
        .risk-indicator {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            margin: 5px;
        }
        .risk-low { background: #4caf50; color: white; }
        .risk-medium { background: #ff9800; color: white; }
        .risk-high { background: #f44336; color: white; }
        .model-badge {
            display: inline-block;
            padding: 5px 10px;
            background: #1e3c72;
            color: white;
            border-radius: 5px;
            margin: 2px;
            font-size: 12px;
        }
        .signal-display {
            font-size: 48px;
            font-weight: bold;
            text-align: center;
            padding: 20px;
            border-radius: 15px;
            margin: 20px 0;
        }
        .signal-buy {
            background: linear-gradient(135deg, #4caf50, #8bc34a);
            color: white;
        }
        .signal-sell {
            background: linear-gradient(135deg, #f44336, #e91e63);
            color: white;
        }
        .signal-hold {
            background: linear-gradient(135deg, #ff9800, #ffc107);
            color: white;
        }
        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
        }
        .error {
            background: #ffebee;
            color: #c62828;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 2px solid #e0e0e0;
        }
        .tab {
            padding: 15px 25px;
            background: none;
            border: none;
            border-bottom: 3px solid transparent;
            cursor: pointer;
            font-weight: 600;
            color: #666;
            transition: all 0.3s;
        }
        .tab.active {
            color: #1e3c72;
            border-bottom-color: #1e3c72;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
            animation: fadeIn 0.5s;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .feature-card {
            background: #f5f5f5;
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid #1e3c72;
        }
        .feature-name {
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }
        .feature-value {
            font-size: 20px;
            color: #1e3c72;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Advanced ML Portfolio System</h1>
            <p>XGBoost • LSTM • Transformer • Portfolio Optimization • Risk Management</p>
            <div style="margin-top: 15px;">
                <span class="model-badge">XGBoost</span>
                <span class="model-badge">LSTM</span>
                <span class="model-badge">Transformer</span>
                <span class="model-badge">Mean-Variance</span>
                <span class="model-badge">HRP</span>
                <span class="model-badge">Risk Parity</span>
                <span class="model-badge">Kelly Criterion</span>
            </div>
        </div>
        
        <div class="grid">
            <!-- ML Analysis Card -->
            <div class="card">
                <h2>🤖 ML Analysis</h2>
                <div class="controls">
                    <input type="text" id="mlSymbol" placeholder="Symbol (e.g., AAPL)" value="AAPL">
                    <select id="mlPeriod">
                        <option value="1mo">1 Month</option>
                        <option value="3mo" selected>3 Months</option>
                        <option value="6mo">6 Months</option>
                        <option value="1y">1 Year</option>
                    </select>
                    <button onclick="runMLAnalysis()">Run Analysis</button>
                </div>
                <div id="mlResults">
                    <div class="loading">Enter a symbol and click "Run Analysis"</div>
                </div>
            </div>
            
            <!-- Portfolio Optimization Card -->
            <div class="card">
                <h2>📊 Portfolio Optimization</h2>
                <div class="controls">
                    <input type="text" id="portfolioSymbols" placeholder="Symbols (comma-separated)" value="AAPL,MSFT,GOOGL,AMZN">
                    <select id="optimizationMethod">
                        <option value="hrp">Hierarchical Risk Parity</option>
                        <option value="mean_variance">Mean-Variance</option>
                        <option value="risk_parity">Risk Parity</option>
                    </select>
                    <button onclick="optimizePortfolio()">Optimize</button>
                </div>
                <div id="portfolioResults">
                    <div class="loading">Enter symbols and click "Optimize"</div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>📈 Performance Metrics</h2>
            <div class="tabs">
                <button class="tab active" onclick="showTab('backtest')">Backtest Results</button>
                <button class="tab" onclick="showTab('risk')">Risk Analysis</button>
                <button class="tab" onclick="showTab('features')">Feature Importance</button>
            </div>
            
            <div id="backtest" class="tab-content active">
                <div class="chart-container">
                    <canvas id="backtestChart"></canvas>
                </div>
                <div id="backtestMetrics"></div>
            </div>
            
            <div id="risk" class="tab-content">
                <div id="riskAnalysis">
                    <div class="loading">Run risk analysis to see metrics</div>
                </div>
            </div>
            
            <div id="features" class="tab-content">
                <div id="featureImportance">
                    <div class="loading">Run ML analysis to see feature importance</div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let backtestChart = null;
        
        function showTab(tabName) {
            // Hide all tab contents
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            
            // Remove active from all tabs
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Show selected tab
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }
        
        async function runMLAnalysis() {
            const symbol = document.getElementById('mlSymbol').value;
            const period = document.getElementById('mlPeriod').value;
            
            if (!symbol) {
                alert('Please enter a symbol');
                return;
            }
            
            document.getElementById('mlResults').innerHTML = '<div class="loading">Running ML analysis...</div>';
            
            try {
                const response = await fetch(`/api/advanced/analyze/${symbol}?period=${period}`);
                const data = await response.json();
                
                if (response.ok) {
                    displayMLResults(data);
                    displayBacktestChart(data.backtest_results);
                } else {
                    document.getElementById('mlResults').innerHTML = 
                        `<div class="error">Error: ${data.error}</div>`;
                }
            } catch (error) {
                document.getElementById('mlResults').innerHTML = 
                    `<div class="error">Error: ${error.message}</div>`;
            }
            
            // Also run risk analysis
            runRiskAnalysis(symbol);
        }
        
        function displayMLResults(data) {
            const signalClass = data.signal === 'BUY' ? 'signal-buy' : 
                               data.signal === 'SELL' ? 'signal-sell' : 'signal-hold';
            
            let html = `
                <div class="signal-display ${signalClass}">
                    ${data.signal}
                    <div style="font-size: 16px; margin-top: 10px;">
                        Confidence: ${data.confidence.toFixed(1)}%
                    </div>
                </div>
                
                <div style="margin-top: 20px;">
                    <div class="metric">
                        <div class="metric-label">Current Price</div>
                        <div class="metric-value">$${data.current_price.toFixed(2)}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Change</div>
                        <div class="metric-value ${data.price_change >= 0 ? 'positive' : 'negative'}">
                            ${data.price_change >= 0 ? '+' : ''}${data.price_change.toFixed(2)}
                            (${data.price_change_pct.toFixed(2)}%)
                        </div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Prediction</div>
                        <div class="metric-value">${(data.ensemble_prediction * 100).toFixed(1)}%</div>
                    </div>
                </div>
                
                <div style="margin-top: 15px;">
                    <strong>Models Used:</strong>
                    ${data.models_available.map(m => `<span class="model-badge">${m.toUpperCase()}</span>`).join(' ')}
                </div>
            `;
            
            document.getElementById('mlResults').innerHTML = html;
        }
        
        function displayBacktestChart(backtestResults) {
            if (!backtestResults || Object.keys(backtestResults).length === 0) {
                return;
            }
            
            const ctx = document.getElementById('backtestChart').getContext('2d');
            
            if (backtestChart) {
                backtestChart.destroy();
            }
            
            const datasets = [];
            const colors = ['#1e3c72', '#4caf50', '#ff9800', '#e91e63', '#9c27b0'];
            let colorIndex = 0;
            
            // Display metrics
            let metricsHtml = '<div class="feature-grid">';
            
            for (const [modelName, results] of Object.entries(backtestResults)) {
                if (results.equity_curve && results.equity_curve.length > 0) {
                    datasets.push({
                        label: modelName.toUpperCase(),
                        data: results.equity_curve,
                        borderColor: colors[colorIndex % colors.length],
                        backgroundColor: colors[colorIndex % colors.length] + '20',
                        borderWidth: 2,
                        tension: 0.1
                    });
                    colorIndex++;
                }
                
                // Add metrics
                if (results.metrics) {
                    metricsHtml += `
                        <div class="feature-card">
                            <div class="feature-name">${modelName.toUpperCase()}</div>
                            <div style="font-size: 14px; margin-top: 10px;">
                                Sharpe: ${results.metrics.sharpe?.toFixed(2) || 'N/A'}<br>
                                Max DD: ${(results.metrics.max_drawdown * 100)?.toFixed(1) || 'N/A'}%<br>
                                Win Rate: ${(results.metrics.win_rate * 100)?.toFixed(1) || 'N/A'}%
                            </div>
                        </div>
                    `;
                }
            }
            
            metricsHtml += '</div>';
            document.getElementById('backtestMetrics').innerHTML = metricsHtml;
            
            if (datasets.length === 0) {
                return;
            }
            
            // Create labels
            const maxLength = Math.max(...datasets.map(d => d.data.length));
            const labels = Array.from({length: maxLength}, (_, i) => i);
            
            backtestChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: datasets
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Model Equity Curves',
                            font: { size: 16 }
                        },
                        legend: {
                            display: true,
                            position: 'top'
                        }
                    },
                    scales: {
                        y: {
                            title: {
                                display: true,
                                text: 'Cumulative Return'
                            }
                        }
                    }
                }
            });
        }
        
        async function optimizePortfolio() {
            const symbolsInput = document.getElementById('portfolioSymbols').value;
            const method = document.getElementById('optimizationMethod').value;
            
            if (!symbolsInput) {
                alert('Please enter symbols');
                return;
            }
            
            const symbols = symbolsInput.split(',').map(s => s.trim());
            
            document.getElementById('portfolioResults').innerHTML = 
                '<div class="loading">Optimizing portfolio...</div>';
            
            try {
                const response = await fetch('/api/portfolio/optimize', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ symbols, method })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    displayPortfolioResults(data);
                } else {
                    document.getElementById('portfolioResults').innerHTML = 
                        `<div class="error">Error: ${data.error}</div>`;
                }
            } catch (error) {
                document.getElementById('portfolioResults').innerHTML = 
                    `<div class="error">Error: ${error.message}</div>`;
            }
        }
        
        function displayPortfolioResults(data) {
            let html = '<div class="portfolio-weights">';
            
            for (const [symbol, weight] of Object.entries(data.weights)) {
                html += `
                    <div class="weight-item">
                        <div class="weight-symbol">${symbol}</div>
                        <div class="weight-value">${(weight * 100).toFixed(1)}%</div>
                    </div>
                `;
            }
            
            html += '</div>';
            
            html += '<div style="margin-top: 20px;">';
            html += `
                <div class="metric">
                    <div class="metric-label">Expected Return</div>
                    <div class="metric-value">${(data.metrics.expected_return * 100).toFixed(2)}%</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Volatility</div>
                    <div class="metric-value">${(data.metrics.volatility * 100).toFixed(2)}%</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Sharpe Ratio</div>
                    <div class="metric-value">${data.metrics.sharpe_ratio.toFixed(2)}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Max Drawdown</div>
                    <div class="metric-value negative">${(data.metrics.max_drawdown * 100).toFixed(2)}%</div>
                </div>
            `;
            html += '</div>';
            
            document.getElementById('portfolioResults').innerHTML = html;
        }
        
        async function runRiskAnalysis(symbol) {
            try {
                const response = await fetch('/api/risk/analysis', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ symbol, position_size: 10000 })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    displayRiskAnalysis(data);
                }
            } catch (error) {
                console.error('Risk analysis error:', error);
            }
        }
        
        function displayRiskAnalysis(data) {
            let html = '<div class="feature-grid">';
            
            // Risk metrics
            html += `
                <div class="feature-card">
                    <div class="feature-name">Daily VaR (95%)</div>
                    <div class="feature-value">${(data.risk_metrics.daily_var_95 * 100).toFixed(2)}%</div>
                </div>
                <div class="feature-card">
                    <div class="feature-name">Daily CVaR (95%)</div>
                    <div class="feature-value">${(data.risk_metrics.daily_cvar_95 * 100).toFixed(2)}%</div>
                </div>
                <div class="feature-card">
                    <div class="feature-name">Annual Volatility</div>
                    <div class="feature-value">${(data.risk_metrics.annualized_volatility * 100).toFixed(2)}%</div>
                </div>
                <div class="feature-card">
                    <div class="feature-name">Sharpe Ratio</div>
                    <div class="feature-value">${data.risk_metrics.sharpe_ratio.toFixed(2)}</div>
                </div>
                <div class="feature-card">
                    <div class="feature-name">Sortino Ratio</div>
                    <div class="feature-value">${data.risk_metrics.sortino_ratio.toFixed(2)}</div>
                </div>
                <div class="feature-card">
                    <div class="feature-name">Max Drawdown</div>
                    <div class="feature-value negative">${(data.risk_metrics.max_drawdown * 100).toFixed(2)}%</div>
                </div>
            `;
            
            html += '</div>';
            
            // Kelly sizing
            if (data.kelly_sizing) {
                html += '<h3 style="margin-top: 20px;">Kelly Criterion Position Sizing</h3>';
                html += '<div class="feature-grid">';
                html += `
                    <div class="feature-card">
                        <div class="feature-name">Win Rate</div>
                        <div class="feature-value">${(data.kelly_sizing.win_rate * 100).toFixed(1)}%</div>
                    </div>
                    <div class="feature-card">
                        <div class="feature-name">Avg Win</div>
                        <div class="feature-value positive">+${(data.kelly_sizing.avg_win * 100).toFixed(2)}%</div>
                    </div>
                    <div class="feature-card">
                        <div class="feature-name">Avg Loss</div>
                        <div class="feature-value negative">-${(data.kelly_sizing.avg_loss * 100).toFixed(2)}%</div>
                    </div>
                    <div class="feature-card">
                        <div class="feature-name">Kelly Fraction</div>
                        <div class="feature-value">${(data.kelly_sizing.kelly_fraction * 100).toFixed(1)}%</div>
                    </div>
                `;
                html += '</div>';
            }
            
            document.getElementById('riskAnalysis').innerHTML = html;
        }
    </script>
</body>
</html>
    ''')

if __name__ == '__main__':
    print("\n" + "="*60)
    print("Starting Advanced ML Portfolio System...")
    print("="*60)
    print("Features:")
    print("  • Multiple ML Models: XGBoost, LSTM, Transformer")
    print("  • Portfolio Optimization: Mean-Variance, HRP, Risk Parity")
    print("  • Risk Management: VaR, CVaR, Kelly Criterion")
    print("  • Walk-Forward Backtesting")
    print("  • Advanced Technical Indicators")
    print("="*60)
    print(f"Server running on: http://localhost:5002")
    print("="*60 + "\n")
    
    app.run(debug=True, port=5002, host='0.0.0.0')