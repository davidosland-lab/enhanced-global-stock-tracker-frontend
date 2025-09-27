"""
Performance Monitoring System for Prediction Models
Tracks accuracy, monitors drift, and provides real-time metrics
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from collections import deque, defaultdict
import numpy as np
import pandas as pd
import asyncio
from pathlib import Path

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Monitor and track prediction model performance"""
    
    def __init__(self, storage_path: str = "./performance_data"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        # In-memory metrics storage
        self.predictions_history = deque(maxlen=1000)
        self.model_metrics = defaultdict(lambda: {
            'total_predictions': 0,
            'correct_predictions': 0,
            'total_error': 0,
            'predictions': deque(maxlen=100)
        })
        
        self.accuracy_window = deque(maxlen=100)
        self.system_metrics = {
            'uptime': datetime.now(),
            'total_requests': 0,
            'failed_requests': 0,
            'average_latency': 0,
            'models_active': []
        }
        
        # Load historical data if exists
        self._load_historical_data()
    
    def track_prediction(
        self,
        symbol: str,
        prediction: float,
        confidence: float,
        model_type: str,
        actual_price: Optional[float] = None,
        metadata: Optional[Dict] = None
    ):
        """Track a new prediction"""
        prediction_record = {
            'id': f"{symbol}_{datetime.now().timestamp()}",
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'prediction': prediction,
            'confidence': confidence,
            'model_type': model_type,
            'actual_price': actual_price,
            'metadata': metadata or {}
        }
        
        # Add to history
        self.predictions_history.append(prediction_record)
        
        # Update model-specific metrics
        self.model_metrics[model_type]['total_predictions'] += 1
        self.model_metrics[model_type]['predictions'].append(prediction_record)
        
        # Update system metrics
        self.system_metrics['total_requests'] += 1
        
        # If we have actual price, calculate accuracy
        if actual_price:
            error = abs(prediction - actual_price) / actual_price
            self.model_metrics[model_type]['total_error'] += error
            
            # Track if prediction direction was correct
            if error < 0.05:  # Within 5% is considered correct
                self.model_metrics[model_type]['correct_predictions'] += 1
                self.accuracy_window.append(1)
            else:
                self.accuracy_window.append(0)
        
        # Save periodically
        if self.system_metrics['total_requests'] % 10 == 0:
            self._save_metrics()
    
    def get_model_accuracy(self, model_type: str) -> float:
        """Get accuracy for a specific model"""
        metrics = self.model_metrics[model_type]
        if metrics['total_predictions'] == 0:
            return 0.0
        
        return metrics['correct_predictions'] / metrics['total_predictions']
    
    def get_overall_accuracy(self) -> float:
        """Get overall system accuracy"""
        if not self.accuracy_window:
            return 0.0
        
        return sum(self.accuracy_window) / len(self.accuracy_window)
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        return {
            'accuracy': self.get_overall_accuracy(),
            'recent_predictions_count': len(self.predictions_history),
            'model_performance': {
                model: {
                    'accuracy': self.get_model_accuracy(model),
                    'total_predictions': metrics['total_predictions'],
                    'average_error': metrics['total_error'] / max(1, metrics['total_predictions'])
                }
                for model, metrics in self.model_metrics.items()
            },
            'system_metrics': self.system_metrics,
            'last_updated': datetime.now().isoformat()
        }
    
    def get_detailed_metrics(
        self,
        lookback_days: int = 7,
        model_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get detailed performance metrics"""
        cutoff_date = datetime.now() - timedelta(days=lookback_days)
        
        # Filter predictions by date
        recent_predictions = [
            p for p in self.predictions_history
            if datetime.fromisoformat(p['timestamp']) > cutoff_date
        ]
        
        # Filter by model type if specified
        if model_type:
            recent_predictions = [
                p for p in recent_predictions
                if p['model_type'] == model_type
            ]
        
        # Calculate statistics
        if not recent_predictions:
            return {
                'total_predictions': 0,
                'average_accuracy': 0,
                'best_model': None,
                'worst_model': None,
                'predictions': []
            }
        
        # Group by model
        model_groups = defaultdict(list)
        for pred in recent_predictions:
            model_groups[pred['model_type']].append(pred)
        
        # Calculate model performance
        model_performance = {}
        for model, preds in model_groups.items():
            confidences = [p['confidence'] for p in preds]
            model_performance[model] = {
                'count': len(preds),
                'avg_confidence': np.mean(confidences),
                'min_confidence': min(confidences),
                'max_confidence': max(confidences)
            }
        
        # Find best and worst models
        if model_performance:
            best_model = max(model_performance.items(), 
                           key=lambda x: x[1]['avg_confidence'])[0]
            worst_model = min(model_performance.items(), 
                            key=lambda x: x[1]['avg_confidence'])[0]
        else:
            best_model = worst_model = None
        
        return {
            'total_predictions': len(recent_predictions),
            'average_accuracy': self.get_overall_accuracy(),
            'best_model': best_model,
            'worst_model': worst_model,
            'model_performance': model_performance,
            'recent_predictions': recent_predictions[-10:]  # Last 10 predictions
        }
    
    def detect_model_drift(self, model_type: str, threshold: float = 0.1) -> bool:
        """Detect if a model's performance is drifting"""
        metrics = self.model_metrics[model_type]
        predictions = list(metrics['predictions'])
        
        if len(predictions) < 20:
            return False
        
        # Compare recent performance to historical
        recent = predictions[-10:]
        historical = predictions[-20:-10]
        
        recent_errors = [p.get('error', 0) for p in recent if 'error' in p]
        historical_errors = [p.get('error', 0) for p in historical if 'error' in p]
        
        if not recent_errors or not historical_errors:
            return False
        
        # Check if error has increased significantly
        recent_avg = np.mean(recent_errors)
        historical_avg = np.mean(historical_errors)
        
        drift = abs(recent_avg - historical_avg) / max(historical_avg, 0.001)
        
        return drift > threshold
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status"""
        uptime = datetime.now() - self.system_metrics['uptime']
        failure_rate = (self.system_metrics['failed_requests'] / 
                       max(1, self.system_metrics['total_requests']))
        
        # Check for model drift
        drifting_models = [
            model for model in self.model_metrics.keys()
            if self.detect_model_drift(model)
        ]
        
        # Determine health status
        if failure_rate > 0.1 or len(drifting_models) > 0:
            health_status = 'degraded'
        elif failure_rate > 0.05:
            health_status = 'warning'
        else:
            health_status = 'healthy'
        
        return {
            'status': health_status,
            'uptime_hours': uptime.total_seconds() / 3600,
            'failure_rate': failure_rate,
            'total_requests': self.system_metrics['total_requests'],
            'active_models': list(self.model_metrics.keys()),
            'drifting_models': drifting_models,
            'overall_accuracy': self.get_overall_accuracy(),
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        return {
            'summary': {
                'overall_accuracy': self.get_overall_accuracy(),
                'total_predictions': len(self.predictions_history),
                'active_models': len(self.model_metrics),
                'system_health': self.get_system_health()['status']
            },
            'model_breakdown': {
                model: {
                    'accuracy': self.get_model_accuracy(model),
                    'predictions': metrics['total_predictions'],
                    'avg_error': metrics['total_error'] / max(1, metrics['total_predictions']),
                    'is_drifting': self.detect_model_drift(model)
                }
                for model, metrics in self.model_metrics.items()
            },
            'recent_performance': self.get_detailed_metrics(lookback_days=1),
            'weekly_performance': self.get_detailed_metrics(lookback_days=7),
            'system_health': self.get_system_health(),
            'generated_at': datetime.now().isoformat()
        }
    
    def _save_metrics(self):
        """Save metrics to disk"""
        try:
            metrics_file = self.storage_path / f"metrics_{datetime.now().date()}.json"
            
            data = {
                'predictions': list(self.predictions_history)[-100:],  # Keep last 100
                'model_metrics': {
                    model: {
                        'total_predictions': metrics['total_predictions'],
                        'correct_predictions': metrics['correct_predictions'],
                        'total_error': metrics['total_error']
                    }
                    for model, metrics in self.model_metrics.items()
                },
                'system_metrics': self.system_metrics,
                'timestamp': datetime.now().isoformat()
            }
            
            with open(metrics_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")
    
    def _load_historical_data(self):
        """Load historical metrics from disk"""
        try:
            # Find most recent metrics file
            metrics_files = list(self.storage_path.glob("metrics_*.json"))
            if not metrics_files:
                return
            
            latest_file = max(metrics_files, key=lambda f: f.stat().st_mtime)
            
            with open(latest_file, 'r') as f:
                data = json.load(f)
            
            # Restore metrics
            if 'predictions' in data:
                for pred in data['predictions']:
                    self.predictions_history.append(pred)
            
            if 'model_metrics' in data:
                for model, metrics in data['model_metrics'].items():
                    self.model_metrics[model].update(metrics)
            
            if 'system_metrics' in data:
                self.system_metrics.update(data['system_metrics'])
                # Reset uptime to now
                self.system_metrics['uptime'] = datetime.now()
            
            logger.info(f"Loaded historical metrics from {latest_file}")
            
        except Exception as e:
            logger.warning(f"Could not load historical metrics: {e}")


# Global instance
performance_monitor = PerformanceMonitor()


class AlertSystem:
    """Alert system for monitoring thresholds"""
    
    def __init__(self, monitor: PerformanceMonitor):
        self.monitor = monitor
        self.alerts = deque(maxlen=100)
        self.alert_thresholds = {
            'accuracy': 0.6,  # Alert if accuracy drops below 60%
            'drift': 0.15,     # Alert if drift exceeds 15%
            'failure_rate': 0.1  # Alert if failure rate exceeds 10%
        }
    
    def check_alerts(self) -> List[Dict[str, Any]]:
        """Check for alert conditions"""
        new_alerts = []
        
        # Check accuracy
        accuracy = self.monitor.get_overall_accuracy()
        if accuracy < self.alert_thresholds['accuracy']:
            alert = {
                'type': 'accuracy',
                'severity': 'warning' if accuracy > 0.5 else 'critical',
                'message': f"Model accuracy dropped to {accuracy:.1%}",
                'timestamp': datetime.now().isoformat()
            }
            new_alerts.append(alert)
            self.alerts.append(alert)
        
        # Check for model drift
        for model in self.monitor.model_metrics.keys():
            if self.monitor.detect_model_drift(model, self.alert_thresholds['drift']):
                alert = {
                    'type': 'drift',
                    'severity': 'warning',
                    'message': f"Model '{model}' showing performance drift",
                    'timestamp': datetime.now().isoformat()
                }
                new_alerts.append(alert)
                self.alerts.append(alert)
        
        # Check system health
        health = self.monitor.get_system_health()
        if health['failure_rate'] > self.alert_thresholds['failure_rate']:
            alert = {
                'type': 'system',
                'severity': 'critical',
                'message': f"High failure rate: {health['failure_rate']:.1%}",
                'timestamp': datetime.now().isoformat()
            }
            new_alerts.append(alert)
            self.alerts.append(alert)
        
        return new_alerts
    
    def get_recent_alerts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent alerts"""
        return list(self.alerts)[-limit:]


# Global alert system
alert_system = AlertSystem(performance_monitor)


async def monitor_performance_loop():
    """Background task to continuously monitor performance"""
    while True:
        try:
            # Check for alerts
            alerts = alert_system.check_alerts()
            if alerts:
                for alert in alerts:
                    logger.warning(f"Alert: {alert['message']}")
            
            # Generate periodic report
            if datetime.now().minute == 0:  # Every hour
                report = performance_monitor.generate_performance_report()
                logger.info(f"Performance Report: Accuracy={report['summary']['overall_accuracy']:.1%}")
            
            # Sleep for 1 minute
            await asyncio.sleep(60)
            
        except Exception as e:
            logger.error(f"Performance monitoring error: {e}")
            await asyncio.sleep(60)