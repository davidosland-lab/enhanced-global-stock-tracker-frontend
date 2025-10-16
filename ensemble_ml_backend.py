"""
Experimental: Ensemble ML Backend with Model Reuse
This shows how to implement model reuse/ensemble for RandomForest
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import yfinance as yf
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

class EnsembleModelManager:
    """Manages ensemble of RandomForest models with reuse"""
    
    def __init__(self, model_dir="ensemble_models", max_models=3):
        self.model_dir = model_dir
        self.max_models = max_models
        os.makedirs(model_dir, exist_ok=True)
        
    def train_with_ensemble(self, symbol: str, days_back: int = 365) -> Dict:
        """Train new model and create ensemble with previous models"""
        
        # Fetch and prepare data
        print(f"Fetching {days_back} days of data for {symbol}...")
        df = self._fetch_data(symbol, days_back)
        X, y, feature_names = self._prepare_features(df)
        
        # Check for previous models
        previous_models = self._load_previous_models(symbol)
        
        # If we have previous models, add their predictions as features
        if previous_models:
            print(f"Found {len(previous_models)} previous models. Adding transfer learning features...")
            X = self._add_transfer_features(X, previous_models)
            feature_names.extend([f"prev_model_{i}_pred" for i in range(len(previous_models))])
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, shuffle=False
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train new model
        print(f"Training new RandomForest model with {X_train.shape[0]} samples...")
        new_model = RandomForestRegressor(
            n_estimators=500,
            max_depth=20,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        new_model.fit(X_train_scaled, y_train)
        
        # Evaluate individual model
        train_score = new_model.score(X_train_scaled, y_train)
        test_score = new_model.score(X_test_scaled, y_test)
        
        print(f"New Model - Train R²: {train_score:.4f}, Test R²: {test_score:.4f}")
        
        # Create ensemble predictions if we have previous models
        if previous_models:
            ensemble_pred = self._ensemble_predict(
                previous_models + [new_model],
                X_test_scaled,
                method='weighted_average'
            )
            ensemble_score = r2_score(y_test, ensemble_pred)
            print(f"Ensemble - Test R²: {ensemble_score:.4f}")
            
            improvement = ensemble_score - test_score
            if improvement > 0:
                print(f"✅ Ensemble improved by {improvement:.4f}")
            else:
                print(f"❌ Ensemble decreased by {abs(improvement):.4f}")
        else:
            ensemble_score = test_score
        
        # Save model and scaler
        model_id = f"{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        model_path = os.path.join(self.model_dir, f"{model_id}.pkl")
        scaler_path = os.path.join(self.model_dir, f"{model_id}_scaler.pkl")
        
        joblib.dump(new_model, model_path)
        joblib.dump(scaler, scaler_path)
        
        # Clean up old models if we have too many
        self._cleanup_old_models(symbol)
        
        return {
            "model_id": model_id,
            "train_score": train_score,
            "test_score": test_score,
            "ensemble_score": ensemble_score,
            "previous_models_used": len(previous_models),
            "features_used": len(feature_names)
        }
    
    def predict_with_ensemble(self, symbol: str, use_ensemble: bool = True) -> Dict:
        """Make predictions using ensemble or single model"""
        
        # Get latest data
        df = self._fetch_data(symbol, days_back=30)
        X, _, feature_names = self._prepare_features(df)
        
        # Load models
        models = self._load_previous_models(symbol)
        
        if not models:
            raise ValueError(f"No trained models found for {symbol}")
        
        if use_ensemble and len(models) > 1:
            # Use ensemble of all available models
            print(f"Using ensemble of {len(models)} models")
            
            # Add transfer features if needed
            if len(models) > 1:
                X = self._add_transfer_features(X, models[:-1])
            
            # Scale features using latest scaler
            latest_scaler = self._load_latest_scaler(symbol)
            X_scaled = latest_scaler.transform(X[-1:])
            
            # Ensemble prediction
            prediction = self._ensemble_predict(models, X_scaled, method='weighted_average')
            confidence = self._calculate_ensemble_confidence(models, X_scaled)
            
            return {
                "prediction": float(prediction[0]),
                "confidence": float(confidence),
                "models_used": len(models),
                "method": "ensemble_weighted"
            }
        else:
            # Use single latest model
            print("Using single latest model")
            model = models[-1]
            scaler = self._load_latest_scaler(symbol)
            
            X_scaled = scaler.transform(X[-1:])
            prediction = model.predict(X_scaled)
            
            return {
                "prediction": float(prediction[0]),
                "confidence": 0.0,  # Would need to calculate from test score
                "models_used": 1,
                "method": "single_model"
            }
    
    def _fetch_data(self, symbol: str, days_back: int) -> pd.DataFrame:
        """Fetch stock data from Yahoo Finance"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start_date, end=end_date)
        
        if df.empty:
            raise ValueError(f"No data found for {symbol}")
        
        return df
    
    def _prepare_features(self, df: pd.DataFrame):
        """Prepare features from dataframe"""
        # Calculate technical indicators
        df['returns'] = df['Close'].pct_change()
        df['sma_5'] = df['Close'].rolling(window=5).mean()
        df['sma_20'] = df['Close'].rolling(window=20).mean()
        df['sma_50'] = df['Close'].rolling(window=50).mean()
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # Volume indicators
        df['volume_sma'] = df['Volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['Volume'] / df['volume_sma']
        
        # Drop NaN values
        df = df.dropna()
        
        # Select features
        feature_cols = ['Open', 'High', 'Low', 'Volume', 'returns', 
                       'sma_5', 'sma_20', 'sma_50', 'rsi', 'volume_ratio']
        
        X = df[feature_cols].values
        y = df['Close'].values
        
        return X, y, feature_cols
    
    def _load_previous_models(self, symbol: str) -> List:
        """Load previous models for a symbol"""
        import glob
        
        model_files = glob.glob(os.path.join(self.model_dir, f"{symbol}_*.pkl"))
        model_files = [f for f in model_files if not f.endswith('_scaler.pkl')]
        model_files.sort()  # Sort by date
        
        # Load only the most recent models
        model_files = model_files[-self.max_models:]
        
        models = []
        for model_file in model_files:
            try:
                model = joblib.load(model_file)
                models.append(model)
                print(f"Loaded model: {os.path.basename(model_file)}")
            except Exception as e:
                print(f"Failed to load {model_file}: {e}")
        
        return models
    
    def _load_latest_scaler(self, symbol: str):
        """Load the most recent scaler for a symbol"""
        import glob
        
        scaler_files = glob.glob(os.path.join(self.model_dir, f"{symbol}_*_scaler.pkl"))
        if not scaler_files:
            raise ValueError(f"No scaler found for {symbol}")
        
        scaler_files.sort()
        return joblib.load(scaler_files[-1])
    
    def _add_transfer_features(self, X: np.ndarray, previous_models: List) -> np.ndarray:
        """Add predictions from previous models as features"""
        transfer_features = []
        
        for model in previous_models:
            try:
                # Get predictions from previous model
                # Note: This assumes models were trained on similar features
                predictions = model.predict(X)
                transfer_features.append(predictions.reshape(-1, 1))
            except Exception as e:
                print(f"Warning: Could not get predictions from previous model: {e}")
        
        if transfer_features:
            # Concatenate original features with transfer learning features
            X_enhanced = np.hstack([X] + transfer_features)
            return X_enhanced
        
        return X
    
    def _ensemble_predict(self, models: List, X: np.ndarray, method: str = 'weighted_average'):
        """Make ensemble predictions"""
        predictions = []
        
        for i, model in enumerate(models):
            pred = model.predict(X)
            predictions.append(pred)
        
        predictions = np.array(predictions)
        
        if method == 'simple_average':
            # Simple average
            return np.mean(predictions, axis=0)
        
        elif method == 'weighted_average':
            # Weight recent models more
            weights = np.array([i + 1 for i in range(len(models))])
            weights = weights / weights.sum()
            return np.average(predictions, weights=weights, axis=0)
        
        elif method == 'median':
            # Use median (robust to outliers)
            return np.median(predictions, axis=0)
        
        else:
            return np.mean(predictions, axis=0)
    
    def _calculate_ensemble_confidence(self, models: List, X: np.ndarray) -> float:
        """Calculate confidence based on prediction variance"""
        predictions = []
        
        for model in models:
            pred = model.predict(X)
            predictions.append(pred)
        
        predictions = np.array(predictions)
        
        # Low variance = high confidence
        variance = np.var(predictions)
        mean_pred = np.mean(predictions)
        
        # Coefficient of variation (CV)
        cv = np.sqrt(variance) / (mean_pred + 1e-10)
        
        # Convert to confidence (0-1 scale)
        confidence = max(0, min(1, 1 - cv))
        
        return confidence
    
    def _cleanup_old_models(self, symbol: str):
        """Remove old models beyond max_models limit"""
        import glob
        
        model_files = glob.glob(os.path.join(self.model_dir, f"{symbol}_*.pkl"))
        model_files = [f for f in model_files if not f.endswith('_scaler.pkl')]
        model_files.sort()
        
        # Keep only the most recent models
        if len(model_files) > self.max_models:
            for old_file in model_files[:-self.max_models]:
                try:
                    os.remove(old_file)
                    # Also remove associated scaler
                    scaler_file = old_file.replace('.pkl', '_scaler.pkl')
                    if os.path.exists(scaler_file):
                        os.remove(scaler_file)
                    print(f"Removed old model: {os.path.basename(old_file)}")
                except Exception as e:
                    print(f"Error removing {old_file}: {e}")


# Example usage
if __name__ == "__main__":
    # Create ensemble manager
    manager = EnsembleModelManager(max_models=3)
    
    # Train models over time
    print("=" * 60)
    print("ENSEMBLE MODEL TRAINING EXPERIMENT")
    print("=" * 60)
    
    # Simulate training over multiple periods
    for i in range(3):
        print(f"\n--- Training Iteration {i+1} ---")
        result = manager.train_with_ensemble("AAPL", days_back=365)
        print(f"Results: {json.dumps(result, indent=2)}")
        
    # Make prediction with ensemble
    print("\n--- Making Ensemble Prediction ---")
    prediction = manager.predict_with_ensemble("AAPL", use_ensemble=True)
    print(f"Prediction: {json.dumps(prediction, indent=2)}")