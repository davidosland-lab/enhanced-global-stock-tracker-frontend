#!/usr/bin/env python3
"""
Add Sentiment Analysis to ML Core Predictions
This shows how to integrate market sentiment into the ML system
"""

import yfinance as yf
import requests
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class MarketSentimentAnalyzer:
    """
    Analyze market sentiment using FinBERT and news data
    """
    
    def __init__(self):
        """Initialize FinBERT model for financial sentiment"""
        try:
            # Use FinBERT for financial sentiment
            self.tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
            self.model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model=self.model,
                tokenizer=self.tokenizer
            )
            print("✅ FinBERT loaded successfully")
        except:
            # Fallback to general sentiment
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english"
            )
            print("⚠️ Using fallback sentiment model")
    
    def get_news_sentiment(self, symbol: str, days: int = 7) -> dict:
        """
        Get sentiment from recent news articles
        """
        # In production, you'd fetch real news from APIs like:
        # - Yahoo Finance News
        # - Alpha Vantage News
        # - NewsAPI
        # - Bloomberg API
        
        # For demonstration, using Yahoo Finance news headlines
        ticker = yf.Ticker(symbol)
        news = ticker.news if hasattr(ticker, 'news') else []
        
        if not news:
            return {
                'sentiment_score': 0.5,  # Neutral
                'sentiment_label': 'NEUTRAL',
                'confidence': 0.0,
                'news_count': 0
            }
        
        sentiments = []
        for article in news[:10]:  # Analyze last 10 articles
            title = article.get('title', '')
            if title:
                result = self.sentiment_pipeline(title)[0]
                
                # Convert to numeric score
                if result['label'] in ['POSITIVE', 'positive']:
                    score = 0.5 + (result['score'] * 0.5)
                elif result['label'] in ['NEGATIVE', 'negative']:
                    score = 0.5 - (result['score'] * 0.5)
                else:  # NEUTRAL
                    score = 0.5
                
                sentiments.append({
                    'score': score,
                    'confidence': result['score']
                })
        
        if sentiments:
            avg_sentiment = np.mean([s['score'] for s in sentiments])
            avg_confidence = np.mean([s['confidence'] for s in sentiments])
            
            # Determine label
            if avg_sentiment > 0.6:
                label = 'POSITIVE'
            elif avg_sentiment < 0.4:
                label = 'NEGATIVE'
            else:
                label = 'NEUTRAL'
            
            return {
                'sentiment_score': float(avg_sentiment),
                'sentiment_label': label,
                'confidence': float(avg_confidence),
                'news_count': len(sentiments)
            }
        
        return {
            'sentiment_score': 0.5,
            'sentiment_label': 'NEUTRAL',
            'confidence': 0.0,
            'news_count': 0
        }
    
    def get_social_sentiment(self, symbol: str) -> dict:
        """
        Get sentiment from social media (Twitter, Reddit, StockTwits)
        """
        # In production, you'd use:
        # - Twitter API for tweet sentiment
        # - Reddit API for r/wallstreetbets sentiment
        # - StockTwits API for trader sentiment
        
        # Placeholder for demonstration
        return {
            'twitter_sentiment': 0.5,
            'reddit_sentiment': 0.5,
            'stocktwits_sentiment': 0.5,
            'social_volume': 0
        }
    
    def get_market_fear_greed_index(self) -> float:
        """
        Get market-wide fear and greed index
        Range: 0 (Extreme Fear) to 1 (Extreme Greed)
        """
        # In production, fetch from CNN Fear & Greed Index or calculate from:
        # - VIX (volatility)
        # - Put/Call ratio
        # - Market momentum
        # - Safe haven demand
        
        # For now, calculate simplified version from VIX
        try:
            vix = yf.Ticker("^VIX")
            vix_data = vix.history(period="1d")
            if not vix_data.empty:
                current_vix = vix_data['Close'].iloc[-1]
                # Convert VIX to fear/greed (inverse relationship)
                # VIX < 12: Extreme Greed, VIX > 30: Extreme Fear
                fear_greed = 1 - (min(max(current_vix - 12, 0), 18) / 18)
                return float(fear_greed)
        except:
            pass
        
        return 0.5  # Neutral if can't fetch
    
    def get_comprehensive_sentiment(self, symbol: str) -> dict:
        """
        Get comprehensive sentiment score combining all sources
        """
        # Get individual sentiment scores
        news_sentiment = self.get_news_sentiment(symbol)
        social_sentiment = self.get_social_sentiment(symbol)
        market_sentiment = self.get_market_fear_greed_index()
        
        # Weight the different sentiment sources
        weights = {
            'news': 0.40,      # 40% weight to news sentiment
            'social': 0.30,    # 30% weight to social sentiment
            'market': 0.30     # 30% weight to market-wide sentiment
        }
        
        # Calculate weighted sentiment
        weighted_sentiment = (
            news_sentiment['sentiment_score'] * weights['news'] +
            social_sentiment['twitter_sentiment'] * weights['social'] +
            market_sentiment * weights['market']
        )
        
        # Determine sentiment impact on prediction
        sentiment_multiplier = 1.0
        if weighted_sentiment > 0.6:  # Positive sentiment
            sentiment_multiplier = 1.0 + (weighted_sentiment - 0.6) * 0.1  # Up to 4% boost
        elif weighted_sentiment < 0.4:  # Negative sentiment
            sentiment_multiplier = 1.0 - (0.4 - weighted_sentiment) * 0.1  # Up to 4% reduction
        
        return {
            'overall_sentiment': float(weighted_sentiment),
            'sentiment_label': 'BULLISH' if weighted_sentiment > 0.6 else 'BEARISH' if weighted_sentiment < 0.4 else 'NEUTRAL',
            'sentiment_multiplier': float(sentiment_multiplier),
            'news_sentiment': news_sentiment,
            'social_sentiment': social_sentiment,
            'market_sentiment': float(market_sentiment),
            'recommendation': self._get_recommendation(weighted_sentiment)
        }
    
    def _get_recommendation(self, sentiment: float) -> str:
        """Get trading recommendation based on sentiment"""
        if sentiment > 0.7:
            return "Strong positive sentiment - Consider buying on dips"
        elif sentiment > 0.6:
            return "Positive sentiment - Favorable for long positions"
        elif sentiment < 0.3:
            return "Strong negative sentiment - Consider reducing exposure"
        elif sentiment < 0.4:
            return "Negative sentiment - Exercise caution"
        else:
            return "Neutral sentiment - Follow technical indicators"


def enhance_ml_prediction_with_sentiment(symbol: str, base_prediction: float, current_price: float) -> dict:
    """
    Enhance ML prediction with sentiment analysis
    """
    # Initialize sentiment analyzer
    sentiment_analyzer = MarketSentimentAnalyzer()
    
    # Get comprehensive sentiment
    sentiment = sentiment_analyzer.get_comprehensive_sentiment(symbol)
    
    # Adjust prediction based on sentiment
    adjusted_prediction = base_prediction * sentiment['sentiment_multiplier']
    
    # Calculate expected returns
    base_return = ((base_prediction - current_price) / current_price) * 100
    adjusted_return = ((adjusted_prediction - current_price) / current_price) * 100
    
    # Generate enhanced signal
    if adjusted_return > 2 and sentiment['overall_sentiment'] > 0.6:
        signal = "STRONG BUY"
        confidence = min(0.9, sentiment['overall_sentiment'])
    elif adjusted_return > 1:
        signal = "BUY"
        confidence = 0.7
    elif adjusted_return < -2 and sentiment['overall_sentiment'] < 0.4:
        signal = "STRONG SELL"
        confidence = min(0.9, 1 - sentiment['overall_sentiment'])
    elif adjusted_return < -1:
        signal = "SELL"
        confidence = 0.7
    else:
        signal = "HOLD"
        confidence = 0.5
    
    return {
        'symbol': symbol,
        'current_price': current_price,
        'base_prediction': base_prediction,
        'sentiment_adjusted_prediction': adjusted_prediction,
        'base_return': base_return,
        'adjusted_return': adjusted_return,
        'signal': signal,
        'confidence': confidence,
        'sentiment': sentiment,
        'analysis': {
            'technical': "Based on 35 technical indicators",
            'fundamental': sentiment['news_sentiment']['sentiment_label'],
            'social': "BULLISH" if sentiment['social_sentiment']['twitter_sentiment'] > 0.6 else "BEARISH" if sentiment['social_sentiment']['twitter_sentiment'] < 0.4 else "NEUTRAL",
            'market': "Risk-On" if sentiment['market_sentiment'] > 0.6 else "Risk-Off" if sentiment['market_sentiment'] < 0.4 else "Neutral"
        }
    }


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("SENTIMENT-ENHANCED ML PREDICTION SYSTEM")
    print("=" * 60)
    
    # Example: Enhance a prediction for AAPL
    symbol = "AAPL"
    current_price = 175.50
    ml_base_prediction = 178.25  # From your ML model
    
    print(f"\nAnalyzing {symbol}...")
    print(f"Current Price: ${current_price}")
    print(f"ML Base Prediction: ${ml_base_prediction}")
    
    # Get sentiment-enhanced prediction
    enhanced = enhance_ml_prediction_with_sentiment(symbol, ml_base_prediction, current_price)
    
    print("\n" + "=" * 40)
    print("ENHANCED PREDICTION RESULTS")
    print("=" * 40)
    print(f"Sentiment Score: {enhanced['sentiment']['overall_sentiment']:.2f}")
    print(f"Sentiment: {enhanced['sentiment']['sentiment_label']}")
    print(f"Adjusted Prediction: ${enhanced['sentiment_adjusted_prediction']:.2f}")
    print(f"Expected Return: {enhanced['adjusted_return']:.2f}%")
    print(f"Signal: {enhanced['signal']}")
    print(f"Confidence: {enhanced['confidence']*100:.1f}%")
    
    print("\n" + "=" * 40)
    print("SENTIMENT BREAKDOWN")
    print("=" * 40)
    print(f"News Sentiment: {enhanced['sentiment']['news_sentiment']['sentiment_label']}")
    print(f"Market Sentiment: {enhanced['sentiment']['market_sentiment']:.2f}")
    print(f"Recommendation: {enhanced['sentiment']['recommendation']}")