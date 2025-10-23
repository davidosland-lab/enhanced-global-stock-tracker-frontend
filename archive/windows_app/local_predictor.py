"""
Local Prediction Engine - Runs on user's computer
"""

import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import joblib
import os
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class LocalPredictor:
    """Local prediction engine using trained models"""
    
    def __init__(self, models_dir: str):
        self.models_dir = models_dir
        self.loaded_models = {}
        self.load_models()
    
    def load_models(self):
        """Load saved models from disk"""
        try:
            model_files = [f for f in os.listdir(self.models_dir) if f.endswith('.pkl')]
            
            for model_file in model_files:
                model_path = os.path.join(self.models_dir, model_file)
                model_name = model_file.replace('.pkl', '')
                
                try:
                    self.loaded_models[model_name] = joblib.load(model_path)
                    logger.info(f"Loaded model: {model_name}")
                except Exception as e:
                    logger.error(f"Failed to load {model_name}: {e}")
                    
        except Exception as e:
            logger.error(f"Error loading models: {e}")
    
    def predict(self, symbol: str, timeframe: str, model_type: str) -> Dict[str, Any]:
        """Generate prediction using local models"""
        
        try:
            # Fetch recent data
            data = self.fetch_data(symbol, timeframe)
            
            if data.empty:
                return {"error": "No data available"}
            
            # Calculate features
            features = self.calculate_features(data)
            
            # Get current price
            current_price = float(data['Close'].iloc[-1])
            
            predictions = {}
            confidence_scores = {}
            
            # Use specified model or all models
            if model_type == "All Models":
                models_to_use = self.loaded_models.keys()
            else:
                models_to_use = [k for k in self.loaded_models.keys() if model_type.lower() in k.lower()]
            
            # Generate predictions from each model
            for model_name in models_to_use:
                model = self.loaded_models[model_name]
                
                try:
                    # Prepare features for model
                    X = features.iloc[-1:].values
                    
                    # Make prediction
                    pred = model.predict(X)[0]
                    
                    # Convert to price prediction
                    predicted_change = pred  # Assuming model predicts returns
                    predicted_price = current_price * (1 + predicted_change)
                    
                    predictions[model_name] = predicted_price
                    
                    # Estimate confidence based on model type
                    confidence_scores[model_name] = self.estimate_confidence(model, X)
                    
                except Exception as e:
                    logger.error(f"Prediction failed for {model_name}: {e}")
            
            # If no models available, use technical analysis
            if not predictions:
                predictions, confidence_scores = self.technical_analysis_prediction(data, timeframe)
            
            # Calculate ensemble prediction
            if len(predictions) > 1:
                weights = np.array(list(confidence_scores.values()))
                prices = np.array(list(predictions.values()))
                
                if weights.sum() > 0:
                    final_prediction = np.average(prices, weights=weights)
                else:
                    final_prediction = np.mean(prices)
            else:
                final_prediction = list(predictions.values())[0] if predictions else current_price
            
            # Calculate metrics
            price_change = final_prediction - current_price
            price_change_pct = (price_change / current_price) * 100
            
            # Determine recommendation
            if price_change_pct > 2:
                recommendation = "STRONG BUY"
            elif price_change_pct > 0.5:
                recommendation = "BUY"
            elif price_change_pct < -2:
                recommendation = "STRONG SELL"
            elif price_change_pct < -0.5:
                recommendation = "SELL"
            else:
                recommendation = "HOLD"
            
            return {
                "symbol": symbol,
                "current_price": current_price,
                "predicted_price": final_prediction,
                "price_change": price_change,
                "price_change_pct": price_change_pct,
                "confidence": np.mean(list(confidence_scores.values())) if confidence_scores else 0.5,
                "recommendation": recommendation,
                "model_predictions": predictions,
                "confidence_scores": confidence_scores,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return {"error": str(e)}
    
    def fetch_data(self, symbol: str, timeframe: str) -> pd.DataFrame:
        """Fetch historical data"""
        period_map = {
            "1d": "1mo",
            "1w": "3mo",
            "1m": "6mo",
            "3m": "1y",
            "1y": "2y"
        }
        
        period = period_map.get(timeframe, "3mo")
        
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period)
        
        return data
    
    def calculate_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical features"""
        df = data.copy()
        
        # Price features
        df['returns'] = df['Close'].pct_change()
        df['log_returns'] = np.log(df['Close'] / df['Close'].shift(1))
        
        # Moving averages
        for period in [5, 10, 20, 50]:
            df[f'sma_{period}'] = df['Close'].rolling(period).mean()
            df[f'sma_ratio_{period}'] = df['Close'] / df[f'sma_{period}']
        
        # RSI
        delta = df['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = -delta.where(delta < 0, 0).rolling(14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        ema_12 = df['Close'].ewm(span=12).mean()
        ema_26 = df['Close'].ewm(span=26).mean()
        df['macd'] = ema_12 - ema_26
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        
        # Volatility
        df['volatility'] = df['returns'].rolling(20).std()
        
        # Volume features
        df['volume_ratio'] = df['Volume'] / df['Volume'].rolling(20).mean()
        
        # Fill NaN values
        df = df.fillna(method='ffill').fillna(0)
        
        return df
    
    def estimate_confidence(self, model, X) -> float:
        """Estimate prediction confidence"""
        # Simple confidence estimation
        # In practice, use model-specific methods
        
        try:
            # For ensemble models, use prediction variance
            if hasattr(model, 'predict_proba'):
                proba = model.predict_proba(X)
                confidence = np.max(proba)
            elif hasattr(model, 'feature_importances_'):
                # For tree-based models
                confidence = 0.6 + min(0.3, np.std(model.feature_importances_))
            else:
                # Default confidence
                confidence = 0.65
                
            return float(confidence)
            
        except:
            return 0.5
    
    def technical_analysis_prediction(self, data: pd.DataFrame, timeframe: str) -> tuple:
        """Fallback prediction using technical analysis"""
        
        current_price = float(data['Close'].iloc[-1])
        
        # Calculate indicators
        sma_20 = data['Close'].rolling(20).mean().iloc[-1]
        sma_50 = data['Close'].rolling(50).mean().iloc[-1] if len(data) >= 50 else sma_20
        
        # RSI
        delta = data['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = -delta.where(delta < 0, 0).rolling(14).mean()
        rs = gain / loss
        rsi = (100 - (100 / (1 + rs))).iloc[-1]
        
        # Trend analysis
        trend_strength = (current_price - sma_50) / sma_50 if sma_50 > 0 else 0
        
        # Generate prediction based on indicators
        timeframe_multipliers = {
            "1d": 0.01,
            "1w": 0.025,
            "1m": 0.05,
            "3m": 0.12,
            "1y": 0.25
        }
        
        multiplier = timeframe_multipliers.get(timeframe, 0.025)
        
        # Calculate expected change
        if rsi > 70:  # Overbought
            expected_change = -multiplier * 0.5
        elif rsi < 30:  # Oversold
            expected_change = multiplier * 0.5
        else:
            expected_change = trend_strength * multiplier
        
        predicted_price = current_price * (1 + expected_change)
        
        # Confidence based on trend clarity
        confidence = 0.5 + min(abs(trend_strength), 0.3)
        
        predictions = {"technical_analysis": predicted_price}
        confidence_scores = {"technical_analysis": confidence}
        
        return predictions, confidence_scores