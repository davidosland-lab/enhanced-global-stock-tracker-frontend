#!/usr/bin/env python3
"""
FinBERT Sentiment Analyzer for Financial Text
Can be used standalone or through MCP server
"""

import os
import json
import logging
from typing import Dict, List, Optional, Union
from datetime import datetime
import numpy as np

logger = logging.getLogger(__name__)

# Check if transformers is available
try:
    from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
    import torch
    FINBERT_AVAILABLE = True
except ImportError:
    FINBERT_AVAILABLE = False
    logger.warning("FinBERT requires: pip install transformers torch")

class FinBERTAnalyzer:
    """
    Financial sentiment analyzer using FinBERT
    Pre-trained on financial text for accurate sentiment analysis
    """
    
    def __init__(self, model_name: str = "ProsusAI/finbert"):
        """
        Initialize FinBERT analyzer
        
        Args:
            model_name: HuggingFace model name (default: ProsusAI/finbert)
                       Alternatives: "yiyanghkust/finbert-tone", "ahmedrachid/FinancialBERT"
        """
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.pipeline = None
        
        if FINBERT_AVAILABLE:
            self._load_model()
        else:
            logger.error("FinBERT not available. Install with: pip install transformers torch")
    
    def _load_model(self):
        """Load FinBERT model and create pipeline"""
        try:
            logger.info(f"Loading FinBERT model: {self.model_name}")
            
            # Check if CUDA is available
            device = 0 if torch.cuda.is_available() else -1
            
            # Create sentiment analysis pipeline
            self.pipeline = pipeline(
                "sentiment-analysis",
                model=self.model_name,
                device=device
            )
            
            # Also load model directly for more control
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            
            if torch.cuda.is_available():
                self.model = self.model.cuda()
                logger.info("✅ FinBERT loaded on GPU")
            else:
                logger.info("✅ FinBERT loaded on CPU")
                
        except Exception as e:
            logger.error(f"Failed to load FinBERT: {e}")
            self.pipeline = None
    
    def analyze(self, text: Union[str, List[str]], batch_size: int = 8) -> Union[Dict, List[Dict]]:
        """
        Analyze sentiment of financial text
        
        Args:
            text: Single text string or list of texts
            batch_size: Batch size for processing multiple texts
            
        Returns:
            Sentiment analysis results with scores
        """
        if not FINBERT_AVAILABLE or not self.pipeline:
            return self._fallback_analysis(text)
        
        try:
            # Handle single text
            if isinstance(text, str):
                results = self.pipeline(text, truncation=True, max_length=512)
                return self._format_result(results[0], text)
            
            # Handle multiple texts
            all_results = []
            for i in range(0, len(text), batch_size):
                batch = text[i:i+batch_size]
                results = self.pipeline(batch, truncation=True, max_length=512)
                
                for txt, res in zip(batch, results):
                    all_results.append(self._format_result(res, txt))
            
            return all_results
            
        except Exception as e:
            logger.error(f"Error in FinBERT analysis: {e}")
            return self._fallback_analysis(text)
    
    def _format_result(self, raw_result: Dict, original_text: str) -> Dict:
        """Format pipeline result into consistent structure"""
        
        # Map FinBERT labels to standard sentiment
        label_map = {
            'positive': 'positive',
            'negative': 'negative',
            'neutral': 'neutral',
            'LABEL_0': 'positive',  # Some models use LABEL_X
            'LABEL_1': 'negative',
            'LABEL_2': 'neutral'
        }
        
        sentiment = label_map.get(raw_result['label'], raw_result['label'].lower())
        
        return {
            'text': original_text[:200] + '...' if len(original_text) > 200 else original_text,
            'sentiment': sentiment,
            'confidence': raw_result['score'],
            'model': self.model_name,
            'timestamp': datetime.now().isoformat()
        }
    
    def _fallback_analysis(self, text: Union[str, List[str]]) -> Union[Dict, List[Dict]]:
        """Fallback sentiment analysis using keywords when FinBERT unavailable"""
        
        positive_words = {
            'beat', 'exceed', 'outperform', 'surge', 'rally', 'gain', 'profit',
            'growth', 'upgrade', 'bullish', 'strong', 'record', 'high', 'rise'
        }
        
        negative_words = {
            'miss', 'decline', 'fall', 'loss', 'weak', 'concern', 'risk',
            'downgrade', 'bearish', 'low', 'cut', 'reduce', 'warning', 'drop'
        }
        
        def analyze_single(t):
            t_lower = t.lower()
            pos_count = sum(1 for word in positive_words if word in t_lower)
            neg_count = sum(1 for word in negative_words if word in t_lower)
            
            if pos_count > neg_count:
                sentiment = 'positive'
                confidence = min(0.5 + (pos_count - neg_count) * 0.1, 0.9)
            elif neg_count > pos_count:
                sentiment = 'negative'
                confidence = min(0.5 + (neg_count - pos_count) * 0.1, 0.9)
            else:
                sentiment = 'neutral'
                confidence = 0.5
            
            return {
                'text': t[:200] + '...' if len(t) > 200 else t,
                'sentiment': sentiment,
                'confidence': confidence,
                'model': 'keyword_fallback',
                'timestamp': datetime.now().isoformat()
            }
        
        if isinstance(text, str):
            return analyze_single(text)
        else:
            return [analyze_single(t) for t in text]
    
    def analyze_news_headlines(self, headlines: List[str]) -> Dict:
        """
        Analyze multiple news headlines and provide aggregate sentiment
        
        Args:
            headlines: List of news headlines
            
        Returns:
            Aggregate sentiment analysis with distribution
        """
        if not headlines:
            return {
                'overall_sentiment': 'neutral',
                'confidence': 0.0,
                'distribution': {'positive': 0, 'negative': 0, 'neutral': 0}
            }
        
        # Analyze all headlines
        results = self.analyze(headlines)
        if not isinstance(results, list):
            results = [results]
        
        # Calculate distribution
        sentiments = [r['sentiment'] for r in results]
        distribution = {
            'positive': sentiments.count('positive'),
            'negative': sentiments.count('negative'),
            'neutral': sentiments.count('neutral')
        }
        
        # Calculate weighted sentiment score
        scores = {
            'positive': 1.0,
            'neutral': 0.0,
            'negative': -1.0
        }
        
        weighted_score = sum(scores[r['sentiment']] * r['confidence'] for r in results)
        weighted_score /= len(results)
        
        # Determine overall sentiment
        if weighted_score > 0.2:
            overall = 'positive'
        elif weighted_score < -0.2:
            overall = 'negative'
        else:
            overall = 'neutral'
        
        # Average confidence
        avg_confidence = np.mean([r['confidence'] for r in results])
        
        return {
            'overall_sentiment': overall,
            'weighted_score': float(weighted_score),
            'confidence': float(avg_confidence),
            'distribution': distribution,
            'total_analyzed': len(headlines),
            'individual_results': results
        }
    
    def analyze_earnings_call(self, transcript: str, chunk_size: int = 512) -> Dict:
        """
        Analyze long earnings call transcript
        
        Args:
            transcript: Full earnings call transcript
            chunk_size: Size of text chunks for analysis
            
        Returns:
            Sentiment analysis of entire transcript
        """
        # Split transcript into chunks
        words = transcript.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size):
            chunk = ' '.join(words[i:i+chunk_size])
            chunks.append(chunk)
        
        # Analyze all chunks
        results = self.analyze(chunks)
        if not isinstance(results, list):
            results = [results]
        
        # Aggregate results
        sentiments = [r['sentiment'] for r in results]
        
        # Calculate time-weighted sentiment (later parts might be more important)
        weights = np.linspace(0.8, 1.2, len(results))  # Weight later chunks higher
        
        sentiment_scores = {
            'positive': sum(w for w, s in zip(weights, sentiments) if s == 'positive'),
            'negative': sum(w for w, s in zip(weights, sentiments) if s == 'negative'),
            'neutral': sum(w for w, s in zip(weights, sentiments) if s == 'neutral')
        }
        
        overall = max(sentiment_scores, key=sentiment_scores.get)
        
        return {
            'overall_sentiment': overall,
            'sentiment_progression': sentiments,  # How sentiment changed through call
            'chunk_count': len(chunks),
            'distribution': {
                'positive': sentiments.count('positive'),
                'negative': sentiments.count('negative'),
                'neutral': sentiments.count('neutral')
            },
            'confidence': float(np.mean([r['confidence'] for r in results]))
        }


class FinBERTMLIntegration:
    """
    Integration of FinBERT with ML stock prediction
    Adds sentiment as a feature for predictions
    """
    
    def __init__(self):
        self.analyzer = FinBERTAnalyzer()
        self.sentiment_cache = {}
    
    def get_sentiment_feature(self, symbol: str, texts: List[str]) -> float:
        """
        Convert sentiment analysis to numerical feature for ML
        
        Args:
            symbol: Stock symbol
            texts: List of texts to analyze (news, tweets, etc.)
            
        Returns:
            Sentiment score between -1 (negative) and 1 (positive)
        """
        # Check cache
        cache_key = f"{symbol}_{len(texts)}"
        if cache_key in self.sentiment_cache:
            cache_time, score = self.sentiment_cache[cache_key]
            if (datetime.now() - cache_time).seconds < 3600:  # 1 hour cache
                return score
        
        # Analyze texts
        result = self.analyzer.analyze_news_headlines(texts)
        
        # Convert to numerical score
        score = result['weighted_score'] if 'weighted_score' in result else 0.0
        
        # Cache result
        self.sentiment_cache[cache_key] = (datetime.now(), score)
        
        return score
    
    def enhance_features_with_sentiment(self, df, symbol: str, news_texts: List[str] = None) -> pd.DataFrame:
        """
        Add sentiment features to existing technical indicators
        
        Args:
            df: DataFrame with OHLCV data and technical indicators
            symbol: Stock symbol
            news_texts: Optional list of news texts
            
        Returns:
            DataFrame with added sentiment features
        """
        import pandas as pd
        
        if news_texts:
            # Get sentiment score
            sentiment_score = self.get_sentiment_feature(symbol, news_texts)
            
            # Add as feature
            df['sentiment_score'] = sentiment_score
            
            # Add rolling sentiment (would need historical news)
            df['sentiment_ma_5'] = sentiment_score  # Placeholder
            df['sentiment_ma_20'] = sentiment_score  # Placeholder
            
            logger.info(f"✅ Added sentiment features (score: {sentiment_score:.3f})")
        else:
            # No sentiment data available
            df['sentiment_score'] = 0.0
            df['sentiment_ma_5'] = 0.0
            df['sentiment_ma_20'] = 0.0
            logger.info("ℹ️ No sentiment data, using neutral values")
        
        return df


# ==================== USAGE EXAMPLES ====================
def example_basic_usage():
    """Example of basic FinBERT usage"""
    
    analyzer = FinBERTAnalyzer()
    
    # Single text analysis
    text = "Apple reported better than expected earnings, beating analyst estimates by 15%"
    result = analyzer.analyze(text)
    print(f"Sentiment: {result['sentiment']} (confidence: {result['confidence']:.2%})")
    
    # Multiple headlines
    headlines = [
        "Stock market crashes amid recession fears",
        "Tech stocks rally on strong earnings",
        "Federal Reserve maintains interest rates",
        "Unemployment rises to 5-year high",
        "Microsoft announces record profits"
    ]
    
    aggregate = analyzer.analyze_news_headlines(headlines)
    print(f"\nOverall Market Sentiment: {aggregate['overall_sentiment']}")
    print(f"Distribution: {aggregate['distribution']}")
    print(f"Confidence: {aggregate['confidence']:.2%}")


def example_ml_integration():
    """Example of integrating FinBERT with ML predictions"""
    
    integration = FinBERTMLIntegration()
    
    # Sample news for Apple
    apple_news = [
        "Apple unveils new iPhone with breakthrough technology",
        "Analysts upgrade Apple stock to strong buy",
        "Apple faces supply chain challenges in China",
        "iPhone sales exceed expectations in Q4"
    ]
    
    # Get sentiment feature for ML model
    sentiment_score = integration.get_sentiment_feature("AAPL", apple_news)
    print(f"Apple Sentiment Score for ML: {sentiment_score:.3f}")
    
    # This score can now be used as a feature in ML prediction
    # Combined with technical indicators for better predictions


def example_mcp_usage():
    """Example of using FinBERT through MCP"""
    
    print("\nMCP Server Usage:")
    print("-" * 40)
    print("1. Start MCP server: python mcp_integration.py")
    print("2. Use MCP client to analyze sentiment:")
    print("""
    async with MCPClient() as client:
        result = await client.call_tool("analyze_sentiment", {
            "text": "Tesla stock surges on delivery numbers",
            "context": "news"
        })
        print(result)
    """)


if __name__ == "__main__":
    print("="*60)
    print("FinBERT Financial Sentiment Analyzer")
    print("="*60)
    
    if not FINBERT_AVAILABLE:
        print("\n❌ FinBERT not available!")
        print("\nTo install requirements:")
        print("pip install transformers torch")
        print("\nFor GPU support:")
        print("pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
    else:
        print("\n✅ FinBERT is available!")
        print("\nRunning examples...")
        print("-" * 40)
        
        example_basic_usage()
        print("-" * 40)
        example_ml_integration()
        print("-" * 40)
        example_mcp_usage()
    
    print("\n" + "="*60)