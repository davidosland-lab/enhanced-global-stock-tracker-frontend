"""
Cloud API Client for integration with online prediction center
"""

import requests
import json
from typing import Dict, Any, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class CloudClient:
    """Client for communicating with cloud prediction API"""
    
    def __init__(self, api_url: str):
        self.api_url = api_url
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
    def test_connection(self) -> bool:
        """Test connection to cloud API"""
        try:
            response = self.session.get(f"{self.api_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def predict(self, symbol: str, timeframe: str, model: str) -> Dict[str, Any]:
        """Get prediction from cloud API"""
        try:
            params = {
                "timeframe": timeframe,
                "include_gnn": True,
                "include_ensemble": True
            }
            
            response = self.session.get(
                f"{self.api_url}/api/unified-prediction/{symbol}",
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract and format prediction
                pred_engine = data.get("predictions", {}).get("prediction_engine", {})
                
                return {
                    "symbol": symbol,
                    "current_price": pred_engine.get("current_price"),
                    "predicted_price": pred_engine.get("final_prediction"),
                    "price_change_pct": pred_engine.get("price_change_percent"),
                    "confidence": self._calculate_avg_confidence(pred_engine.get("confidence_scores", {})),
                    "trend": pred_engine.get("trend"),
                    "recommendation": self._get_recommendation(pred_engine.get("price_change_percent", 0)),
                    "model_predictions": pred_engine.get("models", {}),
                    "technical_indicators": pred_engine.get("technical_indicators", {}),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"error": f"API error: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Cloud prediction failed: {e}")
            return {"error": str(e)}
    
    def upload_backtest(self, result: Dict[str, Any]) -> bool:
        """Upload backtest results to cloud"""
        try:
            # Format result for upload
            upload_data = {
                "symbol": result.get("symbol"),
                "strategy": result.get("strategy"),
                "period": {
                    "start": result.get("start_date"),
                    "end": result.get("end_date")
                },
                "metrics": {
                    "total_return": result.get("total_return"),
                    "sharpe_ratio": result.get("sharpe_ratio"),
                    "max_drawdown": result.get("max_drawdown"),
                    "win_rate": result.get("win_rate")
                },
                "source": "desktop_app",
                "timestamp": datetime.now().isoformat()
            }
            
            # Send to cloud
            response = self.session.post(
                f"{self.api_url}/api/backtest-results",
                json=upload_data,
                timeout=10
            )
            
            return response.status_code in [200, 201]
            
        except Exception as e:
            logger.error(f"Failed to upload backtest: {e}")
            return False
    
    def upload_model(self, model_path: str, metadata: Dict[str, Any]) -> bool:
        """Upload trained model to cloud"""
        try:
            with open(model_path, 'rb') as f:
                files = {'model': f}
                data = {'metadata': json.dumps(metadata)}
                
                response = self.session.post(
                    f"{self.api_url}/api/upload-model",
                    files=files,
                    data=data,
                    timeout=60
                )
                
                return response.status_code in [200, 201]
                
        except Exception as e:
            logger.error(f"Failed to upload model: {e}")
            return False
    
    def download_model(self, symbol: str, model_type: str, save_path: str) -> bool:
        """Download model from cloud"""
        try:
            response = self.session.get(
                f"{self.api_url}/api/models/{symbol}/{model_type}",
                timeout=60
            )
            
            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Failed to download model: {e}")
            return False
    
    def sync_training_data(self, symbol: str, data: pd.DataFrame) -> bool:
        """Sync training data with cloud"""
        try:
            # Convert dataframe to JSON
            data_json = data.to_json(orient='split')
            
            response = self.session.post(
                f"{self.api_url}/api/training-data/{symbol}",
                json={"data": data_json},
                timeout=30
            )
            
            return response.status_code in [200, 201]
            
        except Exception as e:
            logger.error(f"Failed to sync training data: {e}")
            return False
    
    def get_model_performance(self, symbol: str) -> Dict[str, Any]:
        """Get model performance metrics from cloud"""
        try:
            response = self.session.get(
                f"{self.api_url}/api/model-performance/{symbol}",
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            
            return {"error": f"API error: {response.status_code}"}
            
        except Exception as e:
            logger.error(f"Failed to get model performance: {e}")
            return {"error": str(e)}
    
    def _calculate_avg_confidence(self, confidence_scores: Dict[str, float]) -> float:
        """Calculate average confidence from scores"""
        if not confidence_scores:
            return 0.5
        
        values = [v for v in confidence_scores.values() if isinstance(v, (int, float))]
        return sum(values) / len(values) if values else 0.5
    
    def _get_recommendation(self, price_change_pct: float) -> str:
        """Get recommendation based on price change"""
        if price_change_pct > 2:
            return "STRONG BUY"
        elif price_change_pct > 0.5:
            return "BUY"
        elif price_change_pct < -2:
            return "STRONG SELL"
        elif price_change_pct < -0.5:
            return "SELL"
        else:
            return "HOLD"