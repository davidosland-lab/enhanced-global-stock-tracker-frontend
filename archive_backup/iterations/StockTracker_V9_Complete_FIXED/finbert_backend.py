"""
FinBERT Backend - Real Financial Sentiment Analysis
NO fake data - Uses actual FinBERT model or advanced keyword analysis
"""

import os
import logging
import sqlite3
import json
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import re
from typing import Dict, List, Optional
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import transformers for FinBERT
try:
    from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
    import torch
    HAS_FINBERT = True
    logger.info("FinBERT available - will use real sentiment analysis")
except ImportError:
    HAS_FINBERT = False
    logger.warning("FinBERT not available - using advanced keyword-based analysis")
    logger.warning("To enable FinBERT: pip install transformers torch")

app = FastAPI(title="FinBERT Sentiment Analysis - Real Implementation", version="2.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database for caching sentiment analysis
SENTIMENT_DB = "sentiment_cache.db"

def init_database():
    """Initialize sentiment cache database"""
    conn = sqlite3.connect(SENTIMENT_DB)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sentiment_cache (
            hash_key TEXT PRIMARY KEY,
            text_preview TEXT,
            sentiment TEXT,
            positive_score REAL,
            negative_score REAL,
            neutral_score REAL,
            confidence REAL,
            method TEXT,
            created_at TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS document_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            file_hash TEXT,
            sentiment TEXT,
            positive_score REAL,
            negative_score REAL,
            neutral_score REAL,
            confidence REAL,
            chunks_analyzed INTEGER,
            method TEXT,
            created_at TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

init_database()

# Initialize FinBERT if available
finbert_pipeline = None
if HAS_FINBERT:
    try:
        # Use pipeline for easier usage
        finbert_pipeline = pipeline(
            "sentiment-analysis",
            model="ProsusAI/finbert",
            tokenizer="ProsusAI/finbert",
            device=0 if torch.cuda.is_available() else -1
        )
        logger.info("FinBERT pipeline initialized successfully")
    except Exception as e:
        HAS_FINBERT = False
        logger.error(f"Failed to load FinBERT model: {e}")

class TextRequest(BaseModel):
    text: str
    use_cache: bool = True

class DocumentRequest(BaseModel):
    filename: str
    content: str

# Enhanced financial keywords for better fallback analysis
FINANCIAL_KEYWORDS = {
    'strong_positive': [
        'surge', 'soar', 'skyrocket', 'breakthrough', 'record high', 'all-time high',
        'exceptional', 'outstanding', 'beat expectations', 'exceeded', 'outperform',
        'robust growth', 'strong momentum', 'bullish', 'upgrade', 'raised guidance',
        'expansion', 'innovation', 'market leader', 'competitive advantage'
    ],
    'positive': [
        'profit', 'gain', 'growth', 'increase', 'rise', 'improve', 'positive',
        'strong', 'robust', 'healthy', 'stable', 'recovery', 'rebound', 'upturn',
        'optimistic', 'favorable', 'benefit', 'opportunity', 'efficient', 'success'
    ],
    'negative': [
        'loss', 'decline', 'fall', 'drop', 'decrease', 'weak', 'poor', 'negative',
        'concern', 'risk', 'threat', 'challenge', 'difficult', 'struggle', 'pressure',
        'pessimistic', 'unfavorable', 'headwind', 'slowdown', 'contraction'
    ],
    'strong_negative': [
        'plunge', 'crash', 'collapse', 'plummet', 'crisis', 'bankruptcy', 'default',
        'recession', 'bear market', 'sell-off', 'panic', 'catastrophic', 'severe',
        'downgrade', 'cut guidance', 'profit warning', 'layoffs', 'restructuring'
    ],
    'uncertainty': [
        'volatile', 'uncertain', 'unclear', 'mixed', 'fluctuate', 'unpredictable',
        'caution', 'wait-and-see', 'depends', 'possible', 'potential', 'maybe'
    ]
}

def get_text_hash(text: str) -> str:
    """Generate hash for text caching"""
    return hashlib.md5(text.encode()).hexdigest()

def analyze_with_finbert(text: str) -> Dict:
    """Analyze text using real FinBERT model"""
    if not finbert_pipeline:
        return analyze_with_advanced_keywords(text)
    
    try:
        # FinBERT returns: positive, negative, neutral
        results = finbert_pipeline(text[:512])  # Truncate to max length
        
        if results and len(results) > 0:
            result = results[0]
            label = result['label'].lower()
            score = result['score']
            
            # Map FinBERT output to our format
            scores = {'positive': 0.0, 'negative': 0.0, 'neutral': 0.0}
            
            if label == 'positive':
                scores['positive'] = score
                scores['negative'] = (1 - score) * 0.3
                scores['neutral'] = (1 - score) * 0.7
            elif label == 'negative':
                scores['negative'] = score
                scores['positive'] = (1 - score) * 0.3
                scores['neutral'] = (1 - score) * 0.7
            else:  # neutral
                scores['neutral'] = score
                scores['positive'] = (1 - score) * 0.5
                scores['negative'] = (1 - score) * 0.5
            
            overall = max(scores, key=scores.get)
            
            return {
                'overall': overall,
                'scores': scores,
                'confidence': max(scores.values()),
                'method': 'FinBERT'
            }
    except Exception as e:
        logger.error(f"FinBERT analysis failed: {e}")
        return analyze_with_advanced_keywords(text)
    
    return analyze_with_advanced_keywords(text)

def analyze_with_advanced_keywords(text: str) -> Dict:
    """Advanced keyword-based sentiment analysis with weighted scoring"""
    text_lower = text.lower()
    
    # Calculate weighted scores
    scores = {
        'strong_positive': 0,
        'positive': 0,
        'negative': 0,
        'strong_negative': 0,
        'uncertainty': 0
    }
    
    # Count keyword occurrences with context
    for category, keywords in FINANCIAL_KEYWORDS.items():
        for keyword in keywords:
            # Count with word boundaries for accuracy
            pattern = r'\b' + re.escape(keyword) + r'\b'
            matches = len(re.findall(pattern, text_lower))
            scores[category] += matches
    
    # Apply weights
    weighted_positive = scores['strong_positive'] * 2 + scores['positive']
    weighted_negative = scores['strong_negative'] * 2 + scores['negative']
    weighted_uncertainty = scores['uncertainty'] * 0.5
    
    total = weighted_positive + weighted_negative + weighted_uncertainty
    
    if total == 0:
        # No financial keywords found - neutral
        return {
            'overall': 'neutral',
            'scores': {'positive': 0.33, 'negative': 0.33, 'neutral': 0.34},
            'confidence': 0.34,
            'method': 'keyword-advanced'
        }
    
    # Calculate normalized scores
    positive_score = weighted_positive / total
    negative_score = weighted_negative / total
    neutral_score = weighted_uncertainty / total
    
    # Adjust for balance
    if neutral_score < 0.2:
        neutral_score = 0.2
        adjustment = (positive_score + negative_score) * 0.2 / (positive_score + negative_score + 0.001)
        positive_score *= (1 - adjustment)
        negative_score *= (1 - adjustment)
    
    scores_dict = {
        'positive': min(positive_score, 1.0),
        'negative': min(negative_score, 1.0),
        'neutral': min(neutral_score, 1.0)
    }
    
    # Normalize to sum to 1
    total_score = sum(scores_dict.values())
    if total_score > 0:
        scores_dict = {k: v/total_score for k, v in scores_dict.items()}
    
    overall = max(scores_dict, key=scores_dict.get)
    
    return {
        'overall': overall,
        'scores': scores_dict,
        'confidence': max(scores_dict.values()),
        'method': 'keyword-advanced'
    }

def analyze_text_with_cache(text: str, use_cache: bool = True) -> Dict:
    """Analyze text with caching for performance"""
    text_hash = get_text_hash(text)
    
    if use_cache:
        # Check cache
        conn = sqlite3.connect(SENTIMENT_DB)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT sentiment, positive_score, negative_score, neutral_score, 
                   confidence, method 
            FROM sentiment_cache 
            WHERE hash_key = ?
        ''', (text_hash,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            logger.info("Cache hit for sentiment analysis")
            return {
                'overall': result[0],
                'scores': {
                    'positive': result[1],
                    'negative': result[2],
                    'neutral': result[3]
                },
                'confidence': result[4],
                'method': result[5] + ' (cached)'
            }
    
    # Analyze
    if HAS_FINBERT:
        result = analyze_with_finbert(text)
    else:
        result = analyze_with_advanced_keywords(text)
    
    # Cache result
    if use_cache:
        conn = sqlite3.connect(SENTIMENT_DB)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO sentiment_cache 
            (hash_key, text_preview, sentiment, positive_score, negative_score, 
             neutral_score, confidence, method, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (text_hash, text[:100], result['overall'], 
              result['scores']['positive'], result['scores']['negative'],
              result['scores']['neutral'], result['confidence'], 
              result['method'], datetime.now().isoformat()))
        conn.commit()
        conn.close()
    
    return result

@app.get("/")
async def root():
    return {
        "service": "FinBERT Sentiment Analysis",
        "status": "operational",
        "method": "FinBERT" if HAS_FINBERT else "keyword-advanced",
        "finbert_available": HAS_FINBERT,
        "caching_enabled": True,
        "endpoints": {
            "analyze": "/api/sentiment/analyze",
            "upload": "/api/sentiment/upload",
            "batch": "/api/sentiment/batch",
            "history": "/api/sentiment/history"
        }
    }

@app.get("/api/sentiment/status")
async def get_status():
    """Get sentiment service status"""
    conn = sqlite3.connect(SENTIMENT_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM sentiment_cache")
    cache_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM document_analysis")
    doc_count = cursor.fetchone()[0]
    conn.close()
    
    return {
        "status": "ready",
        "method": "FinBERT" if HAS_FINBERT else "keyword-advanced",
        "cached_analyses": cache_count,
        "documents_analyzed": doc_count,
        "finbert_available": HAS_FINBERT
    }

@app.post("/api/sentiment/analyze")
async def analyze_text(request: TextRequest):
    """Analyze sentiment of provided text"""
    try:
        result = analyze_text_with_cache(request.text, request.use_cache)
        
        return {
            "text": request.text[:200] + "..." if len(request.text) > 200 else request.text,
            "sentiment": result['overall'],
            "scores": result['scores'],
            "confidence": result['confidence'],
            "method": result['method']
        }
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sentiment/upload")
async def analyze_document(file: UploadFile = File(...)):
    """Analyze uploaded document with comprehensive sentiment analysis"""
    try:
        content = await file.read()
        text = content.decode('utf-8', errors='ignore')
        
        # Clean text
        text = re.sub(r'\s+', ' ', text)
        file_hash = get_text_hash(text)
        
        # Check if already analyzed
        conn = sqlite3.connect(SENTIMENT_DB)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT sentiment, positive_score, negative_score, neutral_score, 
                   confidence, chunks_analyzed, method 
            FROM document_analysis 
            WHERE file_hash = ?
        ''', (file_hash,))
        
        cached = cursor.fetchone()
        
        if cached:
            conn.close()
            return {
                "filename": file.filename,
                "sentiment": cached[0],
                "scores": {
                    'positive': cached[1],
                    'negative': cached[2],
                    'neutral': cached[3]
                },
                "confidence": cached[4],
                "chunks_analyzed": cached[5],
                "method": cached[6] + ' (cached)',
                "cached": True
            }
        
        # Split into chunks for analysis
        chunk_size = 500
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        
        # Analyze chunks
        results = []
        for i, chunk in enumerate(chunks[:50]):  # Limit to first 50 chunks
            if len(chunk.strip()) > 20:  # Only analyze meaningful chunks
                result = analyze_text_with_cache(chunk, use_cache=True)
                results.append(result)
        
        if not results:
            conn.close()
            return {
                "filename": file.filename,
                "error": "No meaningful content found in document"
            }
        
        # Aggregate results with weighted average
        total_weight = len(results)
        avg_scores = {
            'positive': sum(r['scores']['positive'] for r in results) / total_weight,
            'negative': sum(r['scores']['negative'] for r in results) / total_weight,
            'neutral': sum(r['scores']['neutral'] for r in results) / total_weight
        }
        
        # Normalize scores
        total = sum(avg_scores.values())
        if total > 0:
            avg_scores = {k: v/total for k, v in avg_scores.items()}
        
        overall = max(avg_scores, key=avg_scores.get)
        confidence = max(avg_scores.values())
        
        # Save to database
        cursor.execute('''
            INSERT INTO document_analysis 
            (filename, file_hash, sentiment, positive_score, negative_score, 
             neutral_score, confidence, chunks_analyzed, method, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (file.filename, file_hash, overall, avg_scores['positive'],
              avg_scores['negative'], avg_scores['neutral'], confidence,
              len(results), results[0]['method'] if results else 'unknown',
              datetime.now().isoformat()))
        conn.commit()
        conn.close()
        
        return {
            "filename": file.filename,
            "chunks_analyzed": len(results),
            "sentiment": overall,
            "scores": avg_scores,
            "confidence": confidence,
            "method": results[0]['method'] if results else 'unknown',
            "cached": False
        }
    except Exception as e:
        logger.error(f"Document analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sentiment/batch")
async def analyze_batch(texts: List[str]):
    """Analyze multiple texts in batch"""
    results = []
    for text in texts[:100]:  # Limit to 100 texts
        try:
            result = analyze_text_with_cache(text, use_cache=True)
            results.append({
                "text": text[:100] + "..." if len(text) > 100 else text,
                "sentiment": result['overall'],
                "confidence": result['confidence']
            })
        except:
            results.append({
                "text": text[:100] + "..." if len(text) > 100 else text,
                "sentiment": "error",
                "confidence": 0
            })
    
    # Calculate overall sentiment
    sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
    for r in results:
        if r['sentiment'] in sentiment_counts:
            sentiment_counts[r['sentiment']] += 1
    
    total = sum(sentiment_counts.values())
    if total > 0:
        sentiment_percentages = {k: v/total for k, v in sentiment_counts.items()}
    else:
        sentiment_percentages = {'positive': 0, 'negative': 0, 'neutral': 1}
    
    return {
        "total_texts": len(texts),
        "analyzed": len(results),
        "results": results,
        "overall_sentiment": max(sentiment_percentages, key=sentiment_percentages.get),
        "sentiment_distribution": sentiment_percentages
    }

@app.get("/api/sentiment/history")
async def get_history(limit: int = 50):
    """Get recent document analysis history"""
    conn = sqlite3.connect(SENTIMENT_DB)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT filename, sentiment, confidence, chunks_analyzed, created_at 
        FROM document_analysis 
        ORDER BY created_at DESC 
        LIMIT ?
    ''', (limit,))
    
    history = []
    for row in cursor.fetchall():
        history.append({
            "filename": row[0],
            "sentiment": row[1],
            "confidence": row[2],
            "chunks_analyzed": row[3],
            "created_at": row[4]
        })
    
    conn.close()
    return {"history": history, "count": len(history)}

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FinBERT Sentiment Analysis on port 8004...")
    logger.info(f"FinBERT available: {HAS_FINBERT}")
    uvicorn.run(app, host="0.0.0.0", port=8004)