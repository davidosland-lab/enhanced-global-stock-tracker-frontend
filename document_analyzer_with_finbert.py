#!/usr/bin/env python3
"""
Document Analyzer with FinBERT Sentiment Analysis
Provides consistent financial sentiment analysis for uploaded documents
"""

import os
import json
import hashlib
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# For text extraction
import PyPDF2
import docx
import pandas as pd

# For sentiment analysis
try:
    from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
    import torch
    FINBERT_AVAILABLE = True
except ImportError:
    FINBERT_AVAILABLE = False
    print("WARNING: transformers library not installed. Install with: pip install transformers torch")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Document Analyzer API with FinBERT", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create necessary directories
UPLOAD_DIR = Path("uploads")
ANALYSIS_CACHE_DIR = Path("analysis_cache")
UPLOAD_DIR.mkdir(exist_ok=True)
ANALYSIS_CACHE_DIR.mkdir(exist_ok=True)

# Initialize FinBERT model if available
finbert_analyzer = None
if FINBERT_AVAILABLE:
    try:
        logger.info("Loading FinBERT model...")
        # Use FinBERT for financial sentiment analysis
        finbert_analyzer = pipeline(
            "sentiment-analysis",
            model="ProsusAI/finbert",
            tokenizer="ProsusAI/finbert",
            device=0 if torch.cuda.is_available() else -1
        )
        logger.info("FinBERT model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load FinBERT: {e}")
        FINBERT_AVAILABLE = False

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF file"""
    text = ""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
    return text

def extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX file"""
    text = ""
    try:
        doc = docx.Document(file_path)
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
    except Exception as e:
        logger.error(f"Error extracting text from DOCX: {e}")
    return text

def extract_text_from_txt(file_path: str) -> str:
    """Extract text from TXT file"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            return file.read()
    except Exception as e:
        logger.error(f"Error reading text file: {e}")
        return ""

def extract_text_from_csv(file_path: str) -> str:
    """Extract text from CSV file"""
    try:
        df = pd.read_csv(file_path)
        return df.to_string()
    except Exception as e:
        logger.error(f"Error reading CSV file: {e}")
        return ""

def extract_text(file_path: str, file_extension: str) -> str:
    """Extract text based on file type"""
    ext = file_extension.lower()
    
    if ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif ext in ['.docx', '.doc']:
        return extract_text_from_docx(file_path)
    elif ext == '.txt':
        return extract_text_from_txt(file_path)
    elif ext == '.csv':
        return extract_text_from_csv(file_path)
    else:
        # Try to read as text
        return extract_text_from_txt(file_path)

def get_file_hash(file_path: str) -> str:
    """Generate hash for file to use as cache key"""
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def analyze_sentiment_with_finbert(text: str, max_length: int = 512) -> Dict[str, Any]:
    """
    Analyze sentiment using FinBERT model
    Returns consistent results by using deterministic processing
    """
    if not FINBERT_AVAILABLE or not finbert_analyzer:
        return {
            "overall_sentiment": "neutral",
            "confidence": 0.0,
            "sentiment_scores": {"positive": 0.33, "negative": 0.33, "neutral": 0.34},
            "error": "FinBERT not available"
        }
    
    try:
        # Split text into chunks if too long
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 > max_length:
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_length = len(word)
            else:
                current_chunk.append(word)
                current_length += len(word) + 1
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        # Analyze each chunk
        all_results = []
        for chunk in chunks[:10]:  # Limit to first 10 chunks for consistency
            result = finbert_analyzer(chunk)[0]
            all_results.append(result)
        
        # Aggregate results deterministically
        sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
        total_confidence = 0
        
        for result in all_results:
            label = result['label'].lower()
            sentiment_counts[label] = sentiment_counts.get(label, 0) + result['score']
            total_confidence += result['score']
        
        # Normalize scores
        total = sum(sentiment_counts.values())
        if total > 0:
            sentiment_scores = {k: v/total for k, v in sentiment_counts.items()}
        else:
            sentiment_scores = {"positive": 0.33, "negative": 0.33, "neutral": 0.34}
        
        # Determine overall sentiment
        overall_sentiment = max(sentiment_scores, key=sentiment_scores.get)
        confidence = sentiment_scores[overall_sentiment]
        
        return {
            "overall_sentiment": overall_sentiment,
            "confidence": round(confidence, 3),
            "sentiment_scores": {k: round(v, 3) for k, v in sentiment_scores.items()},
            "chunks_analyzed": len(all_results)
        }
        
    except Exception as e:
        logger.error(f"Error in sentiment analysis: {e}")
        return {
            "overall_sentiment": "neutral",
            "confidence": 0.0,
            "sentiment_scores": {"positive": 0.33, "negative": 0.33, "neutral": 0.34},
            "error": str(e)
        }

def analyze_document(file_path: str, filename: str) -> Dict[str, Any]:
    """
    Analyze document with caching for consistent results
    """
    # Check cache first
    file_hash = get_file_hash(file_path)
    cache_file = ANALYSIS_CACHE_DIR / f"{file_hash}.json"
    
    if cache_file.exists():
        logger.info(f"Using cached analysis for {filename}")
        with open(cache_file, 'r') as f:
            return json.load(f)
    
    # Extract text
    file_extension = Path(filename).suffix
    text = extract_text(file_path, file_extension)
    
    if not text:
        return {
            "filename": filename,
            "analysis": {
                "sentiment": "neutral",
                "summary": "Could not extract text from document",
                "key_points": [],
                "confidence": 0.0
            }
        }
    
    # Perform sentiment analysis
    sentiment_result = analyze_sentiment_with_finbert(text)
    
    # Extract key points (simple implementation)
    sentences = text.split('.')[:5]  # First 5 sentences
    key_points = [s.strip() for s in sentences if len(s.strip()) > 20][:3]
    
    # Generate summary
    words = text.split()[:50]  # First 50 words
    summary = ' '.join(words) + "..." if len(words) == 50 else ' '.join(words)
    
    analysis_result = {
        "filename": filename,
        "file_hash": file_hash,
        "analysis": {
            "sentiment": sentiment_result["overall_sentiment"],
            "confidence": sentiment_result["confidence"],
            "sentiment_scores": sentiment_result["sentiment_scores"],
            "summary": summary,
            "key_points": key_points,
            "word_count": len(text.split()),
            "analyzed_at": datetime.now().isoformat()
        }
    }
    
    # Save to cache
    with open(cache_file, 'w') as f:
        json.dump(analysis_result, f, indent=2)
    
    logger.info(f"Analysis completed and cached for {filename}")
    return analysis_result

@app.get("/")
async def root():
    return {
        "service": "Document Analyzer with FinBERT",
        "status": "active",
        "finbert_available": FINBERT_AVAILABLE,
        "max_file_size": "100MB",
        "supported_formats": [".pdf", ".docx", ".txt", ".csv"],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/status")
async def status():
    return {
        "status": "active",
        "finbert_available": FINBERT_AVAILABLE,
        "max_file_upload": "100MB",
        "cache_size": len(list(ANALYSIS_CACHE_DIR.glob("*.json"))),
        "uploads_count": len(list(UPLOAD_DIR.glob("*")))
    }

@app.post("/api/documents/upload")
async def upload_and_analyze(
    file: UploadFile = File(...),
    documentType: str = Form(default="financial")
):
    """Upload document and perform FinBERT sentiment analysis"""
    try:
        # Check file size (100MB limit)
        contents = await file.read()
        if len(contents) > 100 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File too large. Maximum size is 100MB")
        
        # Save file
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Analyze document
        analysis = analyze_document(str(file_path), file.filename)
        
        # Add upload metadata
        analysis.update({
            "success": True,
            "documentType": documentType,
            "size": len(contents),
            "size_mb": round(len(contents) / (1024 * 1024), 2)
        })
        
        logger.info(f"Document uploaded and analyzed: {file.filename}")
        return analysis
        
    except Exception as e:
        logger.error(f"Upload/analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analysis/clear-cache")
async def clear_cache():
    """Clear analysis cache to force re-analysis"""
    try:
        cache_files = list(ANALYSIS_CACHE_DIR.glob("*.json"))
        for cache_file in cache_files:
            cache_file.unlink()
        
        return {
            "success": True,
            "message": f"Cleared {len(cache_files)} cached analyses",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analysis/history")
async def get_analysis_history():
    """Get history of analyzed documents"""
    try:
        analyses = []
        for cache_file in ANALYSIS_CACHE_DIR.glob("*.json"):
            with open(cache_file, 'r') as f:
                data = json.load(f)
                analyses.append({
                    "filename": data.get("filename"),
                    "sentiment": data["analysis"]["sentiment"],
                    "confidence": data["analysis"]["confidence"],
                    "analyzed_at": data["analysis"].get("analyzed_at", "Unknown")
                })
        
        # Sort by analysis time
        analyses.sort(key=lambda x: x["analyzed_at"], reverse=True)
        
        return {
            "success": True,
            "count": len(analyses),
            "analyses": analyses[:20]  # Return last 20
        }
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = 8004  # Different port for document analyzer
    logger.info(f"Starting Document Analyzer on port {port}")
    logger.info(f"FinBERT Available: {FINBERT_AVAILABLE}")
    
    if not FINBERT_AVAILABLE:
        print("\n" + "="*60)
        print("IMPORTANT: FinBERT is not installed!")
        print("To enable sentiment analysis, install required packages:")
        print("pip install transformers torch sentencepiece protobuf")
        print("="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=port)