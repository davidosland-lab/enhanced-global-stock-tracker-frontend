"""
ML Enhancements Based on Literature Review Research
Additional features and models based on scientific findings
"""

import numpy as np
import pandas as pd
from sklearn.svm import SVR, SVC
from sklearn.neural_network import MLPRegressor
from sklearn.ensemble import VotingRegressor, VotingClassifier
from sklearn.preprocessing import StandardScaler
import talib
import yfinance as yf

class EnhancedFeatureEngineering:
    """
    Extended feature engineering based on 2,173 variables from research
    """
    
    @staticmethod
    def calculate_advanced_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate comprehensive technical indicators based on research findings
        """
        
        # Price-based features
        df['returns'] = df['Close'].pct_change()
        df['log_returns'] = np.log(df['Close'] / df['Close'].shift(1))
        df['cumulative_returns'] = (1 + df['returns']).cumprod()
        
        # Volatility measures
        df['volatility_20'] = df['returns'].rolling(window=20).std() * np.sqrt(252)
        df['volatility_60'] = df['returns'].rolling(window=60).std() * np.sqrt(252)
        df['volatility_ratio'] = df['volatility_20'] / df['volatility_60']
        
        # Advanced moving averages
        df['ema_12'] = df['Close'].ewm(span=12).mean()
        df['ema_26'] = df['Close'].ewm(span=26).mean()
        df['sma_50'] = df['Close'].rolling(window=50).mean()
        df['sma_200'] = df['Close'].rolling(window=200).mean()
        df['ma_cross'] = np.where(df['sma_50'] > df['sma_200'], 1, -1)
        
        # Price position indicators
        df['price_to_sma20'] = df['Close'] / df['Close'].rolling(20).mean()
        df['price_to_sma50'] = df['Close'] / df['Close'].rolling(50).mean()
        
        # Momentum indicators
        df['momentum_10'] = df['Close'] - df['Close'].shift(10)
        df['momentum_30'] = df['Close'] - df['Close'].shift(30)
        df['roc_10'] = ((df['Close'] - df['Close'].shift(10)) / df['Close'].shift(10)) * 100
        
        # Enhanced RSI variations
        df['rsi_14'] = talib.RSI(df['Close'].values, timeperiod=14)
        df['rsi_28'] = talib.RSI(df['Close'].values, timeperiod=28)
        df['stoch_rsi'] = (df['rsi_14'] - df['rsi_14'].rolling(14).min()) / \
                          (df['rsi_14'].rolling(14).max() - df['rsi_14'].rolling(14).min())
        
        # MACD variations
        df['macd'], df['macd_signal'], df['macd_hist'] = talib.MACD(
            df['Close'].values, fastperiod=12, slowperiod=26, signalperiod=9
        )
        df['macd_cross'] = np.where(df['macd'] > df['macd_signal'], 1, -1)
        
        # Bollinger Bands enhanced
        df['bb_upper'], df['bb_middle'], df['bb_lower'] = talib.BBANDS(
            df['Close'].values, timeperiod=20, nbdevup=2, nbdevdn=2
        )
        df['bb_width'] = df['bb_upper'] - df['bb_lower']
        df['bb_position'] = (df['Close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        
        # Volume indicators
        df['volume_sma'] = df['Volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['Volume'] / df['volume_sma']
        df['obv'] = talib.OBV(df['Close'].values, df['Volume'].values)
        df['ad'] = talib.AD(df['High'].values, df['Low'].values, 
                           df['Close'].values, df['Volume'].values)
        
        # Money Flow Index
        df['mfi'] = talib.MFI(df['High'].values, df['Low'].values,
                             df['Close'].values, df['Volume'].values, timeperiod=14)
        
        # Average True Range (volatility)
        df['atr'] = talib.ATR(df['High'].values, df['Low'].values, 
                             df['Close'].values, timeperiod=14)
        df['natr'] = talib.NATR(df['High'].values, df['Low'].values,
                               df['Close'].values, timeperiod=14)
        
        # Commodity Channel Index
        df['cci'] = talib.CCI(df['High'].values, df['Low'].values,
                             df['Close'].values, timeperiod=14)
        
        # Williams %R
        df['willr'] = talib.WILLR(df['High'].values, df['Low'].values,
                                 df['Close'].values, timeperiod=14)
        
        # Aroon indicators
        df['aroon_up'], df['aroon_down'] = talib.AROON(df['High'].values, 
                                                       df['Low'].values, timeperiod=25)
        df['aroon_osc'] = talib.AROONOSC(df['High'].values, df['Low'].values, timeperiod=25)
        
        # Pattern recognition
        df['doji'] = talib.CDLDOJI(df['Open'].values, df['High'].values,
                                  df['Low'].values, df['Close'].values)
        df['hammer'] = talib.CDLHAMMER(df['Open'].values, df['High'].values,
                                      df['Low'].values, df['Close'].values)
        df['shooting_star'] = talib.CDLSHOOTINGSTAR(df['Open'].values, df['High'].values,
                                                   df['Low'].values, df['Close'].values)
        
        # Market microstructure
        df['high_low_spread'] = (df['High'] - df['Low']) / df['Close']
        df['close_open_spread'] = (df['Close'] - df['Open']) / df['Open']
        
        # Trend strength
        df['adx'] = talib.ADX(df['High'].values, df['Low'].values,
                             df['Close'].values, timeperiod=14)
        df['plus_di'] = talib.PLUS_DI(df['High'].values, df['Low'].values,
                                     df['Close'].values, timeperiod=14)
        df['minus_di'] = talib.MINUS_DI(df['High'].values, df['Low'].values,
                                       df['Close'].values, timeperiod=14)
        
        return df
    
    @staticmethod
    def calculate_market_regime_features(df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate market regime and structural features
        """
        
        # Market regime detection
        df['bull_market'] = np.where(df['sma_50'] > df['sma_200'], 1, 0)
        df['bear_market'] = np.where(df['sma_50'] < df['sma_200'], 1, 0)
        
        # Volatility regime
        vol_median = df['volatility_20'].median()
        df['high_vol_regime'] = np.where(df['volatility_20'] > vol_median * 1.5, 1, 0)
        df['low_vol_regime'] = np.where(df['volatility_20'] < vol_median * 0.7, 1, 0)
        
        # Trend strength
        df['trend_strength'] = abs(df['returns'].rolling(20).mean()) / df['returns'].rolling(20).std()
        
        # Support and resistance levels
        df['resistance'] = df['High'].rolling(window=20).max()
        df['support'] = df['Low'].rolling(window=20).min()
        df['price_to_resistance'] = df['Close'] / df['resistance']
        df['price_to_support'] = df['Close'] / df['support']
        
        return df
    
    @staticmethod
    def add_macroeconomic_features(df: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """
        Add macroeconomic indicators
        """
        try:
            # Fetch related macro data
            # VIX - Market fear index
            vix = yf.Ticker("^VIX").history(period="2y", interval="1d")['Close']
            vix.name = 'vix'
            df = df.join(vix, how='left')
            df['vix'].fillna(method='ffill', inplace=True)
            
            # Dollar Index
            dxy = yf.Ticker("DX-Y.NYB").history(period="2y", interval="1d")['Close']
            dxy.name = 'dollar_index'
            df = df.join(dxy, how='left')
            df['dollar_index'].fillna(method='ffill', inplace=True)
            
            # 10-Year Treasury Yield
            tnx = yf.Ticker("^TNX").history(period="2y", interval="1d")['Close']
            tnx.name = 'treasury_10y'
            df = df.join(tnx, how='left')
            df['treasury_10y'].fillna(method='ffill', inplace=True)
            
            # Gold prices (safe haven indicator)
            gold = yf.Ticker("GC=F").history(period="2y", interval="1d")['Close']
            gold.name = 'gold'
            df = df.join(gold, how='left')
            df['gold'].fillna(method='ffill', inplace=True)
            
            # Calculate relative metrics
            df['vix_ma'] = df['vix'].rolling(window=20).mean()
            df['vix_ratio'] = df['vix'] / df['vix_ma']
            df['gold_returns'] = df['gold'].pct_change()
            
        except Exception as e:
            print(f"Could not fetch all macroeconomic data: {e}")
            
        return df


class HybridMLModels:
    """
    Hybrid and ensemble models based on research findings
    """
    
    @staticmethod
    def create_svm_model(kernel='rbf'):
        """Support Vector Machine - one of the most effective according to research"""
        return SVR(kernel=kernel, C=100, gamma='scale', epsilon=0.1)
    
    @staticmethod
    def create_neural_network():
        """Multi-layer Perceptron - historically most used"""
        return MLPRegressor(
            hidden_layer_sizes=(100, 50, 25),
            activation='relu',
            solver='adam',
            alpha=0.001,
            learning_rate='adaptive',
            max_iter=500,
            early_stopping=True,
            validation_fraction=0.1
        )
    
    @staticmethod
    def create_ensemble_model(models_dict):
        """
        Create voting ensemble of multiple models
        Based on research showing hybrid models perform better
        """
        return VotingRegressor(
            estimators=[(name, model) for name, model in models_dict.items()],
            weights=None  # Equal weights, or can be optimized
        )
    
    @staticmethod
    def create_stacked_model(base_models, meta_learner):
        """
        Stacking ensemble - advanced technique from research
        """
        from sklearn.ensemble import StackingRegressor
        return StackingRegressor(
            estimators=[(f"model_{i}", model) for i, model in enumerate(base_models)],
            final_estimator=meta_learner,
            cv=5
        )


class MarketRegimeAdaptiveModel:
    """
    Adaptive model that switches strategies based on market regime
    Research shows different models work better in different market conditions
    """
    
    def __init__(self):
        self.bull_model = None
        self.bear_model = None
        self.high_vol_model = None
        self.normal_model = None
        
    def detect_regime(self, df: pd.DataFrame) -> str:
        """Detect current market regime"""
        latest = df.iloc[-1]
        
        if latest.get('high_vol_regime', 0) == 1:
            return 'high_volatility'
        elif latest.get('bull_market', 0) == 1:
            return 'bull'
        elif latest.get('bear_market', 0) == 1:
            return 'bear'
        else:
            return 'normal'
    
    def select_model(self, regime: str):
        """Select appropriate model based on regime"""
        model_map = {
            'bull': self.bull_model,
            'bear': self.bear_model,
            'high_volatility': self.high_vol_model,
            'normal': self.normal_model
        }
        return model_map.get(regime, self.normal_model)
    
    def train_regime_specific_models(self, X_train, y_train, regime_labels):
        """Train different models for different regimes"""
        from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
        
        # Bull market model - tend to use momentum
        bull_mask = regime_labels == 'bull'
        if bull_mask.any():
            self.bull_model = RandomForestRegressor(n_estimators=100, max_depth=10)
            self.bull_model.fit(X_train[bull_mask], y_train[bull_mask])
        
        # Bear market model - more conservative
        bear_mask = regime_labels == 'bear'
        if bear_mask.any():
            self.bear_model = GradientBoostingRegressor(n_estimators=100, max_depth=5)
            self.bear_model.fit(X_train[bear_mask], y_train[bear_mask])
        
        # High volatility model - robust methods
        vol_mask = regime_labels == 'high_volatility'
        if vol_mask.any():
            self.high_vol_model = SVR(kernel='rbf', C=10)
            self.high_vol_model.fit(X_train[vol_mask], y_train[vol_mask])
        
        # Normal conditions model
        self.normal_model = RandomForestRegressor(n_estimators=150, max_depth=15)
        self.normal_model.fit(X_train, y_train)


def calculate_feature_importance_score(X, y, feature_names):
    """
    Calculate feature importance using multiple methods
    Research shows feature selection is crucial
    """
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.feature_selection import mutual_info_regression, f_regression
    
    # Random Forest importance
    rf = RandomForestRegressor(n_estimators=100, random_state=42)
    rf.fit(X, y)
    rf_importance = rf.feature_importances_
    
    # Mutual information
    mi_importance = mutual_info_regression(X, y, random_state=42)
    
    # F-statistic
    f_scores, _ = f_regression(X, y)
    f_importance = f_scores / f_scores.max()
    
    # Combine scores
    combined_importance = (rf_importance + mi_importance + f_importance) / 3
    
    # Create importance dataframe
    importance_df = pd.DataFrame({
        'feature': feature_names,
        'rf_importance': rf_importance,
        'mi_importance': mi_importance,
        'f_importance': f_importance,
        'combined': combined_importance
    }).sort_values('combined', ascending=False)
    
    return importance_df


def select_optimal_features(importance_df, threshold=0.1):
    """
    Select features based on importance threshold
    Research shows 20-50 features is often optimal
    """
    # Select features above threshold
    selected = importance_df[importance_df['combined'] > threshold]['feature'].tolist()
    
    # Ensure minimum and maximum feature counts
    if len(selected) < 20:
        selected = importance_df.head(20)['feature'].tolist()
    elif len(selected) > 50:
        selected = importance_df.head(50)['feature'].tolist()
    
    return selected


# Example usage in your unified system:
def enhance_ml_training(df: pd.DataFrame, symbol: str):
    """
    Enhanced ML training incorporating research findings
    """
    
    # 1. Calculate comprehensive features
    enhancer = EnhancedFeatureEngineering()
    df = enhancer.calculate_advanced_technical_indicators(df)
    df = enhancer.calculate_market_regime_features(df)
    df = enhancer.add_macroeconomic_features(df, symbol)
    
    # 2. Feature selection
    feature_cols = [col for col in df.columns if col not in ['Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']]
    X = df[feature_cols].dropna()
    y = df['Close'].shift(-1).dropna()  # Predict next day
    
    # Align X and y
    min_len = min(len(X), len(y))
    X = X.iloc[:min_len]
    y = y.iloc[:min_len]
    
    # 3. Calculate feature importance
    importance_df = calculate_feature_importance_score(X.values, y.values, feature_cols)
    optimal_features = select_optimal_features(importance_df)
    
    # 4. Create multiple models
    models = {
        'rf': RandomForestRegressor(n_estimators=100, max_depth=10),
        'svm': HybridMLModels.create_svm_model(),
        'nn': HybridMLModels.create_neural_network()
    }
    
    # 5. Create ensemble
    ensemble = HybridMLModels.create_ensemble_model(models)
    
    return ensemble, optimal_features, importance_df