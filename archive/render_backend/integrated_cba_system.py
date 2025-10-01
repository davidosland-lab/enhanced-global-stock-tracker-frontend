#!/usr/bin/env python3
"""
Integrated CBA System - Connects all existing implementations
Brings together the already-implemented modules from GSMT-Ver-813
"""

from fastapi import APIRouter, HTTPException, Query, File, UploadFile, Form
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any
import logging
import os
import json

# Import the existing CBA enhanced prediction system
try:
    from cba_enhanced_prediction_system import (
        CBAEnhancedPredictor,
        CBAPublication,
        CBANewsArticle,
        NewsSource,
        PublicationType
    )
    CBA_ENHANCED_AVAILABLE = True
except ImportError as e:
    logging.warning(f"CBA Enhanced Prediction System not available: {e}")
    CBA_ENHANCED_AVAILABLE = False

# Import performance monitoring
try:
    from phase3_realtime_performance_monitoring import (
        PerformanceMonitor,
        PredictionRecord,
        PerformanceMetrics
    )
    PERFORMANCE_MONITOR_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Performance Monitoring not available: {e}")
    PERFORMANCE_MONITOR_AVAILABLE = False

# Import reinforcement learning
try:
    from phase3_reinforcement_learning import (
        ReinforcementLearningTrader,
        TradingEnvironment,
        MarketState
    )
    RL_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Reinforcement Learning not available: {e}")
    RL_AVAILABLE = False

# Import central bank integration
try:
    from central_bank_rate_integration import (
        central_bank_tracker,
        CentralBank,
        RateChangeType
    )
    CENTRAL_BANK_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Central Bank Integration not available: {e}")
    CENTRAL_BANK_AVAILABLE = False

logger = logging.getLogger(__name__)

# Create router for CBA integrated features
router = APIRouter(prefix="/api/cba-integrated", tags=["CBA Integrated System"])

# Initialize components if available
cba_predictor = CBAEnhancedPredictor() if CBA_ENHANCED_AVAILABLE else None
performance_monitor = PerformanceMonitor() if PERFORMANCE_MONITOR_AVAILABLE else None
rl_trader = None  # Initialize on demand

@router.get("/status")
async def get_system_status():
    """Get status of all integrated CBA system components"""
    return {
        "success": True,
        "components": {
            "cba_enhanced_predictor": CBA_ENHANCED_AVAILABLE,
            "performance_monitoring": PERFORMANCE_MONITOR_AVAILABLE,
            "reinforcement_learning": RL_AVAILABLE,
            "central_bank_integration": CENTRAL_BANK_AVAILABLE,
            "real_news_api": CBA_ENHANCED_AVAILABLE,
            "document_analysis": CBA_ENHANCED_AVAILABLE,
            "historical_tracking": PERFORMANCE_MONITOR_AVAILABLE
        },
        "message": "CBA Integrated System Status"
    }

@router.get("/real-publications")
async def get_real_cba_publications(
    days: int = Query(30, description="Number of days of publications to fetch"),
    include_asx: bool = Query(True, description="Include ASX announcements"),
    include_reports: bool = Query(True, description="Include annual/quarterly reports")
):
    """Fetch REAL CBA publications from official sources (already implemented in cba_enhanced_prediction_system)"""
    if not CBA_ENHANCED_AVAILABLE:
        raise HTTPException(status_code=503, detail="CBA Enhanced System not available")
    
    try:
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)
        
        # This uses the REAL document fetching already implemented
        publications = await cba_predictor.fetch_cba_publications(
            start_date=start_date,
            end_date=end_date,
            include_asx_announcements=include_asx,
            include_financial_reports=include_reports
        )
        
        return {
            "success": True,
            "publications": [pub.dict() for pub in publications],
            "count": len(publications),
            "sources": [
                "Commonwealth Bank Investor Relations",
                "ASX Announcements",
                "Annual Reports",
                "Quarterly Results"
            ],
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Error fetching real publications: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/real-news")
async def get_real_news_analysis(
    hours: int = Query(48, description="Hours of news to fetch"),
    sources: Optional[List[str]] = Query(None, description="Specific news sources")
):
    """Fetch REAL news from Reuters, Bloomberg, AFR (already implemented)"""
    if not CBA_ENHANCED_AVAILABLE:
        raise HTTPException(status_code=503, detail="CBA Enhanced System not available")
    
    try:
        # Use the real news fetching already implemented
        news_articles = await cba_predictor.fetch_banking_news(
            hours=hours,
            sources=sources or ["reuters", "bloomberg", "afr", "asx"],
            focus_symbol="CBA.AX"
        )
        
        # Perform sentiment analysis on real news
        sentiment_results = []
        for article in news_articles:
            sentiment = await cba_predictor.analyze_news_sentiment(article)
            sentiment_results.append({
                **article.dict(),
                "sentiment_analysis": sentiment
            })
        
        return {
            "success": True,
            "articles": sentiment_results,
            "count": len(sentiment_results),
            "sources_used": list(set(a["source"] for a in sentiment_results)),
            "average_sentiment": sum(a["sentiment_score"] for a in sentiment_results) / len(sentiment_results) if sentiment_results else 0
        }
    except Exception as e:
        logger.error(f"Error fetching real news: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-document")
async def upload_and_analyze_document(
    file: UploadFile = File(...),
    analysis_type: str = Form("general")
):
    """Upload and analyze CBA-related documents (PDF, annual reports, etc.)"""
    if not CBA_ENHANCED_AVAILABLE:
        raise HTTPException(status_code=503, detail="Document analysis not available")
    
    try:
        # Read document content
        content = await file.read()
        
        # Use the existing document analysis implementation
        analysis_result = await cba_predictor.analyze_uploaded_document(
            content=content,
            filename=file.filename,
            content_type=file.content_type,
            analysis_focus=analysis_type
        )
        
        return {
            "success": True,
            "filename": file.filename,
            "analysis": analysis_result,
            "key_metrics_extracted": analysis_result.get("financial_metrics", {}),
            "sentiment": analysis_result.get("sentiment_score", 0),
            "market_impact": analysis_result.get("market_impact_assessment", "neutral")
        }
    except Exception as e:
        logger.error(f"Error analyzing document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ml-prediction")
async def get_machine_learning_prediction(
    horizon: str = Query("1w", description="Prediction horizon"),
    use_rl: bool = Query(False, description="Use reinforcement learning model")
):
    """Get ML-based prediction using trained models (already implemented)"""
    if not CBA_ENHANCED_AVAILABLE:
        raise HTTPException(status_code=503, detail="ML prediction not available")
    
    try:
        # Fetch all real data
        publications = await cba_predictor.fetch_cba_publications(
            start_date=datetime.now(timezone.utc) - timedelta(days=30),
            end_date=datetime.now(timezone.utc)
        )
        
        news = await cba_predictor.fetch_banking_news(hours=48)
        
        # Use the existing ML prediction
        if use_rl and RL_AVAILABLE:
            # Use reinforcement learning model
            prediction = await cba_predictor.predict_with_reinforcement_learning(
                horizon=horizon,
                publications=publications,
                news=news
            )
        else:
            # Use ensemble ML model
            prediction = await cba_predictor.predict_with_ensemble_ml(
                horizon=horizon,
                publications=publications,
                news=news,
                include_central_bank_data=CENTRAL_BANK_AVAILABLE
            )
        
        return {
            "success": True,
            "prediction": prediction,
            "model_type": "reinforcement_learning" if use_rl else "ensemble_ml",
            "data_sources": {
                "publications_used": len(publications),
                "news_articles_used": len(news),
                "central_bank_data": CENTRAL_BANK_AVAILABLE
            }
        }
    except Exception as e:
        logger.error(f"Error generating ML prediction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/historical-performance")
async def get_historical_performance(
    days: int = Query(30, description="Days of historical performance to retrieve")
):
    """Get historical prediction accuracy and performance metrics (already tracked)"""
    if not PERFORMANCE_MONITOR_AVAILABLE:
        raise HTTPException(status_code=503, detail="Performance monitoring not available")
    
    try:
        # Get historical performance from the existing monitoring system
        performance_data = performance_monitor.get_performance_history(
            symbol="CBA.AX",
            days=days
        )
        
        # Calculate accuracy metrics
        accuracy_metrics = performance_monitor.calculate_accuracy_metrics(performance_data)
        
        return {
            "success": True,
            "performance_history": performance_data,
            "accuracy_metrics": accuracy_metrics,
            "period_days": days,
            "total_predictions": len(performance_data),
            "average_accuracy": accuracy_metrics.get("mean_accuracy", 0),
            "best_model": accuracy_metrics.get("best_performing_model", "unknown")
        }
    except Exception as e:
        logger.error(f"Error fetching historical performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/central-bank-impact")
async def get_central_bank_impact():
    """Get central bank rate decisions impact on CBA (already implemented)"""
    if not CENTRAL_BANK_AVAILABLE:
        raise HTTPException(status_code=503, detail="Central bank integration not available")
    
    try:
        # Get RBA rate decisions and impact
        rba_data = await central_bank_tracker.get_rba_impact_on_banking()
        
        # Get global central bank impacts
        global_impacts = await central_bank_tracker.get_global_rate_impacts()
        
        return {
            "success": True,
            "rba_impact": rba_data,
            "global_impacts": global_impacts,
            "current_rba_rate": rba_data.get("current_rate", 0),
            "next_decision_date": rba_data.get("next_meeting", "unknown"),
            "banking_sector_sensitivity": rba_data.get("banking_sensitivity", "high")
        }
    except Exception as e:
        logger.error(f"Error fetching central bank impact: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Export router for main app integration
__all__ = ['router']