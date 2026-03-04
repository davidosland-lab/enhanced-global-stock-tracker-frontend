"""
World Event Monitor
===================
Monitors global events that create market-wide risk (wars, crises, disasters).

This module complements the AI Market Impact Analyzer by:
1. Assessing world-wide systemic risks (not just macro policy)
2. Computing fear/anger emotions from headlines
3. Providing a 0-100 risk score for trading gates
4. Integrating into overnight pipeline sentiment adjustment

Author: FinBERT v4.4.4 Enhanced
Date: 2026-03-01
Version: v193
"""

import logging
import re
from typing import Dict, List, Optional
from datetime import datetime
from collections import Counter

logger = logging.getLogger(__name__)

# Import AI Market Impact Analyzer for crisis detection
try:
    from .ai_market_impact_analyzer import AIMarketImpactAnalyzer
    ai_analyzer_available = True
except ImportError:
    ai_analyzer_available = False
    logger.warning("[!] AI Market Impact Analyzer not available")

# Import FinBERT for sentiment
try:
    from finbert_sentiment import FinBERTSentimentAnalyzer
    finbert = FinBERTSentimentAnalyzer(model_name="ProsusAI/finbert")
    finbert_available = True
except ImportError:
    finbert = None
    finbert_available = False


class WorldEventMonitor:
    """
    Monitors global events and computes market-wide risk score.
    
    Output format (consistent with your spec):
    {
        "world_risk_score": 0-100,
        "risk_level": "LOW|MODERATE|ELEVATED|HIGH|EXTREME",
        "fear": 0.0-1.0,
        "anger": 0.0-1.0,
        "neg_sent": 0.0-1.0,
        "top_topics": ["war", "oil", ...],
        "top_headlines": ["...", "..."],
        "timestamp": "...",
        "article_count": N,
        "sources": [...]
    }
    """
    
    # Severity mappings for quick topic identification
    TOPIC_SEVERITY = {
        # Critical (score: 90-100)
        'nuclear_threat': 100,
        'major_war': 95,
        'global_pandemic': 90,
        
        # High (score: 75-90)
        'military_conflict': 85,
        'banking_crisis': 80,
        'oil_shock': 75,
        'cyber_attack': 75,
        
        # Elevated (score: 60-75)
        'trade_war': 70,
        'political_crisis': 65,
        'currency_crisis': 65,
        'natural_disaster': 60,
        
        # Moderate (score: 50-60)
        'sanctions': 55,
        'protest': 50,
        'diplomatic_tension': 50,
    }
    
    # Keyword patterns for topic detection
    TOPIC_PATTERNS = {
        'nuclear_threat': ['nuclear', 'atomic', 'warhead', 'enrichment', 'icbm'],
        'major_war': ['war', 'declares war', 'invasion', 'full-scale', 'mobilization'],
        'global_pandemic': ['pandemic', 'epidemic', 'outbreak', 'lockdown', 'quarantine'],
        'military_conflict': ['airstrike', 'missile', 'bombing', 'military action', 'strike'],
        'banking_crisis': ['bank failure', 'bank run', 'credit crisis', 'bailout'],
        'oil_shock': ['oil crisis', 'opec', 'energy crisis', 'oil price surge'],
        'cyber_attack': ['cyber attack', 'hack', 'ransomware', 'data breach'],
        'trade_war': ['tariff', 'trade war', 'import duty', 'protectionism'],
        'political_crisis': ['coup', 'impeachment', 'government collapse', 'uprising'],
        'currency_crisis': ['currency collapse', 'devaluation', 'forex crisis'],
        'natural_disaster': ['earthquake', 'tsunami', 'hurricane', 'flood', 'wildfire'],
        'sanctions': ['sanctions', 'embargo', 'trade restrictions'],
        'protest': ['protest', 'riot', 'unrest', 'demonstration'],
        'diplomatic_tension': ['tensions', 'standoff', 'dispute', 'escalation'],
    }
    
    # Fear/anger keywords for emotion detection
    FEAR_KEYWORDS = [
        'fear', 'panic', 'terrified', 'afraid', 'scared', 'worried', 'anxious',
        'threat', 'danger', 'risk', 'warning', 'alarm', 'crisis', 'emergency',
        'chaos', 'turmoil', 'uncertainty', 'instability', 'volatility'
    ]
    
    ANGER_KEYWORDS = [
        'anger', 'outrage', 'fury', 'rage', 'hostile', 'aggression', 'attack',
        'retaliation', 'revenge', 'strike', 'assault', 'confrontation',
        'sanctions', 'punishment', 'condemns', 'slams', 'blasts'
    ]
    
    def __init__(self, use_ai: bool = True, use_finbert: bool = True):
        """
        Initialize World Event Monitor
        
        Args:
            use_ai: Use AI Market Impact Analyzer if available
            use_finbert: Use FinBERT for sentiment if available
        """
        self.use_ai = use_ai and ai_analyzer_available
        self.use_finbert = use_finbert and finbert_available
        
        if self.use_ai:
            self.ai_analyzer = AIMarketImpactAnalyzer(use_ai=False, use_fallback=True)
            logger.info("[OK] World Event Monitor: AI analyzer enabled")
        
        if self.use_finbert:
            logger.info("[OK] World Event Monitor: FinBERT enabled")
        
        logger.info("[OK] World Event Monitor initialized")
    
    def get_world_event_risk(self, articles: Optional[List[Dict]] = None) -> Dict:
        """
        Compute world event risk from articles
        
        Args:
            articles: List of article dicts with 'title', 'source', etc.
                     If None, returns neutral baseline
        
        Returns:
            Dict with world_risk_score, risk_level, emotions, topics, etc.
        """
        if not articles or len(articles) == 0:
            return self._get_neutral_baseline()
        
        # Step 1: Topic detection and severity
        topics, topic_severity = self._detect_topics(articles)
        
        # Step 2: Emotion detection (fear/anger)
        fear, anger = self._detect_emotions(articles)
        
        # Step 3: FinBERT negative sentiment
        neg_sent = self._get_negative_sentiment(articles)
        
        # Step 4: Compute composite risk score
        # v193.4 FIX: Topic severity should dominate the score for major crises
        # Formula adjusted to give topic severity primary weight:
        #   - Topic severity contributes 60-95 points directly (not just 15%)
        #   - Fear/anger/neg_sent provide additional boost (5-35 points)
        #   - This ensures major_war (95) → ~85-95 score, not just 19
        
        # Start with topic severity as base (contributes 60-95% of score)
        base_risk = topic_severity * 100  # Convert back from 0-1 to 0-100 scale
        
        # Add emotional intensity boost (fear + anger can add up to 35 points)
        emotion_boost = (fear * 20) + (anger * 15)
        
        # Add negative sentiment boost (can add up to 20 points)
        sentiment_boost = neg_sent * 20
        
        # Total risk score
        world_risk_score = base_risk + emotion_boost + sentiment_boost
        
        # Clamp to 0-100
        world_risk_score = max(0, min(100, world_risk_score))
        
        # Step 5: Determine risk level
        if world_risk_score >= 85:
            risk_level = "EXTREME"
        elif world_risk_score >= 75:
            risk_level = "HIGH"
        elif world_risk_score >= 65:
            risk_level = "ELEVATED"
        elif world_risk_score >= 50:
            risk_level = "MODERATE"
        else:
            risk_level = "LOW"
        
        # Step 6: Extract top headlines and sources
        top_headlines = [a.get('title', '')[:100] for a in articles[:5]]
        sources = list(set([a.get('source', 'Unknown') for a in articles]))
        
        result = {
            'world_risk_score': round(world_risk_score, 1),
            'risk_level': risk_level,
            'fear': round(fear, 3),
            'anger': round(anger, 3),
            'neg_sent': round(neg_sent, 3),
            'topic_severity': round(topic_severity, 3),
            'top_topics': topics[:5],
            'top_headlines': top_headlines,
            'timestamp': datetime.now().isoformat(),
            'article_count': len(articles),
            'sources': sources
        }
        
        logger.info(f"[World Event Risk] Score: {world_risk_score:.1f}/100 ({risk_level})")
        logger.info(f"  Base Risk (topics): {base_risk:.1f}, Emotion Boost: {emotion_boost:.1f}, Sentiment Boost: {sentiment_boost:.1f}")
        logger.info(f"  Fear: {fear:.2f}, Anger: {anger:.2f}, NegSent: {neg_sent:.2f}")
        logger.info(f"  Topics: {', '.join(topics[:3])}")
        
        return result
    
    def _detect_topics(self, articles: List[Dict]) -> tuple:
        """
        Detect crisis topics in articles
        
        FIX v193.9: Now uses full article text if available for better topic detection
        
        Returns:
            (topic_list, avg_severity_score)
        """
        detected_topics = []
        severity_scores = []
        
        for article in articles:
            title = article.get('title', '').lower()
            # FIX v193.9: Use full article text if available for better topic detection
            full_text = article.get('full_text', '').lower()
            combined_text = f"{title} {full_text}" if full_text else title
            
            # Check each topic pattern
            for topic, keywords in self.TOPIC_PATTERNS.items():
                if any(kw in combined_text for kw in keywords):
                    detected_topics.append(topic)
                    severity_scores.append(self.TOPIC_SEVERITY.get(topic, 50))
        
        # Get top topics by frequency
        if detected_topics:
            topic_counts = Counter(detected_topics)
            top_topics = [t for t, _ in topic_counts.most_common(10)]
        else:
            top_topics = []
        
        # Average severity (normalized to 0-1 range)
        avg_severity = (sum(severity_scores) / len(severity_scores) / 100) if severity_scores else 0.5
        
        return top_topics, avg_severity
    
    def _detect_emotions(self, articles: List[Dict]) -> tuple:
        """
        Detect fear and anger emotions from article content
        
        FIX v193.9: Now uses full article text if available for better emotion detection
        
        Returns:
            (fear_score, anger_score) both 0.0-1.0
        """
        fear_count = 0
        anger_count = 0
        total_words = 0
        
        for article in articles:
            title = article.get('title', '').lower()
            # FIX v193.9: Use full article text for more accurate emotion detection
            full_text = article.get('full_text', '').lower()
            combined_text = f"{title} {full_text}" if full_text else title
            
            words = re.findall(r'\w+', combined_text)
            total_words += len(words)
            
            # Count fear keywords
            fear_count += sum(1 for w in words if w in self.FEAR_KEYWORDS)
            
            # Count anger keywords
            anger_count += sum(1 for w in words if w in self.ANGER_KEYWORDS)
        
        # Normalize to 0-1 range (cap at 1.0)
        fear_score = min(1.0, fear_count / max(1, total_words) * 10)  # Scale by 10
        anger_score = min(1.0, anger_count / max(1, total_words) * 10)
        
        return fear_score, anger_score
    
    def _get_negative_sentiment(self, articles: List[Dict]) -> float:
        """
        Get negative sentiment using FinBERT (or fallback to keywords)
        
        Returns:
            neg_sent: 0.0-1.0 (proportion of negative sentiment)
        """
        if self.use_finbert and finbert is not None:
            try:
                negative_scores = []
                
                for article in articles:
                    title = article.get('title', '')
                    # FIX v193.9: Use full article text for more accurate sentiment
                    full_text = article.get('full_text', '')
                    # Prefer first 200 words of full_text for FinBERT (API limits)
                    text_for_analysis = full_text[:1000] if full_text else title
                    
                    if not text_for_analysis:
                        continue
                    
                    result = finbert.analyze_text(text_for_analysis)
                    label = result.get('label', 'neutral').lower()
                    score = result.get('score', 0.5)
                    
                    if label == 'negative':
                        negative_scores.append(score)
                    elif label == 'neutral':
                        negative_scores.append(0.0)
                    else:  # positive
                        negative_scores.append(0.0)
                
                if negative_scores:
                    return sum(negative_scores) / len(negative_scores)
            
            except Exception as e:
                logger.warning(f"FinBERT sentiment failed: {e}, using fallback")
        
        # Fallback: keyword-based
        negative_words = ['fall', 'decline', 'drop', 'plunge', 'crash', 'collapse', 
                         'crisis', 'concern', 'worry', 'risk', 'threat']
        
        neg_count = 0
        total = 0
        
        for article in articles:
            title = article.get('title', '').lower()
            # FIX v193.9: Use full article text for keyword fallback
            full_text = article.get('full_text', '').lower()
            combined_text = f"{title} {full_text}" if full_text else title
            words = re.findall(r'\w+', combined_text)
            total += len(words)
            neg_count += sum(1 for w in words if w in negative_words)
        
        return min(1.0, neg_count / max(1, total) * 5)  # Scale and cap at 1.0
    
    def _get_neutral_baseline(self) -> Dict:
        """Return neutral baseline when no articles available"""
        return {
            'world_risk_score': 50.0,
            'risk_level': 'MODERATE',
            'fear': 0.0,
            'anger': 0.0,
            'neg_sent': 0.0,
            'topic_severity': 0.5,
            'top_topics': [],
            'top_headlines': [],
            'timestamp': datetime.now().isoformat(),
            'article_count': 0,
            'sources': []
        }


def test_world_event_monitor():
    """Test the world event monitor"""
    print("="*80)
    print("Testing World Event Monitor")
    print("="*80)
    
    # Test articles
    crisis_articles = [
        {
            'title': 'US launches massive airstrikes on Iranian nuclear facilities',
            'source': 'Reuters'
        },
        {
            'title': 'Iran threatens retaliation as Middle East tensions escalate',
            'source': 'BBC'
        },
        {
            'title': 'Oil prices surge 12% on fears of supply disruption',
            'source': 'Bloomberg'
        },
        {
            'title': 'Stock markets plunge worldwide on war fears',
            'source': 'CNBC'
        },
        {
            'title': 'Emergency UN Security Council meeting called',
            'source': 'AP'
        }
    ]
    
    monitor = WorldEventMonitor(use_ai=True, use_finbert=True)
    result = monitor.get_world_event_risk(crisis_articles)
    
    print(f"\nWorld Risk Score: {result['world_risk_score']}/100")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Fear: {result['fear']:.2f}")
    print(f"Anger: {result['anger']:.2f}")
    print(f"Negative Sentiment: {result['neg_sent']:.2f}")
    print(f"Top Topics: {', '.join(result['top_topics'][:5])}")
    print(f"Headlines:")
    for h in result['top_headlines']:
        print(f"  - {h}")
    
    print("\n[OK] Test complete!")


if __name__ == '__main__':
    test_world_event_monitor()
_event_monitor()
