"""
Integration Bridge Service - Safe ML Learning Integration
Connects modules to ML backend without modifying existing functionality
Runs on port 8004 to avoid conflicts
"""

import os
import sys
import json
import logging
import sqlite3
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import httpx
import pandas as pd
import numpy as np
from collections import deque
import threading
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(title="ML Integration Bridge", version="1.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service URLs - keeping existing ports
MAIN_BACKEND_URL = "http://localhost:8002"
ML_BACKEND_URL = "http://localhost:8003"

# Database for integration data
BRIDGE_DB = "ml_integration_bridge.db"

# Knowledge queue for async processing
knowledge_queue = deque(maxlen=1000)  # Fixed: use maxlen instead of maxsize
pattern_cache = {}

def init_bridge_database():
    """Initialize bridge database for integration data"""
    conn = sqlite3.connect(BRIDGE_DB)
    cursor = conn.cursor()
    
    # Integration events table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS integration_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            source_module TEXT NOT NULL,
            event_type TEXT NOT NULL,
            data TEXT NOT NULL,
            processed BOOLEAN DEFAULT 0,
            ml_model_updated BOOLEAN DEFAULT 0
        )
    ''')
    
    # Shared patterns discovered across modules
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shared_patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pattern_id TEXT UNIQUE NOT NULL,
            source_module TEXT NOT NULL,
            pattern_type TEXT NOT NULL,
            symbol TEXT,
            pattern_data TEXT NOT NULL,
            confidence REAL,
            created_at TEXT NOT NULL,
            last_validated TEXT,
            validation_count INTEGER DEFAULT 0,
            ml_incorporated BOOLEAN DEFAULT 0
        )
    ''')
    
    # Module insights for cross-sharing
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS module_insights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            module_name TEXT NOT NULL,
            insight_type TEXT NOT NULL,
            symbol TEXT,
            insight_data TEXT NOT NULL,
            ml_prediction TEXT,
            accuracy_score REAL
        )
    ''')
    
    # ML feedback to modules
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ml_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            target_module TEXT NOT NULL,
            symbol TEXT NOT NULL,
            feedback_type TEXT NOT NULL,
            recommendation TEXT NOT NULL,
            confidence REAL,
            applied BOOLEAN DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database
init_bridge_database()

# Request/Response models
class DocumentSentimentEvent(BaseModel):
    source: str = "document_analyzer"
    symbol: Optional[str]
    sentiment_score: float
    confidence: float
    key_phrases: List[str]
    document_type: str
    analysis_text: str

class HistoricalPatternEvent(BaseModel):
    source: str = "historical_analysis"
    symbol: str
    pattern_type: str
    pattern_data: Dict
    time_period: str
    confidence: float
    
class MarketMoverEvent(BaseModel):
    source: str = "market_movers"
    symbol: str
    movement_type: str  # "gainer" or "loser"
    change_percent: float
    volume_spike: float
    sector: Optional[str]

class TechnicalIndicatorEvent(BaseModel):
    source: str = "technical_analysis"
    symbol: str
    indicators: Dict[str, float]  # RSI, MACD, etc.
    signals: List[str]
    trend: str

class MLKnowledgeRequest(BaseModel):
    module: str
    symbol: str
    request_type: str  # "prediction", "pattern", "sentiment"
    context: Optional[Dict] = {}

class IntegrationStatus(BaseModel):
    bridge_active: bool
    events_pending: int
    patterns_discovered: int
    ml_updates_sent: int
    modules_connected: List[str]

# Bridge Core Functions
async def forward_to_ml(event_data: Dict, event_type: str):
    """Forward learning events to ML backend"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Check if ML backend is available
            try:
                health = await client.get(f"{ML_BACKEND_URL}/api/health")
                if not health.is_success:
                    logger.warning("ML backend not available")
                    return None
            except:
                logger.warning("ML backend not responding")
                return None
            
            # Send to ML for learning
            if event_type == "sentiment":
                # Add sentiment pattern to ML knowledge base
                response = await client.post(
                    f"{ML_BACKEND_URL}/api/knowledge/add-pattern",
                    json={
                        "pattern_type": "sentiment_signal",
                        "symbol": event_data.get("symbol", "GENERAL"),
                        "pattern_data": {
                            "sentiment": event_data.get("sentiment_score"),
                            "confidence": event_data.get("confidence"),
                            "phrases": event_data.get("key_phrases", [])
                        }
                    }
                )
            elif event_type == "historical_pattern":
                response = await client.post(
                    f"{ML_BACKEND_URL}/api/knowledge/add-pattern",
                    json={
                        "pattern_type": event_data.get("pattern_type"),
                        "symbol": event_data.get("symbol"),
                        "pattern_data": event_data.get("pattern_data")
                    }
                )
            elif event_type == "market_movement":
                response = await client.post(
                    f"{ML_BACKEND_URL}/api/knowledge/add-pattern",
                    json={
                        "pattern_type": "market_movement",
                        "symbol": event_data.get("symbol"),
                        "pattern_data": {
                            "movement": event_data.get("movement_type"),
                            "change": event_data.get("change_percent"),
                            "volume": event_data.get("volume_spike")
                        }
                    }
                )
                
            return response.json() if response.is_success else None
    except Exception as e:
        logger.error(f"Error forwarding to ML: {str(e)}")
        return None

async def get_ml_insights(symbol: str, context: Dict) -> Optional[Dict]:
    """Get ML insights for a symbol"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{ML_BACKEND_URL}/api/predict",
                json={
                    "symbol": symbol,
                    "context": context
                }
            )
            if response.is_success:
                return response.json()
    except Exception as e:
        logger.error(f"Error getting ML insights: {str(e)}")
    return None

# API Endpoints for Module Integration

@app.post("/api/bridge/document-sentiment")
async def receive_document_sentiment(event: DocumentSentimentEvent, background_tasks: BackgroundTasks):
    """Receive sentiment analysis from Document Analyzer"""
    try:
        # Store event
        conn = sqlite3.connect(BRIDGE_DB)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO integration_events (timestamp, source_module, event_type, data)
            VALUES (?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            event.source,
            "sentiment",
            json.dumps(event.dict())
        ))
        event_id = cursor.lastrowid
        conn.commit()
        
        # Add pattern if significant
        if abs(event.sentiment_score) > 0.7:
            pattern_id = f"sentiment_{event.symbol}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            cursor.execute('''
                INSERT OR REPLACE INTO shared_patterns 
                (pattern_id, source_module, pattern_type, symbol, pattern_data, confidence, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                pattern_id,
                event.source,
                "strong_sentiment",
                event.symbol,
                json.dumps({
                    "score": event.sentiment_score,
                    "phrases": event.key_phrases[:5]
                }),
                event.confidence,
                datetime.now().isoformat()
            ))
            conn.commit()
        
        conn.close()
        
        # Forward to ML in background
        background_tasks.add_task(forward_to_ml, event.dict(), "sentiment")
        
        # Return ML insights if available
        ml_insights = await get_ml_insights(event.symbol or "GENERAL", {"sentiment": event.sentiment_score})
        
        return {
            "status": "received",
            "event_id": event_id,
            "ml_insights": ml_insights,
            "recommendation": generate_recommendation("document", event.dict(), ml_insights)
        }
        
    except Exception as e:
        logger.error(f"Error processing document sentiment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/bridge/historical-pattern")
async def receive_historical_pattern(event: HistoricalPatternEvent, background_tasks: BackgroundTasks):
    """Receive pattern discovery from Historical Data Analysis"""
    try:
        # Store event and pattern
        conn = sqlite3.connect(BRIDGE_DB)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO integration_events (timestamp, source_module, event_type, data)
            VALUES (?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            event.source,
            "historical_pattern",
            json.dumps(event.dict())
        ))
        
        pattern_id = f"hist_{event.symbol}_{event.pattern_type}_{datetime.now().strftime('%Y%m%d')}"
        cursor.execute('''
            INSERT OR REPLACE INTO shared_patterns 
            (pattern_id, source_module, pattern_type, symbol, pattern_data, confidence, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            pattern_id,
            event.source,
            event.pattern_type,
            event.symbol,
            json.dumps(event.pattern_data),
            event.confidence,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        # Forward to ML
        background_tasks.add_task(forward_to_ml, event.dict(), "historical_pattern")
        
        # Get ML validation
        ml_insights = await get_ml_insights(event.symbol, {"pattern": event.pattern_type})
        
        return {
            "status": "received",
            "pattern_id": pattern_id,
            "ml_validation": ml_insights,
            "enhanced_pattern": enhance_pattern_with_ml(event.dict(), ml_insights)
        }
        
    except Exception as e:
        logger.error(f"Error processing historical pattern: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/bridge/market-movement")
async def receive_market_movement(event: MarketMoverEvent, background_tasks: BackgroundTasks):
    """Receive market movement from Market Movers"""
    try:
        # Store and process
        conn = sqlite3.connect(BRIDGE_DB)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO integration_events (timestamp, source_module, event_type, data)
            VALUES (?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            event.source,
            "market_movement",
            json.dumps(event.dict())
        ))
        
        # Check for significant movement
        if abs(event.change_percent) > 5:
            cursor.execute('''
                INSERT INTO shared_patterns 
                (pattern_id, source_module, pattern_type, symbol, pattern_data, confidence, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                f"move_{event.symbol}_{datetime.now().strftime('%Y%m%d')}",
                event.source,
                "significant_movement",
                event.symbol,
                json.dumps({
                    "change": event.change_percent,
                    "volume": event.volume_spike,
                    "type": event.movement_type
                }),
                0.8,
                datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
        
        # Forward to ML
        background_tasks.add_task(forward_to_ml, event.dict(), "market_movement")
        
        # Get ML prediction for continued movement
        ml_prediction = await get_ml_insights(event.symbol, {
            "recent_change": event.change_percent,
            "volume_spike": event.volume_spike
        })
        
        return {
            "status": "received",
            "ml_prediction": ml_prediction,
            "suggested_action": suggest_action_from_movement(event.dict(), ml_prediction)
        }
        
    except Exception as e:
        logger.error(f"Error processing market movement: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/bridge/technical-indicators")
async def receive_technical_indicators(event: TechnicalIndicatorEvent, background_tasks: BackgroundTasks):
    """Receive technical indicators from Technical Analysis"""
    try:
        # Store event
        conn = sqlite3.connect(BRIDGE_DB)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO integration_events (timestamp, source_module, event_type, data)
            VALUES (?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            event.source,
            "technical_indicators",
            json.dumps(event.dict())
        ))
        
        # Store significant signals
        for signal in event.signals:
            if signal in ["golden_cross", "death_cross", "breakout", "breakdown"]:
                cursor.execute('''
                    INSERT INTO shared_patterns 
                    (pattern_id, source_module, pattern_type, symbol, pattern_data, confidence, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    f"signal_{event.symbol}_{signal}_{datetime.now().strftime('%Y%m%d')}",
                    event.source,
                    f"technical_{signal}",
                    event.symbol,
                    json.dumps({
                        "indicators": event.indicators,
                        "signal": signal,
                        "trend": event.trend
                    }),
                    0.75,
                    datetime.now().isoformat()
                ))
        
        conn.commit()
        conn.close()
        
        # Forward to ML
        background_tasks.add_task(forward_to_ml, event.dict(), "technical_indicators")
        
        # Get ML confirmation
        ml_analysis = await get_ml_insights(event.symbol, event.indicators)
        
        return {
            "status": "received",
            "ml_confirmation": ml_analysis,
            "combined_signal": combine_technical_ml_signals(event.dict(), ml_analysis)
        }
        
    except Exception as e:
        logger.error(f"Error processing technical indicators: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/bridge/ml-knowledge/{symbol}")
async def get_ml_knowledge(symbol: str, module: str):
    """Get ML knowledge for a specific symbol and module"""
    try:
        # Get shared patterns
        conn = sqlite3.connect(BRIDGE_DB)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT pattern_type, pattern_data, confidence, source_module
            FROM shared_patterns
            WHERE symbol = ? AND ml_incorporated = 1
            ORDER BY confidence DESC
            LIMIT 10
        ''', (symbol,))
        
        patterns = []
        for row in cursor.fetchall():
            patterns.append({
                "type": row[0],
                "data": json.loads(row[1]),
                "confidence": row[2],
                "source": row[3]
            })
        
        # Get ML feedback for this module
        cursor.execute('''
            SELECT feedback_type, recommendation, confidence
            FROM ml_feedback
            WHERE target_module = ? AND symbol = ? AND applied = 0
            ORDER BY timestamp DESC
            LIMIT 5
        ''', (module, symbol))
        
        feedback = []
        for row in cursor.fetchall():
            feedback.append({
                "type": row[0],
                "recommendation": row[1],
                "confidence": row[2]
            })
        
        conn.close()
        
        # Get latest ML prediction
        ml_prediction = await get_ml_insights(symbol, {"requesting_module": module})
        
        return {
            "symbol": symbol,
            "learned_patterns": patterns,
            "ml_feedback": feedback,
            "current_prediction": ml_prediction,
            "integration_active": True
        }
        
    except Exception as e:
        logger.error(f"Error getting ML knowledge: {str(e)}")
        return {
            "symbol": symbol,
            "learned_patterns": [],
            "ml_feedback": [],
            "current_prediction": None,
            "integration_active": False,
            "error": str(e)
        }

@app.get("/api/bridge/status")
async def get_bridge_status():
    """Get integration bridge status"""
    try:
        conn = sqlite3.connect(BRIDGE_DB)
        cursor = conn.cursor()
        
        # Count pending events
        cursor.execute("SELECT COUNT(*) FROM integration_events WHERE processed = 0")
        pending = cursor.fetchone()[0]
        
        # Count patterns
        cursor.execute("SELECT COUNT(*) FROM shared_patterns")
        patterns = cursor.fetchone()[0]
        
        # Count ML updates
        cursor.execute("SELECT COUNT(*) FROM integration_events WHERE ml_model_updated = 1")
        ml_updates = cursor.fetchone()[0]
        
        # Get connected modules
        cursor.execute("SELECT DISTINCT source_module FROM integration_events WHERE timestamp > datetime('now', '-1 hour')")
        modules = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        # Check service health
        ml_healthy = False
        backend_healthy = False
        
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                ml_response = await client.get(f"{ML_BACKEND_URL}/api/health")
                ml_healthy = ml_response.is_success
                
                backend_response = await client.get(f"{MAIN_BACKEND_URL}/api/status")
                backend_healthy = backend_response.is_success
        except:
            pass
        
        return {
            "bridge_active": True,
            "events_pending": pending,
            "patterns_discovered": patterns,
            "ml_updates_sent": ml_updates,
            "modules_connected": modules,
            "ml_backend_healthy": ml_healthy,
            "main_backend_healthy": backend_healthy,
            "queue_size": len(knowledge_queue)
        }
        
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/bridge/sync-patterns")
async def sync_patterns_with_ml():
    """Manually sync all patterns with ML backend"""
    try:
        conn = sqlite3.connect(BRIDGE_DB)
        cursor = conn.cursor()
        
        # Get unsynced patterns
        cursor.execute('''
            SELECT pattern_id, symbol, pattern_type, pattern_data, confidence
            FROM shared_patterns
            WHERE ml_incorporated = 0
            LIMIT 100
        ''')
        
        patterns = cursor.fetchall()
        synced_count = 0
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            for pattern in patterns:
                try:
                    response = await client.post(
                        f"{ML_BACKEND_URL}/api/knowledge/add-pattern",
                        json={
                            "pattern_type": pattern[2],
                            "symbol": pattern[1],
                            "pattern_data": json.loads(pattern[3]),
                            "confidence": pattern[4]
                        }
                    )
                    
                    if response.is_success:
                        cursor.execute(
                            "UPDATE shared_patterns SET ml_incorporated = 1 WHERE pattern_id = ?",
                            (pattern[0],)
                        )
                        synced_count += 1
                except Exception as e:
                    logger.error(f"Error syncing pattern {pattern[0]}: {str(e)}")
        
        conn.commit()
        conn.close()
        
        return {
            "patterns_synced": synced_count,
            "patterns_remaining": len(patterns) - synced_count
        }
        
    except Exception as e:
        logger.error(f"Error syncing patterns: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Helper Functions

def generate_recommendation(module: str, event_data: Dict, ml_insights: Optional[Dict]) -> Dict:
    """Generate recommendation based on event and ML insights"""
    recommendation = {
        "action": "monitor",
        "confidence": 0.5,
        "reasoning": []
    }
    
    if module == "document" and event_data.get("sentiment_score"):
        sentiment = event_data["sentiment_score"]
        if sentiment > 0.7:
            recommendation["action"] = "consider_buy"
            recommendation["reasoning"].append("Strong positive sentiment detected")
        elif sentiment < -0.7:
            recommendation["action"] = "consider_sell"
            recommendation["reasoning"].append("Strong negative sentiment detected")
    
    if ml_insights and ml_insights.get("prediction"):
        ml_pred = ml_insights["prediction"]
        if ml_pred.get("direction") == "up":
            recommendation["confidence"] += 0.2
            recommendation["reasoning"].append("ML predicts upward movement")
        elif ml_pred.get("direction") == "down":
            recommendation["confidence"] -= 0.2
            recommendation["reasoning"].append("ML predicts downward movement")
    
    recommendation["confidence"] = max(0, min(1, recommendation["confidence"]))
    return recommendation

def enhance_pattern_with_ml(pattern_data: Dict, ml_insights: Optional[Dict]) -> Dict:
    """Enhance pattern with ML insights"""
    enhanced = pattern_data.copy()
    
    if ml_insights:
        enhanced["ml_validation"] = ml_insights.get("pattern_valid", False)
        enhanced["ml_confidence"] = ml_insights.get("confidence", 0)
        enhanced["ml_similar_patterns"] = ml_insights.get("similar_patterns", [])
        enhanced["ml_success_rate"] = ml_insights.get("historical_success", 0)
    
    return enhanced

def suggest_action_from_movement(movement_data: Dict, ml_prediction: Optional[Dict]) -> Dict:
    """Suggest action based on market movement and ML prediction"""
    suggestion = {
        "action": "wait",
        "reasoning": [],
        "confidence": 0.5
    }
    
    change = movement_data.get("change_percent", 0)
    volume = movement_data.get("volume_spike", 1)
    
    if abs(change) > 5 and volume > 2:
        if change > 0:
            suggestion["action"] = "monitor_resistance"
            suggestion["reasoning"].append(f"Strong move up {change:.1f}% with volume")
        else:
            suggestion["action"] = "monitor_support"
            suggestion["reasoning"].append(f"Strong move down {change:.1f}% with volume")
    
    if ml_prediction and ml_prediction.get("continuation_probability"):
        cont_prob = ml_prediction["continuation_probability"]
        if cont_prob > 0.7:
            suggestion["action"] = "follow_trend"
            suggestion["reasoning"].append(f"ML suggests {cont_prob:.0%} continuation probability")
            suggestion["confidence"] = cont_prob
    
    return suggestion

def combine_technical_ml_signals(technical_data: Dict, ml_analysis: Optional[Dict]) -> Dict:
    """Combine technical and ML signals"""
    combined = {
        "signal_strength": 0,
        "direction": "neutral",
        "confidence": 0.5,
        "factors": []
    }
    
    # Technical signals
    for signal in technical_data.get("signals", []):
        if signal == "golden_cross":
            combined["signal_strength"] += 2
            combined["factors"].append("Golden cross detected")
        elif signal == "death_cross":
            combined["signal_strength"] -= 2
            combined["factors"].append("Death cross detected")
    
    # ML signals
    if ml_analysis:
        ml_signal = ml_analysis.get("signal_strength", 0)
        combined["signal_strength"] += ml_signal
        if ml_signal != 0:
            combined["factors"].append(f"ML signal: {ml_signal:+.1f}")
    
    # Determine direction
    if combined["signal_strength"] > 1:
        combined["direction"] = "bullish"
    elif combined["signal_strength"] < -1:
        combined["direction"] = "bearish"
    
    # Calculate confidence
    combined["confidence"] = min(1, abs(combined["signal_strength"]) / 5)
    
    return combined

# Background processor for async learning
async def process_knowledge_queue():
    """Process knowledge queue in background"""
    while True:
        try:
            if knowledge_queue:
                item = knowledge_queue.popleft()
                await forward_to_ml(item["data"], item["type"])
        except Exception as e:
            logger.error(f"Queue processor error: {str(e)}")
        await asyncio.sleep(5)

@app.on_event("startup")
async def startup_event():
    """Start background tasks"""
    asyncio.create_task(process_knowledge_queue())
    logger.info("Integration Bridge started on port 8004")
    logger.info("Bridging Main Backend (8002) <-> ML Backend (8003)")

@app.get("/api/bridge/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ML Integration Bridge",
        "version": "1.0",
        "bridges": [
            "document_analyzer -> ml_learning",
            "historical_analysis -> ml_learning",
            "market_movers -> ml_learning",
            "technical_analysis -> ml_learning",
            "ml_predictions -> all_modules"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting ML Integration Bridge on port 8004")
    logger.info("This bridge connects all modules to ML learning without breaking existing functionality")
    uvicorn.run(app, host="0.0.0.0", port=8004)