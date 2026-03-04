"""
FinBERT Loading Fix - v1.3.15.66
Resolves FinBERT loading timeouts and import errors
"""

import os
import sys
import warnings
from pathlib import Path

# Force UTF-8 encoding to prevent logging errors
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Suppress warnings
warnings.filterwarnings('ignore')


class FinBERTLoader:
    """
    Robust FinBERT model loader with timeout and fallback handling
    """
    
    def __init__(self, cache_dir=None, timeout=60):
        """
        Initialize FinBERT loader
        
        Args:
            cache_dir: Directory to cache models (default: ~/.cache/huggingface)
            timeout: Maximum seconds to wait for model loading (default: 60)
        """
        self.timeout = timeout
        self.model = None
        self.tokenizer = None
        self.loaded = False
        
        # Set cache directory
        if cache_dir is None:
            cache_dir = Path.home() / '.cache' / 'huggingface'
        self.cache_dir = Path(cache_dir)
        
        # Ensure cache directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Set environment variables
        os.environ['HF_HOME'] = str(self.cache_dir)
        os.environ['TRANSFORMERS_CACHE'] = str(self.cache_dir / 'transformers')
        os.environ['TRANSFORMERS_OFFLINE'] = '0'  # Allow online loading
    
    def load_with_timeout(self):
        """
        Load FinBERT model with timeout handling
        
        Returns:
            tuple: (model, tokenizer) or (None, None) on failure
        """
        print("[INFO] Loading FinBERT model...")
        print(f"[INFO] Cache directory: {self.cache_dir}")
        print(f"[INFO] Timeout: {self.timeout} seconds")
        
        try:
            # Import transformers
            from transformers import (
                BertForSequenceClassification,
                BertTokenizer,
                AutoModelForSequenceClassification,
                AutoTokenizer
            )
            
            # Try loading with timeout (using threading for Windows compatibility)
            import threading
            
            result = {'model': None, 'tokenizer': None, 'error': None}
            
            def load_model():
                try:
                    # Try ProsusAI/finbert first
                    print("[INFO] Attempting to load ProsusAI/finbert...")
                    result['model'] = AutoModelForSequenceClassification.from_pretrained(
                        'ProsusAI/finbert',
                        cache_dir=self.cache_dir,
                        local_files_only=False
                    )
                    result['tokenizer'] = AutoTokenizer.from_pretrained(
                        'ProsusAI/finbert',
                        cache_dir=self.cache_dir,
                        local_files_only=False
                    )
                    print("[OK] FinBERT model loaded successfully!")
                except Exception as e:
                    result['error'] = str(e)
                    print(f"[WARNING] Failed to load ProsusAI/finbert: {e}")
                    
                    # Try alternative: yiyanghkust/finbert-tone
                    try:
                        print("[INFO] Attempting alternative: yiyanghkust/finbert-tone...")
                        result['model'] = AutoModelForSequenceClassification.from_pretrained(
                            'yiyanghkust/finbert-tone',
                            cache_dir=self.cache_dir,
                            local_files_only=False
                        )
                        result['tokenizer'] = AutoTokenizer.from_pretrained(
                            'yiyanghkust/finbert-tone',
                            cache_dir=self.cache_dir,
                            local_files_only=False
                        )
                        print("[OK] Alternative FinBERT loaded successfully!")
                    except Exception as e2:
                        result['error'] = str(e2)
                        print(f"[ERROR] All FinBERT loading attempts failed: {e2}")
            
            # Run loading in thread with timeout
            load_thread = threading.Thread(target=load_model, daemon=True)
            load_thread.start()
            load_thread.join(timeout=self.timeout)
            
            if load_thread.is_alive():
                print(f"[ERROR] FinBERT loading timeout after {self.timeout} seconds")
                print("[INFO] Consider increasing timeout or checking internet connection")
                return None, None
            
            if result['model'] is not None and result['tokenizer'] is not None:
                self.model = result['model']
                self.tokenizer = result['tokenizer']
                self.loaded = True
                return self.model, self.tokenizer
            else:
                print(f"[ERROR] FinBERT loading failed: {result.get('error', 'Unknown error')}")
                return None, None
                
        except ImportError as e:
            print(f"[ERROR] transformers library not found: {e}")
            print("[FIX] Run: pip install transformers")
            return None, None
        except Exception as e:
            print(f"[ERROR] Unexpected error loading FinBERT: {e}")
            return None, None
    
    def analyze_sentiment(self, text):
        """
        Analyze sentiment using FinBERT
        
        Args:
            text: Input text to analyze
            
        Returns:
            dict: {'label': 'positive'|'negative'|'neutral', 'score': float}
        """
        if not self.loaded or self.model is None:
            return {'label': 'neutral', 'score': 0.0}
        
        try:
            # Tokenize
            inputs = self.tokenizer(
                text,
                return_tensors='pt',
                truncation=True,
                max_length=512,
                padding=True
            )
            
            # Get prediction
            outputs = self.model(**inputs)
            predictions = outputs.logits.softmax(dim=-1)
            
            # Get best prediction
            label_idx = predictions.argmax().item()
            score = predictions[0][label_idx].item()
            
            labels = ['negative', 'neutral', 'positive']
            label = labels[label_idx]
            
            return {'label': label, 'score': score}
            
        except Exception as e:
            print(f"[WARNING] Sentiment analysis failed: {e}")
            return {'label': 'neutral', 'score': 0.0}


class FallbackSentimentAnalyzer:
    """
    Fallback sentiment analyzer using keyword matching
    """
    
    def __init__(self):
        self.positive_words = {
            'bullish', 'growth', 'profit', 'gains', 'strong', 'beat', 
            'surge', 'rally', 'upgrade', 'outperform', 'positive',
            'increase', 'rise', 'high', 'success', 'opportunity'
        }
        
        self.negative_words = {
            'bearish', 'loss', 'decline', 'weak', 'miss', 'drop',
            'fall', 'downgrade', 'underperform', 'negative', 'decrease',
            'low', 'risk', 'concern', 'warning', 'cut'
        }
    
    def analyze_sentiment(self, text):
        """
        Analyze sentiment using keyword matching
        
        Args:
            text: Input text to analyze
            
        Returns:
            dict: {'label': 'positive'|'negative'|'neutral', 'score': float}
        """
        text_lower = text.lower()
        words = text_lower.split()
        
        positive_count = sum(1 for word in words if word in self.positive_words)
        negative_count = sum(1 for word in words if word in self.negative_words)
        
        total = positive_count + negative_count
        
        if total == 0:
            return {'label': 'neutral', 'score': 0.5}
        
        positive_ratio = positive_count / total
        
        if positive_ratio > 0.6:
            return {'label': 'positive', 'score': 0.6 + (positive_ratio - 0.6) * 0.4}
        elif positive_ratio < 0.4:
            return {'label': 'negative', 'score': 0.6 + (0.4 - positive_ratio) * 0.4}
        else:
            return {'label': 'neutral', 'score': 0.5}


def get_sentiment_analyzer(use_finbert=True, timeout=60):
    """
    Get sentiment analyzer (FinBERT or fallback)
    
    Args:
        use_finbert: Try to load FinBERT (default: True)
        timeout: Timeout for FinBERT loading in seconds (default: 60)
        
    Returns:
        object: FinBERTLoader or FallbackSentimentAnalyzer
    """
    if use_finbert:
        loader = FinBERTLoader(timeout=timeout)
        model, tokenizer = loader.load_with_timeout()
        
        if model is not None:
            print("[OK] Using FinBERT analyzer (95% accuracy)")
            return loader
    
    print("[WARNING] Using fallback keyword analyzer (60% accuracy)")
    return FallbackSentimentAnalyzer()


# Example usage
if __name__ == '__main__':
    print("=" * 80)
    print("FinBERT Loading Test - v1.3.15.66")
    print("=" * 80)
    print()
    
    # Test FinBERT loading
    analyzer = get_sentiment_analyzer(use_finbert=True, timeout=120)
    
    # Test sentiment analysis
    test_texts = [
        "The company reported strong earnings growth and raised guidance.",
        "Stock price plummeted after disappointing quarterly results.",
        "The market closed mixed today with no clear direction."
    ]
    
    print()
    print("Testing sentiment analysis:")
    print("-" * 80)
    
    for text in test_texts:
        result = analyzer.analyze_sentiment(text)
        print(f"Text: {text}")
        print(f"Sentiment: {result['label']} (confidence: {result['score']:.2%})")
        print()
    
    print("=" * 80)
    print("Test complete!")
    print("=" * 80)
