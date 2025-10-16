#!/usr/bin/env python3
"""
Document Analysis Module with FinBERT
Provides consistent sentiment analysis with caching
"""

import hashlib
import json
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Try to import document processing libraries
try:
    import PyPDF2
    import docx
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    logger.warning("PyPDF2/python-docx not installed")

# Try to import FinBERT
try:
    from transformers import pipeline
    import torch
    FINBERT_AVAILABLE = True
except ImportError:
    FINBERT_AVAILABLE = False
    logger.warning("FinBERT not available - install transformers and torch")

# Initialize FinBERT if available
finbert_analyzer = None
if FINBERT_AVAILABLE:
    try:
        finbert_analyzer = pipeline(
            "sentiment-analysis",
            model="ProsusAI/finbert",
            tokenizer="ProsusAI/finbert",
            device=0 if torch.cuda.is_available() else -1
        )
        logger.info("FinBERT loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load FinBERT: {e}")
        FINBERT_AVAILABLE = False

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF file"""
    if not PDF_SUPPORT:
        return "PDF support not available"
    
    text = ""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        logger.error(f"Error extracting PDF: {e}")
    return text

def extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX file"""
    if not PDF_SUPPORT:
        return "DOCX support not available"
    
    text = ""
    try:
        doc = docx.Document(file_path)
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
    except Exception as e:
        logger.error(f"Error extracting DOCX: {e}")
    return text

def extract_text(file_path: str, filename: str) -> str:
    """Extract text based on file type"""
    ext = Path(filename).suffix.lower()
    
    if ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif ext in ['.docx', '.doc']:
        return extract_text_from_docx(file_path)
    elif ext in ['.txt', '.csv']:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading text file: {e}")
            return ""
    else:
        return "Unsupported file type"

def analyze_sentiment(text: str) -> Dict[str, Any]:
    """Analyze sentiment using FinBERT - returns consistent results"""
    if not FINBERT_AVAILABLE or not finbert_analyzer:
        return {
            "sentiment": "neutral",
            "confidence": 0.0,
            "message": "FinBERT not available"
        }
    
    try:
        # Truncate text to first 512 tokens for consistency
        words = text.split()[:100]
        truncated_text = ' '.join(words)
        
        # Get sentiment
        result = finbert_analyzer(truncated_text)[0]
        
        return {
            "sentiment": result['label'].lower(),
            "confidence": round(result['score'], 3)
        }
    except Exception as e:
        logger.error(f"Sentiment analysis error: {e}")
        return {"sentiment": "error", "confidence": 0.0}

def analyze_document(file_path: str, filename: str, cache_dir: Path) -> Dict[str, Any]:
    """Analyze document with caching for consistent results"""
    # Generate file hash for caching
    file_hash = hashlib.md5(open(file_path, 'rb').read()).hexdigest()
    cache_file = cache_dir / f"{file_hash}.json"
    
    # Check cache first
    if cache_file.exists():
        logger.info(f"Using cached analysis for {filename}")
        with open(cache_file, 'r') as f:
            return json.load(f)
    
    # Extract text
    text = extract_text(file_path, filename)
    
    # Perform sentiment analysis
    sentiment_result = analyze_sentiment(text)
    
    # Create analysis result
    analysis_result = {
        "filename": filename,
        "file_hash": file_hash,
        "analysis": {
            "sentiment": sentiment_result["sentiment"],
            "confidence": sentiment_result["confidence"],
            "summary": ' '.join(text.split()[:50]) + "..." if len(text.split()) > 50 else text,
            "word_count": len(text.split())
        }
    }
    
    # Save to cache
    with open(cache_file, 'w') as f:
        json.dump(analysis_result, f, indent=2)
    
    return analysis_result