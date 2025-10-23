#!/usr/bin/env python3
"""
Phase 3 Component P3_004: Real-Time Performance Monitoring
=========================================================

Live model performance tracking with automatic model updates and retraining triggers.
Implements real-time accuracy tracking, performance degradation detection,
and dynamic weight adjustment based on live performance metrics.

Target: Real-time accuracy tracking and weight adjustment
Dependencies: All Phase 2 advanced models (P2_001-P2_004)
"""

import numpy as np
import pandas as pd
import logging
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Callable
from collections import deque, defaultdict
from dataclasses import dataclass, asdict
from threading import Lock
import warnings
warnings.filterwarnings('ignore')

@dataclass
class PredictionRecord:
    """Data class for storing individual prediction records."""
    timestamp: datetime
    model_name: str
    symbol: str
    prediction: float
    confidence: float
    actual_outcome: Optional[float] = None
    error: Optional[float] = None
    absolute_error: Optional[float] = None
    directional_accuracy: Optional[bool] = None
    regime: Optional[str] = None
    timeframe: str = '5d'

@dataclass
class PerformanceMetrics:
    """Data class for storing aggregated performance metrics."""
    model_name: str
    window_size: int
    mean_error: float
    mean_absolute_error: float
    root_mean_squared_error: float
    directional_accuracy: float
    confidence_calibration: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    last_updated: datetime

class RealtimePerformanceMonitor:
    """
    Real-Time Performance Monitoring system.
    
    Provides:
    - Live prediction tracking and outcome recording
    - Real-time performance metric calculation
    - Performance degradation detection and alerting
    - Automatic model weight adjustment
    - Model retraining trigger detection
    - Performance dashboard data
    """
    
    def __init__(self, config: Dict = None):
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.config = config or {}
        self.db_path = self.config.get('db_path', 'performance_monitoring.db')
        self.max_memory_records = self.config.get('max_memory_records', 10000)
        self.performance_windows = self.config.get('performance_windows', [10, 50, 100, 500])
        self.alert_thresholds = self.config.get('alert_thresholds', {
            'accuracy_drop': 0.15,  # 15% drop in accuracy triggers alert
            'error_increase': 0.5,   # 50% increase in error triggers alert
            'confidence_miscalibration': 0.3  # 30% miscalibration triggers alert
        })
        
        # In-memory storage for fast access
        self.prediction_records = deque(maxlen=self.max_memory_records)
        self.performance_cache = {}  # Cache for frequently accessed metrics
        self.model_weights = {}      # Dynamic model weights
        self.baseline_performance = {}  # Baseline performance for degradation detection
        
        # Thread safety
        self.lock = Lock()
        
        # Performance tracking by model and timeframe
        self.model_performance = defaultdict(lambda: defaultdict(list))
        self.real_time_metrics = {}
        
        # Alert system
        self.alerts = deque(maxlen=1000)
        self.alert_callbacks = []
        
        # Retraining triggers
        self.retraining_thresholds = {
            'min_performance_drop': 0.2,  # 20% drop from baseline
            'min_samples_since_retrain': 100,
            'max_days_since_retrain': 30
        }
        self.last_retraining = {}
        
        # Initialize database
        self._initialize_database()
        
        self.logger.info("📊 Phase 3 Real-Time Performance Monitoring initialized")
    
    def _initialize_database(self) -> None:
        """Initialize SQLite database for persistent storage."""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Predictions table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS predictions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        model_name TEXT NOT NULL,
                        symbol TEXT NOT NULL,
                        prediction REAL NOT NULL,
                        confidence REAL NOT NULL,
                        actual_outcome REAL,
                        error REAL,
                        absolute_error REAL,
                        directional_accuracy INTEGER,
                        regime TEXT,
                        timeframe TEXT DEFAULT '5d'
                    )
                """)
                
                # Performance metrics table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS performance_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        model_name TEXT NOT NULL,
                        window_size INTEGER NOT NULL,
                        mean_error REAL,
                        mean_absolute_error REAL,
                        root_mean_squared_error REAL,
                        directional_accuracy REAL,
                        confidence_calibration REAL,
                        sharpe_ratio REAL,
                        max_drawdown REAL,
                        win_rate REAL
                    )
                """)
                
                # Model weights table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS model_weights (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        model_name TEXT NOT NULL,
                        weight REAL NOT NULL,
                        regime TEXT,
                        reason TEXT
                    )
                """)
                
                # Alerts table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS alerts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        alert_type TEXT NOT NULL,
                        model_name TEXT,
                        severity TEXT NOT NULL,
                        message TEXT NOT NULL,
                        metrics TEXT
                    )
                """)
                
                # Create indexes for performance
                conn.execute("CREATE INDEX IF NOT EXISTS idx_predictions_model_time ON predictions(model_name, timestamp)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_predictions_symbol ON predictions(symbol)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_performance_model ON performance_metrics(model_name)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts(timestamp)")
                
                conn.commit()
                
        except sqlite3.Error as e:
            self.logger.error(f"Database initialization failed: {e}")
    
    def record_prediction(self, model_name: str, symbol: str, prediction: float,
                         confidence: float, regime: str = None, 
                         timeframe: str = '5d') -> str:
        """Record a new prediction for monitoring."""
        
        try:
            with self.lock:
                # Create prediction record
                record = PredictionRecord(
                    timestamp=datetime.now(),
                    model_name=model_name,
                    symbol=symbol,
                    prediction=prediction,
                    confidence=confidence,
                    regime=regime,
                    timeframe=timeframe
                )
                
                # Add to memory storage
                self.prediction_records.append(record)
                
                # Store in database
                record_id = self._store_prediction_to_db(record)
                
                # Clear relevant cache entries
                self._invalidate_performance_cache(model_name)
                
                self.logger.debug(f"Recorded prediction: {model_name} -> {symbol}: {prediction:.4f}")
                
                return record_id
                
        except Exception as e:
            self.logger.error(f"Failed to record prediction: {e}")
            return None
    
    def record_outcome(self, model_name: str, symbol: str, actual_outcome: float,
                      prediction_timestamp: datetime = None, 
                      timeframe: str = '5d') -> bool:
        """Record actual outcome and calculate performance metrics."""
        
        try:
            with self.lock:
                # Find matching prediction
                matching_record = self._find_matching_prediction(
                    model_name, symbol, prediction_timestamp, timeframe
                )
                
                if matching_record is None:
                    self.logger.warning(f"No matching prediction found for {model_name}-{symbol}")
                    return False
                
                # Calculate performance metrics
                error = matching_record.prediction - actual_outcome
                abs_error = abs(error)
                directional_accuracy = (
                    (matching_record.prediction > 0 and actual_outcome > 0) or
                    (matching_record.prediction <= 0 and actual_outcome <= 0)
                )
                
                # Update record
                matching_record.actual_outcome = actual_outcome
                matching_record.error = error
                matching_record.absolute_error = abs_error
                matching_record.directional_accuracy = directional_accuracy
                
                # Update database
                self._update_prediction_outcome_in_db(matching_record)
                
                # Update real-time metrics
                self._update_realtime_metrics(model_name, matching_record)
                
                # Check for performance degradation
                self._check_performance_degradation(model_name)
                
                # Update model weights if needed
                self._update_model_weights_if_needed(model_name)
                
                self.logger.debug(f"Recorded outcome: {model_name} error={error:.4f}, "
                                f"directional={directional_accuracy}")
                
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to record outcome: {e}")
            return False
    
    def _find_matching_prediction(self, model_name: str, symbol: str,
                                timestamp: datetime = None, 
                                timeframe: str = '5d') -> Optional[PredictionRecord]:
        """Find matching prediction record for outcome."""
        
        # If no timestamp provided, find most recent prediction
        if timestamp is None:
            for record in reversed(self.prediction_records):
                if (record.model_name == model_name and 
                    record.symbol == symbol and 
                    record.timeframe == timeframe and
                    record.actual_outcome is None):
                    return record
        else:
            # Find prediction within time window
            time_window = timedelta(hours=1)  # 1-hour matching window
            
            for record in reversed(self.prediction_records):
                if (record.model_name == model_name and
                    record.symbol == symbol and
                    record.timeframe == timeframe and
                    abs(record.timestamp - timestamp) <= time_window and
                    record.actual_outcome is None):
                    return record
        
        return None
    
    def _update_realtime_metrics(self, model_name: str, record: PredictionRecord) -> None:
        """Update real-time performance metrics."""
        
        # Get recent records for this model
        recent_records = [r for r in self.prediction_records 
                         if (r.model_name == model_name and 
                             r.actual_outcome is not None)]
        
        if len(recent_records) < 2:
            return
        
        # Calculate metrics for different windows
        for window_size in self.performance_windows:
            if len(recent_records) >= window_size:
                window_records = recent_records[-window_size:]
                metrics = self._calculate_performance_metrics(window_records, window_size)
                
                # Store in cache
                cache_key = f"{model_name}_w{window_size}"
                self.performance_cache[cache_key] = metrics
                
                # Store in database periodically
                if window_size == 50:  # Store medium-term metrics
                    self._store_performance_metrics_to_db(metrics)
    
    def _calculate_performance_metrics(self, records: List[PredictionRecord], 
                                     window_size: int) -> PerformanceMetrics:
        """Calculate performance metrics from a list of records."""
        
        if not records:
            return None
        
        model_name = records[0].model_name
        errors = [r.error for r in records if r.error is not None]
        abs_errors = [r.absolute_error for r in records if r.absolute_error is not None]
        directional = [r.directional_accuracy for r in records if r.directional_accuracy is not None]
        predictions = [r.prediction for r in records]
        outcomes = [r.actual_outcome for r in records if r.actual_outcome is not None]
        confidences = [r.confidence for r in records]
        
        # Basic metrics
        mean_error = np.mean(errors) if errors else 0.0
        mean_abs_error = np.mean(abs_errors) if abs_errors else 0.0
        rmse = np.sqrt(np.mean([e**2 for e in errors])) if errors else 0.0
        directional_accuracy = np.mean(directional) if directional else 0.5
        
        # Confidence calibration (simplified)
        confidence_calibration = self._calculate_confidence_calibration(
            predictions, outcomes, confidences
        )
        
        # Sharpe ratio (simplified)
        if outcomes:
            returns = np.array(outcomes)
            sharpe_ratio = np.mean(returns) / (np.std(returns) + 1e-8) if len(returns) > 1 else 0.0
        else:
            sharpe_ratio = 0.0
        
        # Max drawdown
        max_drawdown = self._calculate_max_drawdown(outcomes) if outcomes else 0.0
        
        # Win rate
        win_rate = np.mean([o > 0 for o in outcomes]) if outcomes else 0.5
        
        return PerformanceMetrics(
            model_name=model_name,
            window_size=window_size,
            mean_error=mean_error,
            mean_absolute_error=mean_abs_error,
            root_mean_squared_error=rmse,
            directional_accuracy=directional_accuracy,
            confidence_calibration=confidence_calibration,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            win_rate=win_rate,
            last_updated=datetime.now()
        )
    
    def _calculate_confidence_calibration(self, predictions: List[float], 
                                        outcomes: List[float], 
                                        confidences: List[float]) -> float:
        """Calculate confidence calibration score."""
        
        if not predictions or not outcomes or not confidences:
            return 0.5
        
        try:
            # Simplified calibration: correlation between confidence and accuracy
            accuracies = [1.0 if abs(p - o) < 0.02 else 0.0 
                         for p, o in zip(predictions, outcomes)]
            
            if len(accuracies) > 5:
                correlation = np.corrcoef(confidences, accuracies)[0, 1]
                return abs(correlation) if not np.isnan(correlation) else 0.5
            else:
                return 0.5
                
        except Exception:
            return 0.5
    
    def _calculate_max_drawdown(self, returns: List[float]) -> float:
        """Calculate maximum drawdown from returns."""
        
        if not returns or len(returns) < 2:
            return 0.0
        
        cumulative = np.cumsum(returns)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = cumulative - running_max
        
        return abs(np.min(drawdown)) if len(drawdown) > 0 else 0.0
    
    def _check_performance_degradation(self, model_name: str) -> None:
        """Check for performance degradation and trigger alerts."""
        
        try:
            # Get current performance
            current_metrics = self.get_current_performance(model_name, window=50)
            if not current_metrics:
                return
            
            # Get baseline performance
            baseline = self.baseline_performance.get(model_name)
            if not baseline:
                # Set current as baseline if none exists
                self.baseline_performance[model_name] = current_metrics
                return
            
            # Check for degradation
            accuracy_drop = (baseline.directional_accuracy - 
                           current_metrics.directional_accuracy)
            error_increase = (current_metrics.mean_absolute_error / 
                            (baseline.mean_absolute_error + 1e-8) - 1)
            confidence_miscal = abs(current_metrics.confidence_calibration - 
                                  baseline.confidence_calibration)
            
            alerts_triggered = []
            
            if accuracy_drop > self.alert_thresholds['accuracy_drop']:
                alerts_triggered.append({
                    'type': 'accuracy_degradation',
                    'severity': 'high',
                    'message': f"Accuracy dropped by {accuracy_drop:.1%}",
                    'metrics': {'drop': accuracy_drop, 'current': current_metrics.directional_accuracy}
                })
            
            if error_increase > self.alert_thresholds['error_increase']:
                alerts_triggered.append({
                    'type': 'error_increase',
                    'severity': 'medium',
                    'message': f"Error increased by {error_increase:.1%}",
                    'metrics': {'increase': error_increase, 'current': current_metrics.mean_absolute_error}
                })
            
            if confidence_miscal > self.alert_thresholds['confidence_miscalibration']:
                alerts_triggered.append({
                    'type': 'confidence_miscalibration',
                    'severity': 'medium',
                    'message': f"Confidence miscalibration: {confidence_miscal:.3f}",
                    'metrics': {'miscalibration': confidence_miscal}
                })
            
            # Process alerts
            for alert in alerts_triggered:
                self._trigger_alert(model_name, alert)
                
        except Exception as e:
            self.logger.error(f"Performance degradation check failed: {e}")
    
    def _trigger_alert(self, model_name: str, alert: Dict[str, Any]) -> None:
        """Trigger performance alert."""
        
        alert_record = {
            'timestamp': datetime.now(),
            'model_name': model_name,
            'alert_type': alert['type'],
            'severity': alert['severity'],
            'message': alert['message'],
            'metrics': alert['metrics']
        }
        
        # Add to memory
        self.alerts.append(alert_record)
        
        # Store in database
        self._store_alert_to_db(alert_record)
        
        # Call registered callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert_record)
            except Exception as e:
                self.logger.error(f"Alert callback failed: {e}")
        
        self.logger.warning(f"ALERT [{alert['severity']}] {model_name}: {alert['message']}")
    
    def _update_model_weights_if_needed(self, model_name: str) -> None:
        """Update model weights based on recent performance."""
        
        try:
            # Get recent performance for all models
            all_performances = {}
            for record in self.prediction_records:
                if record.actual_outcome is not None:
                    model = record.model_name
                    if model not in all_performances:
                        perf = self.get_current_performance(model, window=20)
                        if perf:
                            all_performances[model] = perf.directional_accuracy
            
            if len(all_performances) > 1:
                # Calculate performance-based weights
                total_performance = sum(all_performances.values())
                if total_performance > 0:
                    new_weights = {model: perf / total_performance 
                                 for model, perf in all_performances.items()}
                    
                    # Update weights
                    for model, weight in new_weights.items():
                        old_weight = self.model_weights.get(model, 0.25)
                        # Smooth weight updates
                        smoothed_weight = 0.7 * old_weight + 0.3 * weight
                        self.model_weights[model] = smoothed_weight
                        
                        # Store weight change
                        self._store_model_weight_to_db(model, smoothed_weight, "performance_update")
                        
        except Exception as e:
            self.logger.error(f"Model weight update failed: {e}")
    
    def get_current_performance(self, model_name: str, window: int = 50) -> Optional[PerformanceMetrics]:
        """Get current performance metrics for a model."""
        
        # Check cache first
        cache_key = f"{model_name}_w{window}"
        if cache_key in self.performance_cache:
            return self.performance_cache[cache_key]
        
        # Calculate from records
        model_records = [r for r in self.prediction_records 
                        if (r.model_name == model_name and 
                            r.actual_outcome is not None)]
        
        if len(model_records) >= min(window, 5):
            recent_records = model_records[-window:]
            metrics = self._calculate_performance_metrics(recent_records, window)
            
            # Cache result
            self.performance_cache[cache_key] = metrics
            return metrics
        
        return None
    
    def get_model_weights(self, regime: str = None) -> Dict[str, float]:
        """Get current dynamic model weights."""
        
        if not self.model_weights:
            # Default equal weights if no performance data
            return {'default': 1.0}
        
        # Apply regime-specific adjustments if provided
        weights = self.model_weights.copy()
        
        if regime and regime in ['Bull', 'Bear', 'Sideways']:
            # Simple regime-based adjustments
            regime_adjustments = {
                'Bull': {'momentum': 1.2, 'technical': 0.9},
                'Bear': {'momentum': 0.8, 'fundamental': 1.2},
                'Sideways': {'sentiment': 1.1, 'technical': 1.1}
            }
            
            if regime in regime_adjustments:
                for model_name in weights:
                    for model_type, adj in regime_adjustments[regime].items():
                        if model_type in model_name.lower():
                            weights[model_name] *= adj
            
            # Renormalize
            total_weight = sum(weights.values())
            if total_weight > 0:
                for model in weights:
                    weights[model] /= total_weight
        
        return weights
    
    def get_performance_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive performance data for dashboard."""
        
        dashboard_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_predictions': len(self.prediction_records),
                'models_tracked': len(set(r.model_name for r in self.prediction_records)),
                'recent_alerts': len([a for a in self.alerts 
                                    if a['timestamp'] > datetime.now() - timedelta(hours=24)])
            },
            'model_performance': {},
            'recent_alerts': list(self.alerts)[-10:],  # Last 10 alerts
            'model_weights': self.get_model_weights(),
            'performance_trends': {}
        }
        
        # Get performance for each model
        tracked_models = set(r.model_name for r in self.prediction_records)
        for model_name in tracked_models:
            performance = self.get_current_performance(model_name)
            if performance:
                dashboard_data['model_performance'][model_name] = asdict(performance)
        
        # Performance trends (last 100 predictions)
        for model_name in tracked_models:
            model_records = [r for r in self.prediction_records 
                           if r.model_name == model_name and r.actual_outcome is not None]
            
            if len(model_records) >= 20:
                recent_records = model_records[-100:]
                
                # Calculate sliding window accuracy
                window_accuracies = []
                for i in range(10, len(recent_records), 10):
                    window = recent_records[i-10:i]
                    accuracy = np.mean([r.directional_accuracy for r in window 
                                      if r.directional_accuracy is not None])
                    window_accuracies.append(accuracy)
                
                dashboard_data['performance_trends'][model_name] = window_accuracies
        
        return dashboard_data
    
    def check_retraining_needed(self, model_name: str) -> Dict[str, Any]:
        """Check if model retraining is recommended."""
        
        try:
            current_performance = self.get_current_performance(model_name, window=100)
            if not current_performance:
                return {'retraining_needed': False, 'reason': 'insufficient_data'}
            
            baseline = self.baseline_performance.get(model_name)
            if not baseline:
                return {'retraining_needed': False, 'reason': 'no_baseline'}
            
            # Check performance drop
            performance_drop = baseline.directional_accuracy - current_performance.directional_accuracy
            
            # Check time since last retrain
            last_retrain = self.last_retraining.get(model_name, datetime.now() - timedelta(days=365))
            days_since_retrain = (datetime.now() - last_retrain).days
            
            # Count samples since last retrain
            samples_since_retrain = len([r for r in self.prediction_records
                                       if (r.model_name == model_name and 
                                           r.timestamp > last_retrain and
                                           r.actual_outcome is not None)])
            
            retraining_needed = (
                performance_drop > self.retraining_thresholds['min_performance_drop'] or
                days_since_retrain > self.retraining_thresholds['max_days_since_retrain'] or
                samples_since_retrain > self.retraining_thresholds['min_samples_since_retrain']
            )
            
            return {
                'retraining_needed': retraining_needed,
                'performance_drop': performance_drop,
                'days_since_retrain': days_since_retrain,
                'samples_since_retrain': samples_since_retrain,
                'current_accuracy': current_performance.directional_accuracy,
                'baseline_accuracy': baseline.directional_accuracy,
                'recommendation': 'retrain_immediately' if retraining_needed else 'continue_monitoring'
            }
            
        except Exception as e:
            self.logger.error(f"Retraining check failed: {e}")
            return {'retraining_needed': False, 'error': str(e)}
    
    def register_alert_callback(self, callback: Callable) -> None:
        """Register callback function for alerts."""
        self.alert_callbacks.append(callback)
    
    def _invalidate_performance_cache(self, model_name: str) -> None:
        """Invalidate cached performance metrics for a model."""
        keys_to_remove = [key for key in self.performance_cache.keys() 
                         if key.startswith(model_name)]
        for key in keys_to_remove:
            del self.performance_cache[key]
    
    # Database operations
    def _store_prediction_to_db(self, record: PredictionRecord) -> str:
        """Store prediction record to database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    INSERT INTO predictions 
                    (timestamp, model_name, symbol, prediction, confidence, regime, timeframe)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    record.timestamp.isoformat(),
                    record.model_name,
                    record.symbol,
                    record.prediction,
                    record.confidence,
                    record.regime,
                    record.timeframe
                ))
                return str(cursor.lastrowid)
        except sqlite3.Error as e:
            self.logger.error(f"Database storage failed: {e}")
            return None
    
    def _update_prediction_outcome_in_db(self, record: PredictionRecord) -> None:
        """Update prediction record with outcome in database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE predictions 
                    SET actual_outcome = ?, error = ?, absolute_error = ?, directional_accuracy = ?
                    WHERE model_name = ? AND symbol = ? AND timestamp = ? AND timeframe = ?
                """, (
                    record.actual_outcome,
                    record.error,
                    record.absolute_error,
                    1 if record.directional_accuracy else 0,
                    record.model_name,
                    record.symbol,
                    record.timestamp.isoformat(),
                    record.timeframe
                ))
        except sqlite3.Error as e:
            self.logger.error(f"Database update failed: {e}")
    
    def _store_performance_metrics_to_db(self, metrics: PerformanceMetrics) -> None:
        """Store performance metrics to database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO performance_metrics 
                    (timestamp, model_name, window_size, mean_error, mean_absolute_error,
                     root_mean_squared_error, directional_accuracy, confidence_calibration,
                     sharpe_ratio, max_drawdown, win_rate)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    metrics.last_updated.isoformat(),
                    metrics.model_name,
                    metrics.window_size,
                    metrics.mean_error,
                    metrics.mean_absolute_error,
                    metrics.root_mean_squared_error,
                    metrics.directional_accuracy,
                    metrics.confidence_calibration,
                    metrics.sharpe_ratio,
                    metrics.max_drawdown,
                    metrics.win_rate
                ))
        except sqlite3.Error as e:
            self.logger.error(f"Performance metrics storage failed: {e}")
    
    def _store_model_weight_to_db(self, model_name: str, weight: float, reason: str) -> None:
        """Store model weight change to database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO model_weights (timestamp, model_name, weight, reason)
                    VALUES (?, ?, ?, ?)
                """, (
                    datetime.now().isoformat(),
                    model_name,
                    weight,
                    reason
                ))
        except sqlite3.Error as e:
            self.logger.error(f"Model weight storage failed: {e}")
    
    def _store_alert_to_db(self, alert: Dict[str, Any]) -> None:
        """Store alert to database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO alerts (timestamp, alert_type, model_name, severity, message, metrics)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    alert['timestamp'].isoformat(),
                    alert['alert_type'],
                    alert.get('model_name'),
                    alert['severity'],
                    alert['message'],
                    json.dumps(alert.get('metrics', {}))
                ))
        except sqlite3.Error as e:
            self.logger.error(f"Alert storage failed: {e}")

# Integration function for existing system
def create_phase3_performance_monitor(config: Dict = None) -> RealtimePerformanceMonitor:
    """Create and initialize Phase 3 Real-Time Performance Monitoring system."""
    monitor = RealtimePerformanceMonitor(config)
    
    logging.info(f"📊 P3_004 Real-Time Performance Monitor initialized")
    
    return monitor

if __name__ == "__main__":
    # Test implementation
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Test the Real-Time Performance Monitoring system
    logger.info("🧪 Testing P3_004 Real-Time Performance Monitoring...")
    
    # Create performance monitor
    monitor = create_phase3_performance_monitor({
        'db_path': 'test_performance.db',
        'max_memory_records': 1000
    })
    
    # Register alert callback
    def alert_callback(alert):
        logger.info(f"🚨 ALERT: {alert['message']}")
    
    monitor.register_alert_callback(alert_callback)
    
    # Simulate prediction and outcome cycle
    np.random.seed(42)
    
    models = ['lstm_model', 'rf_model', 'quantile_model']
    symbols = ['CBA.AX', 'BHP.AX', 'ANZ.AX']
    
    logger.info("🔄 Simulating prediction-outcome cycles...")
    
    for i in range(100):
        # Record predictions
        for model in models:
            symbol = np.random.choice(symbols)
            
            # Simulate different model performance characteristics
            if model == 'lstm_model':
                prediction = np.random.normal(0.02, 0.03)
                confidence = np.random.uniform(0.6, 0.9)
            elif model == 'rf_model':
                prediction = np.random.normal(0.01, 0.025)
                confidence = np.random.uniform(0.5, 0.8)
            else:  # quantile_model
                prediction = np.random.normal(0.015, 0.02)
                confidence = np.random.uniform(0.7, 0.95)
            
            # Record prediction
            monitor.record_prediction(model, symbol, prediction, confidence, 'Bull_Medium_Vol')
        
        # Record outcomes (simulate delay)
        if i > 5:  # Start recording outcomes after some predictions
            for model in models:
                symbol = np.random.choice(symbols)
                
                # Simulate actual outcome with model-specific accuracy
                base_outcome = np.random.normal(0.018, 0.04)
                if model == 'lstm_model' and np.random.random() > 0.3:
                    # LSTM has 70% accuracy
                    outcome = base_outcome + np.random.normal(0, 0.01)
                elif model == 'rf_model' and np.random.random() > 0.4:
                    # RF has 60% accuracy  
                    outcome = base_outcome + np.random.normal(0, 0.015)
                else:
                    # Quantile has 75% accuracy
                    outcome = base_outcome + np.random.normal(0, 0.008)
                
                monitor.record_outcome(model, symbol, outcome)
        
        # Check performance every 20 iterations
        if i > 0 and i % 20 == 0:
            logger.info(f"\n📊 Performance Check at iteration {i}:")
            
            for model in models:
                performance = monitor.get_current_performance(model, window=20)
                if performance:
                    logger.info(f"   {model}: {performance.directional_accuracy:.1%} accuracy, "
                               f"MAE: {performance.mean_absolute_error:.4f}")
                
                # Check retraining recommendation
                retrain_check = monitor.check_retraining_needed(model)
                if retrain_check.get('retraining_needed'):
                    logger.info(f"   🔄 {model}: Retraining recommended - {retrain_check['recommendation']}")
    
    # Get final dashboard data
    dashboard = monitor.get_performance_dashboard_data()
    logger.info("\n📋 Final Performance Dashboard Summary:")
    logger.info(f"   Total predictions: {dashboard['summary']['total_predictions']}")
    logger.info(f"   Models tracked: {dashboard['summary']['models_tracked']}")
    logger.info(f"   Recent alerts: {dashboard['summary']['recent_alerts']}")
    
    # Model weights
    weights = monitor.get_model_weights()
    logger.info("🎯 Final Model Weights:")
    for model, weight in weights.items():
        logger.info(f"   {model}: {weight:.3f}")
    
    logger.info("🎉 P3_004 Real-Time Performance Monitoring test completed successfully!")