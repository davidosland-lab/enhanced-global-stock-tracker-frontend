"""
FinBERT Backend for Real Sentiment Analysis
No fake data - uses actual FinBERT or fallback to keyword analysis
"""

import os
import logging
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import re
from typing import Dict, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import transformers for FinBERT
try:
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    import torch
    HAS_FINBERT = True
    logger.info("FinBERT available - will use real sentiment analysis")
except ImportError:
    HAS_FINBERT = False
    logger.warning("FinBERT not available - using keyword-based fallback")

app = FastAPI(title="FinBERT Sentiment Analysis", version="1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize FinBERT if available
if HAS_FINBERT:
    try:
        tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
        model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
        logger.info("FinBERT model loaded successfully")
    except:
        HAS_FINBERT = False
        logger.error("Failed to load FinBERT model")

class TextRequest(BaseModel):
    text: str

def analyze_with_finbert(text: str) -> Dict:
    """Analyze text using real FinBERT model"""
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    
    with torch.no_grad():
        outputs = model(**inputs)
        predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
        
    positive = predictions[0][0].item()
    negative = predictions[0][1].item()
    neutral = predictions[0][2].item()
    
    # Determine overall sentiment
    sentiments = {'positive': positive, 'negative': negative, 'neutral': neutral}
    overall = max(sentiments, key=sentiments.get)
    
    return {
        'overall': overall,
        'scores': sentiments,
        'confidence': max(sentiments.values()),
        'method': 'FinBERT'
    }

def analyze_with_keywords(text: str) -> Dict:
    """Fallback keyword-based sentiment analysis"""
    text_lower = text.lower()
    
    # Financial keywords
    positive_words = [
        'profit', 'gain', 'growth', 'increase', 'rise', 'surge', 'jump',
        'outperform', 'beat', 'exceed', 'strong', 'robust', 'improve',
        'upgrade', 'buy', 'bullish', 'optimistic', 'record', 'high'
    ]
    
    negative_words = [
        'loss', 'decline', 'fall', 'drop', 'decrease', 'plunge', 'crash',
        'underperform', 'miss', 'weak', 'poor', 'downgrade', 'sell',
        'bearish', 'pessimistic', 'low', 'risk', 'concern', 'warning'
    ]
    
    # Count occurrences
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    # Calculate scores
    total_keywords = positive_count + negative_count
    if total_keywords == 0:
        return {
            'overall': 'neutral',
            'scores': {'positive': 0.33, 'negative': 0.33, 'neutral': 0.34},
            'confidence': 0.34,
            'method': 'keyword-based'
        }
    
    positive_score = positive_count / total_keywords
    negative_score = negative_count / total_keywords
    neutral_score = 1 - (positive_score + negative_score)
    
    scores = {
        'positive': positive_score,
        'negative': negative_score,
        'neutral': abs(neutral_score)
    }
    
    overall = max(scores, key=scores.get)
    
    return {
        'overall': overall,
        'scores': scores,
        'confidence': max(scores.values()),
        'method': 'keyword-based'
    }

@app.get("/")
async def root():
    return {
        "service": "FinBERT Sentiment Analysis",
        "status": "operational",
        "method": "FinBERT" if HAS_FINBERT else "keyword-based",
        "endpoints": {
            "analyze": "/api/sentiment/analyze",
            "upload": "/api/sentiment/upload"
        }
    }

@app.post("/api/sentiment/analyze")
async def analyze_text(request: TextRequest):
    """Analyze sentiment of provided text"""
    try:
        if HAS_FINBERT:
            result = analyze_with_finbert(request.text)
        else:
            result = analyze_with_keywords(request.text)
        
        return {
            "text": request.text[:100] + "..." if len(request.text) > 100 else request.text,
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
    """Analyze uploaded document"""
    try:
        content = await file.read()
        text = content.decode('utf-8', errors='ignore')
        
        # Clean text
        text = re.sub(r'\s+', ' ', text)
        
        # Split into chunks for analysis
        chunks = [text[i:i+500] for i in range(0, len(text), 500)]
        
        results = []
        for chunk in chunks[:10]:  # Analyze first 10 chunks
            if HAS_FINBERT:
                result = analyze_with_finbert(chunk)
            else:
                result = analyze_with_keywords(chunk)
            results.append(result)
        
        # Aggregate results
        avg_scores = {
            'positive': sum(r['scores']['positive'] for r in results) / len(results),
            'negative': sum(r['scores']['negative'] for r in results) / len(results),
            'neutral': sum(r['scores']['neutral'] for r in results) / len(results)
        }
        
        overall = max(avg_scores, key=avg_scores.get)
        
        return {
            "filename": file.filename,
            "chunks_analyzed": len(results),
            "sentiment": overall,
            "scores": avg_scores,
            "confidence": max(avg_scores.values()),
            "method": results[0]['method'] if results else 'unknown'
        }
    except Exception as e:
        logger.error(f"Document analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FinBERT backend on port 8004...")
    uvicorn.run(app, host="0.0.0.0", port=8004)