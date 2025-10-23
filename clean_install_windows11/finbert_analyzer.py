"""
Real FinBERT Sentiment Analysis Implementation
Uses HuggingFace Transformers for actual financial sentiment analysis
"""

import logging
from typing import Dict, List, Optional, Union
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import transformers, fall back to demo mode if not available
try:
    from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
    import torch
    FINBERT_AVAILABLE = True
    logger.info("FinBERT libraries loaded successfully")
except ImportError:
    FINBERT_AVAILABLE = False
    logger.warning("Transformers not installed. Install with: pip install transformers torch")

class FinBERTAnalyzer:
    """Real FinBERT sentiment analyzer for financial text"""
    
    def __init__(self, use_demo_mode=False):
        self.demo_mode = use_demo_mode or not FINBERT_AVAILABLE
        self.model = None
        self.tokenizer = None
        self.classifier = None
        
        if not self.demo_mode:
            try:
                # Load actual FinBERT model from HuggingFace
                logger.info("Loading FinBERT model from HuggingFace...")
                model_name = "ProsusAI/finbert"
                
                # Load tokenizer and model
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
                
                # Create sentiment analysis pipeline
                self.classifier = pipeline(
                    "sentiment-analysis",
                    model=self.model,
                    tokenizer=self.tokenizer
                )
                
                logger.info("FinBERT model loaded successfully")
                self.demo_mode = False
                
            except Exception as e:
                logger.error(f"Failed to load FinBERT model: {str(e)}")
                logger.warning("Falling back to demo mode")
                self.demo_mode = True
    
    def analyze_text(self, text: str, include_phrases: bool = True) -> Dict:
        """
        Analyze sentiment of financial text using FinBERT
        
        Args:
            text: The financial text to analyze
            include_phrases: Whether to extract key phrases
            
        Returns:
            Dictionary with sentiment analysis results
        """
        if not text or len(text.strip()) < 10:
            return {
                "error": "Text too short for analysis",
                "sentiment_score": 0,
                "sentiment_label": "neutral",
                "confidence": 0
            }
        
        if self.demo_mode:
            # Return consistent demo data based on text content
            return self._demo_analysis(text, include_phrases)
        
        try:
            # Real FinBERT analysis
            # Split text into chunks if too long (FinBERT has 512 token limit)
            max_length = 512
            chunks = self._split_text(text, max_length)
            
            all_results = []
            for chunk in chunks:
                if len(chunk.strip()) < 10:
                    continue
                    
                # Get FinBERT prediction
                result = self.classifier(chunk, truncation=True, max_length=max_length)
                all_results.append(result[0])
            
            if not all_results:
                return {
                    "error": "No valid text to analyze",
                    "sentiment_score": 0,
                    "sentiment_label": "neutral",
                    "confidence": 0
                }
            
            # Aggregate results from all chunks
            aggregated = self._aggregate_sentiments(all_results)
            
            # Extract key phrases if requested
            key_phrases = []
            if include_phrases:
                key_phrases = self._extract_key_phrases(text)
            
            return {
                "sentiment_score": aggregated["score"],
                "sentiment_label": aggregated["label"],
                "confidence": aggregated["confidence"],
                "key_phrases": key_phrases,
                "chunks_analyzed": len(chunks),
                "model_used": "ProsusAI/finbert",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in FinBERT analysis: {str(e)}")
            # Fall back to demo mode on error
            return self._demo_analysis(text, include_phrases)
    
    def _split_text(self, text: str, max_length: int) -> List[str]:
        """Split text into chunks for analysis"""
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            word_length = len(word) + 1  # +1 for space
            if current_length + word_length > max_length * 0.8:  # Use 80% to be safe
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_length = word_length
            else:
                current_chunk.append(word)
                current_length += word_length
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks
    
    def _aggregate_sentiments(self, results: List[Dict]) -> Dict:
        """Aggregate sentiment results from multiple chunks"""
        if not results:
            return {"label": "neutral", "score": 0, "confidence": 0}
        
        # Map FinBERT labels to scores
        label_scores = {
            "positive": 1.0,
            "negative": -1.0,
            "neutral": 0.0
        }
        
        total_score = 0
        total_confidence = 0
        label_counts = {"positive": 0, "negative": 0, "neutral": 0}
        
        for result in results:
            label = result["label"].lower()
            confidence = result["score"]
            
            # Handle FinBERT specific labels
            if "pos" in label:
                label = "positive"
            elif "neg" in label:
                label = "negative"
            else:
                label = "neutral"
            
            label_counts[label] += 1
            score = label_scores.get(label, 0)
            total_score += score * confidence
            total_confidence += confidence
        
        # Calculate weighted average
        avg_score = total_score / len(results) if results else 0
        avg_confidence = total_confidence / len(results) if results else 0
        
        # Determine overall label
        if avg_score > 0.3:
            final_label = "positive"
        elif avg_score < -0.3:
            final_label = "negative"
        else:
            final_label = "neutral"
        
        return {
            "label": final_label,
            "score": avg_score,
            "confidence": avg_confidence
        }
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract key financial phrases from text"""
        # Common financial keywords to look for
        keywords = [
            "earnings", "revenue", "profit", "loss", "growth", "decline",
            "increase", "decrease", "expansion", "contraction", "dividend",
            "margin", "debt", "asset", "liability", "cash flow", "guidance",
            "outlook", "forecast", "target", "beat", "miss", "upgrade",
            "downgrade", "bullish", "bearish", "volatility", "risk"
        ]
        
        text_lower = text.lower()
        found_phrases = []
        
        # Find sentences containing keywords
        sentences = text.split(".")
        for sentence in sentences:
            sentence_lower = sentence.lower()
            for keyword in keywords:
                if keyword in sentence_lower:
                    # Extract a phrase around the keyword
                    words = sentence.split()
                    for i, word in enumerate(words):
                        if keyword in word.lower():
                            # Get surrounding words
                            start = max(0, i - 2)
                            end = min(len(words), i + 3)
                            phrase = " ".join(words[start:end])
                            if len(phrase) > 10 and phrase not in found_phrases:
                                found_phrases.append(phrase.strip())
                                break
            
            if len(found_phrases) >= 5:  # Limit to 5 key phrases
                break
        
        return found_phrases[:5]
    
    def _demo_analysis(self, text: str, include_phrases: bool) -> Dict:
        """
        Provide consistent demo analysis based on text content
        This ensures same text gives same result
        """
        # Use text content to generate consistent results
        text_lower = text.lower()
        
        # Determine sentiment based on keywords
        positive_words = ["growth", "increase", "profit", "gain", "positive", "strong", 
                         "beat", "exceed", "improve", "expand", "bullish", "upgrade"]
        negative_words = ["loss", "decline", "decrease", "fall", "weak", "miss", 
                         "below", "concern", "risk", "bearish", "downgrade", "recession"]
        
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        # Calculate sentiment score based on word counts
        if pos_count > neg_count:
            sentiment_score = min(0.9, 0.3 + (pos_count * 0.15))
            sentiment_label = "positive"
        elif neg_count > pos_count:
            sentiment_score = max(-0.9, -0.3 - (neg_count * 0.15))
            sentiment_label = "negative"
        else:
            sentiment_score = 0.0
            sentiment_label = "neutral"
        
        # Calculate confidence based on total keywords found
        total_keywords = pos_count + neg_count
        confidence = min(0.95, 0.6 + (total_keywords * 0.05))
        
        # Extract key phrases
        key_phrases = []
        if include_phrases:
            sentences = text.split(".")[:3]
            for sentence in sentences:
                if len(sentence) > 20:
                    # Take first meaningful part of sentence
                    words = sentence.strip().split()[:8]
                    if len(words) > 3:
                        key_phrases.append(" ".join(words))
        
        return {
            "sentiment_score": sentiment_score,
            "sentiment_label": sentiment_label,
            "confidence": confidence,
            "key_phrases": key_phrases[:5],
            "model_used": "demo_mode",
            "note": "Install transformers and torch for real FinBERT analysis",
            "timestamp": datetime.now().isoformat()
        }

# Global instance
_analyzer = None

def get_analyzer() -> FinBERTAnalyzer:
    """Get or create global FinBERT analyzer instance"""
    global _analyzer
    if _analyzer is None:
        _analyzer = FinBERTAnalyzer()
    return _analyzer

def analyze_financial_text(text: str) -> Dict:
    """Main function to analyze financial text"""
    analyzer = get_analyzer()
    return analyzer.analyze_text(text)

if __name__ == "__main__":
    # Test the analyzer
    test_texts = [
        "The company reported strong earnings growth of 25% year-over-year, beating analyst expectations.",
        "Revenue declined sharply due to increased competition and margin pressure from rising costs.",
        "The quarterly results were in line with market expectations, maintaining stable operations."
    ]
    
    print("Testing FinBERT Analyzer...")
    print(f"FinBERT Available: {FINBERT_AVAILABLE}")
    print("-" * 50)
    
    for text in test_texts:
        print(f"\nText: {text[:100]}...")
        result = analyze_financial_text(text)
        print(f"Sentiment: {result['sentiment_label']} (Score: {result['sentiment_score']:.3f})")
        print(f"Confidence: {result['confidence']:.3f}")
        if result.get('key_phrases'):
            print(f"Key Phrases: {', '.join(result['key_phrases'][:3])}")
        print("-" * 50)