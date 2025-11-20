"""
Prediction Database Manager
Handles storage and retrieval of ML predictions with accuracy tracking
"""

import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
import os

logger = logging.getLogger(__name__)


class PredictionDatabase:
    """Manages prediction storage and accuracy tracking"""
    
    def __init__(self, db_path: str = "trading.db"):
        """Initialize prediction database"""
        self.db_path = db_path
        self.init_prediction_tables()
        logger.info(f"PredictionDatabase initialized with path: {db_path}")
    
    def init_prediction_tables(self):
        """Create prediction tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create predictions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                prediction_date TEXT NOT NULL,
                target_date TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                
                -- Price data at prediction time
                current_price REAL NOT NULL,
                predicted_price REAL NOT NULL,
                predicted_change_percent REAL NOT NULL,
                prediction TEXT NOT NULL,
                confidence REAL NOT NULL,
                
                -- Model information
                lstm_prediction TEXT,
                lstm_weight REAL,
                trend_prediction TEXT,
                trend_weight REAL,
                technical_prediction TEXT,
                technical_weight REAL,
                
                -- Sentiment data
                sentiment_label TEXT,
                sentiment_score REAL,
                sentiment_confidence REAL,
                article_count INTEGER,
                
                -- Actual outcome (filled after target_date)
                actual_price REAL,
                actual_change_percent REAL,
                prediction_error_percent REAL,
                prediction_correct INTEGER,
                
                -- Metadata
                status TEXT DEFAULT 'ACTIVE',
                chart_interval TEXT,
                chart_period TEXT,
                data_points_count INTEGER,
                
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                validated_at TEXT,
                
                UNIQUE(symbol, prediction_date, timeframe)
            )
        ''')
        
        # Create indexes for performance
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_predictions_symbol 
            ON predictions(symbol)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_predictions_date 
            ON predictions(prediction_date)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_predictions_status 
            ON predictions(status)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_predictions_symbol_date 
            ON predictions(symbol, prediction_date)
        ''')
        
        # Create accuracy stats table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prediction_accuracy_stats (
                stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                period_start TEXT NOT NULL,
                period_end TEXT NOT NULL,
                
                -- Accuracy metrics
                total_predictions INTEGER DEFAULT 0,
                correct_predictions INTEGER DEFAULT 0,
                accuracy_percent REAL DEFAULT 0,
                
                -- Direction accuracy
                buy_predictions INTEGER DEFAULT 0,
                buy_correct INTEGER DEFAULT 0,
                sell_predictions INTEGER DEFAULT 0,
                sell_correct INTEGER DEFAULT 0,
                hold_predictions INTEGER DEFAULT 0,
                hold_correct INTEGER DEFAULT 0,
                
                -- Price prediction accuracy
                avg_error_percent REAL DEFAULT 0,
                rmse REAL DEFAULT 0,
                mae REAL DEFAULT 0,
                
                -- Confidence metrics
                avg_confidence REAL DEFAULT 0,
                confidence_calibration REAL DEFAULT 0,
                
                -- Model performance
                lstm_accuracy REAL DEFAULT 0,
                trend_accuracy REAL DEFAULT 0,
                technical_accuracy REAL DEFAULT 0,
                
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                
                UNIQUE(symbol, timeframe, period_start, period_end)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("✓ Prediction database tables initialized successfully")
    
    def get_prediction(self, symbol: str, date: str, timeframe: str = 'DAILY_EOD') -> Optional[Dict]:
        """
        Get existing prediction for symbol on specific date
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            date: Date in 'YYYY-MM-DD' format
            timeframe: Prediction timeframe (default: 'DAILY_EOD')
        
        Returns:
            Prediction dictionary or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM predictions
            WHERE symbol = ? 
            AND DATE(prediction_date) = DATE(?)
            AND timeframe = ?
            AND status = 'ACTIVE'
        ''', (symbol.upper(), date, timeframe))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            result = dict(row)
            logger.info(f"✓ Found cached prediction for {symbol} on {date}")
            return result
        
        logger.info(f"No cached prediction found for {symbol} on {date}")
        return None
    
    def store_prediction(self, prediction_data: Dict) -> int:
        """
        Store new prediction in database
        
        Args:
            prediction_data: Dictionary containing prediction information
        
        Returns:
            prediction_id of the inserted record
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO predictions (
                    symbol, prediction_date, target_date, timeframe,
                    current_price, predicted_price, predicted_change_percent,
                    prediction, confidence,
                    lstm_prediction, lstm_weight,
                    trend_prediction, trend_weight,
                    technical_prediction, technical_weight,
                    sentiment_label, sentiment_score, sentiment_confidence, article_count,
                    chart_interval, chart_period, data_points_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                prediction_data['symbol'].upper(),
                prediction_data['prediction_date'],
                prediction_data['target_date'],
                prediction_data['timeframe'],
                prediction_data['current_price'],
                prediction_data['predicted_price'],
                prediction_data['predicted_change_percent'],
                prediction_data['prediction'],
                prediction_data['confidence'],
                prediction_data.get('lstm_prediction'),
                prediction_data.get('lstm_weight'),
                prediction_data.get('trend_prediction'),
                prediction_data.get('trend_weight'),
                prediction_data.get('technical_prediction'),
                prediction_data.get('technical_weight'),
                prediction_data.get('sentiment_label'),
                prediction_data.get('sentiment_score'),
                prediction_data.get('sentiment_confidence'),
                prediction_data.get('article_count'),
                prediction_data.get('chart_interval', '1d'),
                prediction_data.get('chart_period', '1y'),
                prediction_data.get('data_points_count', 0)
            ))
            
            prediction_id = cursor.lastrowid
            conn.commit()
            logger.info(f"✓ Stored prediction {prediction_id} for {prediction_data['symbol']} - "
                       f"{prediction_data['prediction']} @ ${prediction_data['predicted_price']:.2f}")
            
            return prediction_id
            
        except sqlite3.IntegrityError as e:
            logger.warning(f"Prediction already exists for {prediction_data['symbol']} on "
                          f"{prediction_data['prediction_date']}: {e}")
            # Return existing prediction ID
            cursor.execute('''
                SELECT prediction_id FROM predictions
                WHERE symbol = ? AND prediction_date = ? AND timeframe = ?
            ''', (prediction_data['symbol'].upper(), prediction_data['prediction_date'], 
                  prediction_data['timeframe']))
            
            result = cursor.fetchone()
            return result[0] if result else -1
            
        finally:
            conn.close()
    
    def update_prediction_outcome(self, prediction_id: int, actual_price: float, 
                                   is_correct: bool) -> bool:
        """
        Update prediction with actual outcome
        
        Args:
            prediction_id: ID of the prediction to update
            actual_price: Actual closing price
            is_correct: Whether prediction was correct (within tolerance)
        
        Returns:
            True if successful, False otherwise
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # First get the prediction to calculate accuracy
        cursor.execute('''
            SELECT current_price, predicted_price, prediction 
            FROM predictions WHERE prediction_id = ?
        ''', (prediction_id,))
        
        result = cursor.fetchone()
        if not result:
            logger.error(f"Prediction {prediction_id} not found")
            conn.close()
            return False
        
        current_price, predicted_price, prediction = result
        
        # Calculate actual change and error
        actual_change_percent = ((actual_price - current_price) / current_price) * 100
        prediction_error_percent = abs((actual_price - predicted_price) / predicted_price * 100)
        
        # Update the prediction
        cursor.execute('''
            UPDATE predictions 
            SET actual_price = ?,
                actual_change_percent = ?,
                prediction_error_percent = ?,
                prediction_correct = ?,
                status = 'COMPLETED',
                validated_at = ?
            WHERE prediction_id = ?
        ''', (actual_price, actual_change_percent, prediction_error_percent,
              1 if is_correct else 0, datetime.now().isoformat(), prediction_id))
        
        conn.commit()
        conn.close()
        
        logger.info(f"✓ Updated prediction {prediction_id}: Actual=${actual_price:.2f}, "
                   f"Error={prediction_error_percent:.2f}%, Correct={is_correct}")
        
        return True
    
    def get_active_predictions(self) -> List[Dict]:
        """
        Get all active predictions (not yet validated)
        
        Returns:
            List of prediction dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM predictions
            WHERE status = 'ACTIVE'
            ORDER BY target_date ASC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        predictions = [dict(row) for row in rows]
        logger.info(f"✓ Retrieved {len(predictions)} active predictions")
        
        return predictions
    
    def get_prediction_history(self, symbol: str, days: int = 30, 
                               timeframe: Optional[str] = None) -> List[Dict]:
        """
        Get historical predictions for a symbol
        
        Args:
            symbol: Stock symbol
            days: Number of days to look back
            timeframe: Optional timeframe filter
        
        Returns:
            List of prediction dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        if timeframe:
            cursor.execute('''
                SELECT * FROM predictions
                WHERE symbol = ? 
                AND DATE(prediction_date) >= DATE(?)
                AND timeframe = ?
                ORDER BY prediction_date DESC
            ''', (symbol.upper(), start_date, timeframe))
        else:
            cursor.execute('''
                SELECT * FROM predictions
                WHERE symbol = ? 
                AND DATE(prediction_date) >= DATE(?)
                ORDER BY prediction_date DESC
            ''', (symbol.upper(), start_date))
        
        rows = cursor.fetchall()
        conn.close()
        
        predictions = [dict(row) for row in rows]
        logger.info(f"✓ Retrieved {len(predictions)} historical predictions for {symbol}")
        
        return predictions
    
    def calculate_accuracy_stats(self, symbol: str, days: int = 30, 
                                  timeframe: Optional[str] = None) -> Dict:
        """
        Calculate accuracy statistics for a symbol
        
        Args:
            symbol: Stock symbol
            days: Number of days to analyze
            timeframe: Optional timeframe filter
        
        Returns:
            Dictionary with accuracy statistics
        """
        predictions = self.get_prediction_history(symbol, days, timeframe)
        
        # Filter only completed predictions
        completed = [p for p in predictions if p['status'] == 'COMPLETED']
        
        if not completed:
            return {
                'total_predictions': 0,
                'correct_predictions': 0,
                'accuracy_percent': 0,
                'avg_error_percent': 0,
                'buy_accuracy': 0,
                'sell_accuracy': 0,
                'hold_accuracy': 0
            }
        
        total = len(completed)
        correct = sum(1 for p in completed if p['prediction_correct'] == 1)
        
        # Calculate direction-specific accuracy
        buy_preds = [p for p in completed if p['prediction'] == 'BUY']
        buy_correct = sum(1 for p in buy_preds if p['prediction_correct'] == 1)
        buy_accuracy = (buy_correct / len(buy_preds) * 100) if buy_preds else 0
        
        sell_preds = [p for p in completed if p['prediction'] == 'SELL']
        sell_correct = sum(1 for p in sell_preds if p['prediction_correct'] == 1)
        sell_accuracy = (sell_correct / len(sell_preds) * 100) if sell_preds else 0
        
        hold_preds = [p for p in completed if p['prediction'] == 'HOLD']
        hold_correct = sum(1 for p in hold_preds if p['prediction_correct'] == 1)
        hold_accuracy = (hold_correct / len(hold_preds) * 100) if hold_preds else 0
        
        # Calculate average error
        errors = [p['prediction_error_percent'] for p in completed if p['prediction_error_percent']]
        avg_error = sum(errors) / len(errors) if errors else 0
        
        stats = {
            'total_predictions': total,
            'correct_predictions': correct,
            'accuracy_percent': (correct / total * 100) if total > 0 else 0,
            'avg_error_percent': avg_error,
            'buy_accuracy': buy_accuracy,
            'sell_accuracy': sell_accuracy,
            'hold_accuracy': hold_accuracy,
            'buy_total': len(buy_preds),
            'sell_total': len(sell_preds),
            'hold_total': len(hold_preds)
        }
        
        logger.info(f"✓ Calculated accuracy stats for {symbol}: "
                   f"{stats['accuracy_percent']:.1f}% accurate over {days} days")
        
        return stats
    
    def update_accuracy_stats(self, symbol: str, timeframe: str = 'DAILY_EOD',
                              period_days: int = 30) -> bool:
        """
        Update stored accuracy statistics for a symbol
        
        Args:
            symbol: Stock symbol
            timeframe: Prediction timeframe
            period_days: Period to analyze
        
        Returns:
            True if successful
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        start_date = (datetime.now() - timedelta(days=period_days)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        # Get completed predictions in period
        cursor.execute('''
            SELECT * FROM predictions
            WHERE symbol = ? 
            AND timeframe = ?
            AND status = 'COMPLETED'
            AND DATE(prediction_date) BETWEEN DATE(?) AND DATE(?)
        ''', (symbol.upper(), timeframe, start_date, end_date))
        
        predictions = cursor.fetchall()
        
        if not predictions:
            conn.close()
            return False
        
        # Calculate statistics
        total = len(predictions)
        correct = sum(1 for p in predictions if p[24] == 1)  # prediction_correct column
        
        buy_preds = [p for p in predictions if p[8] == 'BUY']
        buy_correct = sum(1 for p in buy_preds if p[24] == 1)
        
        sell_preds = [p for p in predictions if p[8] == 'SELL']
        sell_correct = sum(1 for p in sell_preds if p[24] == 1)
        
        hold_preds = [p for p in predictions if p[8] == 'HOLD']
        hold_correct = sum(1 for p in hold_preds if p[24] == 1)
        
        errors = [p[23] for p in predictions if p[23] is not None]  # prediction_error_percent
        avg_error = sum(errors) / len(errors) if errors else 0
        
        confidences = [p[9] for p in predictions if p[9] is not None]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        # Insert or update stats
        cursor.execute('''
            INSERT OR REPLACE INTO prediction_accuracy_stats (
                symbol, timeframe, period_start, period_end,
                total_predictions, correct_predictions, accuracy_percent,
                buy_predictions, buy_correct,
                sell_predictions, sell_correct,
                hold_predictions, hold_correct,
                avg_error_percent, avg_confidence, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            symbol.upper(), timeframe, start_date, end_date,
            total, correct, (correct / total * 100) if total > 0 else 0,
            len(buy_preds), buy_correct,
            len(sell_preds), sell_correct,
            len(hold_preds), hold_correct,
            avg_error, avg_confidence,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"✓ Updated accuracy stats for {symbol}: {correct}/{total} correct "
                   f"({correct/total*100:.1f}%)")
        
        return True
    
    def get_accuracy_statistics(self, symbol: str, timeframe: str = 'DAILY_EOD',
                                period: str = 'month') -> Dict:
        """
        Get detailed accuracy statistics from database
        
        Args:
            symbol: Stock symbol
            timeframe: Prediction timeframe
            period: 'week', 'month', 'quarter', 'year', 'all'
        
        Returns:
            Dictionary with detailed statistics
        """
        period_days = {
            'week': 7,
            'month': 30,
            'quarter': 90,
            'year': 365,
            'all': 3650
        }.get(period, 30)
        
        # Calculate live stats
        stats = self.calculate_accuracy_stats(symbol, period_days, timeframe)
        
        # Add detailed breakdowns
        predictions = self.get_prediction_history(symbol, period_days, timeframe)
        completed = [p for p in predictions if p['status'] == 'COMPLETED']
        
        if completed:
            # Calculate RMSE and MAE
            errors = [p['prediction_error_percent'] for p in completed if p['prediction_error_percent']]
            if errors:
                rmse = (sum(e**2 for e in errors) / len(errors)) ** 0.5
                mae = sum(abs(e) for e in errors) / len(errors)
            else:
                rmse = mae = 0
            
            stats['price_accuracy'] = {
                'rmse': rmse,
                'mae': mae
            }
            
            # Confidence analysis
            high_conf = [p for p in completed if p['confidence'] >= 80]
            low_conf = [p for p in completed if p['confidence'] < 60]
            
            stats['confidence_stats'] = {
                'avg_confidence': sum(p['confidence'] for p in completed) / len(completed),
                'high_confidence_accuracy': (sum(1 for p in high_conf if p['prediction_correct'] == 1) / len(high_conf) * 100) if high_conf else 0,
                'low_confidence_accuracy': (sum(1 for p in low_conf if p['prediction_correct'] == 1) / len(low_conf) * 100) if low_conf else 0
            }
            
            # Model component accuracy
            lstm_preds = [p for p in completed if p['lstm_prediction']]
            if lstm_preds:
                lstm_correct = sum(1 for p in lstm_preds if p['prediction_correct'] == 1)
                stats['lstm_accuracy'] = (lstm_correct / len(lstm_preds) * 100) if lstm_preds else 0
            else:
                stats['lstm_accuracy'] = 0
        
        logger.info(f"✓ Retrieved accuracy statistics for {symbol} ({period})")
        
        return stats


# Singleton instance
_prediction_db = None

def get_prediction_db(db_path: str = "trading.db") -> PredictionDatabase:
    """Get singleton prediction database instance"""
    global _prediction_db
    if _prediction_db is None:
        _prediction_db = PredictionDatabase(db_path)
    return _prediction_db
