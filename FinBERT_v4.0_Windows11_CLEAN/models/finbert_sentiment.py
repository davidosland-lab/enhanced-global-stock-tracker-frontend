"""
FinBERT Sentiment Analyzer Module
Financial sentiment analysis using FinBERT pre-trained model
FinBERT v4.0 - Enhanced with fallback mechanisms
"""

import logging
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

# Try to import transformers for FinBERT
try:
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    import torch
    FINBERT_AVAILABLE = True
    logger.info("FinBERT libraries loaded successfully")
except (ImportError, ValueError, Exception) as e:
    FINBERT_AVAILABLE = False
    logger.warning(f"FinBERT libraries not available: {e}. Sentiment analysis will use fallback method.")

class FinBERTSentimentAnalyzer:
    """
    Financial sentiment analyzer using FinBERT model
    Provides sentiment scores for financial text with fallback mechanisms
    """
    
    def __init__(self, model_name: str = "ProsusAI/finbert"):
        """
        Initialize FinBERT sentiment analyzer
        
        Args:
            model_name: HuggingFace model name for FinBERT
        """
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.is_loaded = False
        self.use_fallback = not FINBERT_AVAILABLE
        
        # Sentiment labels
        self.labels = ['negative', 'neutral', 'positive']
        
        # Load model if available
        if FINBERT_AVAILABLE:
            self._load_model()
        else:
            logger.info("Using fallback sentiment analysis (keyword-based)")
    
    def _load_model(self) -> bool:
        """
        Load FinBERT model and tokenizer
        
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Loading FinBERT model: {self.model_name}")
            
            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            
            # Set to evaluation mode
            self.model.eval()
            
            self.is_loaded = True
            self.use_fallback = False
            logger.info("FinBERT model loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load FinBERT model: {e}")
            logger.info("Falling back to keyword-based sentiment analysis")
            self.use_fallback = True
            return False
    
    def analyze_text(self, text: str) -> Dict:
        """
        Analyze sentiment of financial text
        
        Args:
            text: Financial text to analyze
        
        Returns:
            Dictionary with sentiment scores and label
        """
        if not text or len(text.strip()) == 0:
            return self._get_neutral_sentiment()
        
        # Use FinBERT if available
        if self.is_loaded and not self.use_fallback:
            return self._finbert_analysis(text)
        else:
            return self._fallback_analysis(text)
    
    def _finbert_analysis(self, text: str) -> Dict:
        """
        Perform sentiment analysis using FinBERT model
        
        Args:
            text: Text to analyze
        
        Returns:
            Sentiment analysis results
        """
        try:
            # Tokenize input
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512
            )
            
            # Get predictions
            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
            
            # Convert to probabilities
            probs = predictions[0].cpu().numpy()
            
            # Get dominant sentiment
            dominant_idx = np.argmax(probs)
            dominant_label = self.labels[dominant_idx]
            confidence = float(probs[dominant_idx])
            
            # Calculate compound score (-1 to 1)
            compound_score = float(probs[2] - probs[0])  # positive - negative
            
            return {
                'sentiment': dominant_label,
                'confidence': round(confidence * 100, 2),
                'scores': {
                    'negative': round(float(probs[0]), 4),
                    'neutral': round(float(probs[1]), 4),
                    'positive': round(float(probs[2]), 4)
                },
                'compound': round(compound_score, 4),
                'method': 'FinBERT',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"FinBERT analysis error: {e}")
            return self._fallback_analysis(text)
    
    def _fallback_analysis(self, text: str) -> Dict:
        """
        Fallback sentiment analysis using keyword matching
        
        Args:
            text: Text to analyze
        
        Returns:
            Sentiment analysis results
        """
        text_lower = text.lower()
        
        # Financial keywords
        positive_keywords = [
            'bullish', 'growth', 'profit', 'gain', 'surge', 'rally', 'boom',
            'strong', 'beat', 'exceed', 'outperform', 'upgrade', 'positive',
            'buy', 'upside', 'momentum', 'breakout', 'recovery', 'improve',
            'success', 'win', 'rise', 'increase', 'high', 'good', 'excellent'
        ]
        
        negative_keywords = [
            'bearish', 'loss', 'decline', 'fall', 'crash', 'drop', 'plunge',
            'weak', 'miss', 'underperform', 'downgrade', 'negative', 'sell',
            'risk', 'concern', 'warning', 'volatile', 'uncertainty', 'fear',
            'failure', 'lose', 'decrease', 'low', 'bad', 'poor', 'worst'
        ]
        
        # Count keyword occurrences
        positive_count = sum(1 for keyword in positive_keywords if keyword in text_lower)
        negative_count = sum(1 for keyword in negative_keywords if keyword in text_lower)
        total_count = positive_count + negative_count
        
        if total_count == 0:
            return self._get_neutral_sentiment()
        
        # Calculate scores
        positive_score = positive_count / total_count if total_count > 0 else 0.33
        negative_score = negative_count / total_count if total_count > 0 else 0.33
        neutral_score = 1.0 - (positive_score + negative_score)
        
        # Ensure scores sum to 1
        total = positive_score + negative_score + neutral_score
        if total > 0:
            positive_score /= total
            negative_score /= total
            neutral_score /= total
        
        # Determine dominant sentiment
        scores = {
            'positive': positive_score,
            'negative': negative_score,
            'neutral': neutral_score
        }
        dominant_label = max(scores, key=scores.get)
        confidence = scores[dominant_label]
        
        # Calculate compound score
        compound_score = positive_score - negative_score
        
        return {
            'sentiment': dominant_label,
            'confidence': round(confidence * 100, 2),
            'scores': {
                'negative': round(negative_score, 4),
                'neutral': round(neutral_score, 4),
                'positive': round(positive_score, 4)
            },
            'compound': round(compound_score, 4),
            'method': 'Keyword-based (Fallback)',
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_neutral_sentiment(self) -> Dict:
        """Return neutral sentiment when no text provided"""
        return {
            'sentiment': 'neutral',
            'confidence': 100.0,
            'scores': {
                'negative': 0.0,
                'neutral': 1.0,
                'positive': 0.0
            },
            'compound': 0.0,
            'method': 'Default',
            'timestamp': datetime.now().isoformat()
        }
    
    def analyze_news_batch(self, news_items: List[str]) -> Dict:
        """
        Analyze sentiment for multiple news items
        
        Args:
            news_items: List of news headlines/texts
        
        Returns:
            Aggregated sentiment analysis
        """
        if not news_items or len(news_items) == 0:
            return self._get_neutral_sentiment()
        
        # Analyze each item
        sentiments = []
        for item in news_items:
            if item and len(item.strip()) > 0:
                sentiment = self.analyze_text(item)
                sentiments.append(sentiment)
        
        if len(sentiments) == 0:
            return self._get_neutral_sentiment()
        
        # Aggregate results
        avg_negative = np.mean([s['scores']['negative'] for s in sentiments])
        avg_neutral = np.mean([s['scores']['neutral'] for s in sentiments])
        avg_positive = np.mean([s['scores']['positive'] for s in sentiments])
        avg_compound = np.mean([s['compound'] for s in sentiments])
        
        # Determine overall sentiment
        scores = {
            'negative': avg_negative,
            'neutral': avg_neutral,
            'positive': avg_positive
        }
        dominant_label = max(scores, key=scores.get)
        confidence = scores[dominant_label]
        
        return {
            'sentiment': dominant_label,
            'confidence': round(confidence * 100, 2),
            'scores': {
                'negative': round(avg_negative, 4),
                'neutral': round(avg_neutral, 4),
                'positive': round(avg_positive, 4)
            },
            'compound': round(avg_compound, 4),
            'news_count': len(sentiments),
            'method': sentiments[0]['method'] if sentiments else 'Unknown',
            'timestamp': datetime.now().isoformat()
        }
    
    def get_sentiment_signal(self, compound_score: float) -> Tuple[str, str]:
        """
        Convert compound sentiment score to trading signal
        
        Args:
            compound_score: Compound sentiment score (-1 to 1)
        
        Returns:
            Tuple of (signal, strength)
        """
        if compound_score > 0.3:
            return ('BUY', 'Strong' if compound_score > 0.6 else 'Moderate')
        elif compound_score < -0.3:
            return ('SELL', 'Strong' if compound_score < -0.6 else 'Moderate')
        else:
            return ('HOLD', 'Weak')
    
    # REMOVED: get_mock_sentiment() method - Use real news data from news_sentiment_real.py instead
    # Never use mock/fake sentiment data in production


# Singleton instance
finbert_analyzer = FinBERTSentimentAnalyzer()

def get_sentiment_analysis(text: str) -> Dict:
    """
    Convenience function to get sentiment analysis
    
    Args:
        text: Text to analyze
    
    Returns:
        Sentiment analysis results
    """
    return finbert_analyzer.analyze_text(text)

def get_batch_sentiment(news_items: List[str]) -> Dict:
    """
    Convenience function for batch sentiment analysis
    
    Args:
        news_items: List of news texts
    
    Returns:
        Aggregated sentiment results
    """
    return finbert_analyzer.analyze_news_batch(news_items)
