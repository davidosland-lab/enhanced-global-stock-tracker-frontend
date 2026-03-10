"""
AI Market Impact Analyzer
==========================
Uses LLM (GPT-5) to intelligently assess the market impact of global events.

This module solves the critical problem where FinBERT (trained on financial text)
fails to recognize geopolitical/crisis events as market-negative.

Example: "US launches strikes on Iran targets" reads as neutral financial text,
but is clearly a major bearish geopolitical event.

The AI Analyzer:
1. Reviews headlines and summaries from the daily news scrape
2. Applies reasoning about market psychology, risk-off behavior, supply chains
3. Returns a severity score (-1.0 to +1.0) and confidence level
4. Provides human-readable explanation of market impact

Author: FinBERT v4.4.4 (Enhanced)
Date: February 28, 2026
"""

import logging
import os
import json
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# Load OpenAI configuration
try:
    import yaml
    CONFIG_PATH = Path.home() / '.genspark_llm.yaml'
    
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, 'r') as f:
            config = yaml.safe_load(f)
            OPENAI_API_KEY = config.get('openai', {}).get('api_key', os.getenv('OPENAI_API_KEY'))
            OPENAI_BASE_URL = config.get('openai', {}).get('base_url', os.getenv('OPENAI_BASE_URL'))
    else:
        OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
        OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL')
    
    # Initialize OpenAI client
    try:
        from openai import OpenAI
        
        if OPENAI_API_KEY and OPENAI_BASE_URL:
            ai_client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
            logger.info("[OK] AI Market Impact Analyzer initialized with GPT-5")
        else:
            ai_client = None
            logger.warning("[!] OpenAI API key/URL not configured - AI analysis disabled")
    except ImportError:
        ai_client = None
        logger.warning("[!] OpenAI SDK not installed - AI analysis disabled")

except ImportError:
    ai_client = None
    logger.warning("[!] PyYAML not installed - AI analysis disabled")


class AIMarketImpactAnalyzer:
    """
    Uses LLM reasoning to assess market impact of real-world events
    """
    
    # Predefined severity mappings for immediate classification
    GEOPOLITICAL_SEVERITY = {
        # Wars & Military Conflicts (VERY HIGH BEARISH)
        'major_war': {
            'score': -0.85,
            'keywords': ['war', 'declares war', 'invasion', 'invades', 'military offensive', 'full-scale war'],
            'explanation': 'Major military conflict -> extreme risk-off -> flight to safe havens (USD, gold)'
        },
        'military_strikes': {
            'score': -0.70,
            'keywords': ['airstrike', 'missile strike', 'bombing', 'attack', 'strikes targets', 'military action'],
            'explanation': 'Military strikes -> escalation risk -> supply chain disruption -> bearish commodities & equities'
        },
        'nuclear_threat': {
            'score': -0.90,
            'keywords': ['nuclear', 'atomic', 'warhead', 'nuclear threat', 'nuclear test', 'enrichment'],
            'explanation': 'Nuclear escalation -> systemic risk -> extreme volatility -> deep flight to safety'
        },
        
        # Regional Conflicts (HIGH BEARISH)
        'regional_conflict': {
            'score': -0.60,
            'keywords': ['gaza', 'ukraine', 'syria', 'yemen', 'taiwan strait', 'south china sea'],
            'explanation': 'Regional instability -> supply disruption -> energy/commodity volatility -> risk-off sentiment'
        },
        'terrorism': {
            'score': -0.55,
            'keywords': ['terror attack', 'terrorist', 'isis', 'al qaeda', 'bombing', 'suicide'],
            'explanation': 'Terror attack -> uncertainty spike -> short-term selloff -> defensive positioning'
        },
        
        # US Political/Policy Shocks (MEDIUM-HIGH BEARISH/BULLISH)
        'us_tariffs': {
            'score': -0.65,
            'keywords': ['tariff', 'import duty', 'trade war', 'protectionism', 'retaliatory tariff'],
            'explanation': 'Trade war escalation -> supply chain costs up -> corporate earnings down -> bearish equities'
        },
        'us_sanctions': {
            'score': -0.50,
            'keywords': ['sanctions', 'embargo', 'trade restrictions', 'economic penalties'],
            'explanation': 'Sanctions -> trade disruption -> geopolitical tension -> selective sector impact'
        },
        'government_shutdown': {
            'score': -0.40,
            'keywords': ['government shutdown', 'debt ceiling', 'default risk', 'budget crisis'],
            'explanation': 'Political gridlock -> fiscal uncertainty -> short-term volatility -> risk-off bias'
        },
        
        # Economic Crises (HIGH BEARISH)
        'banking_crisis': {
            'score': -0.80,
            'keywords': ['bank failure', 'bank run', 'banking crisis', 'credit crisis', 'systemic risk'],
            'explanation': 'Financial contagion -> liquidity crisis -> systemic risk -> deep equity selloff'
        },
        'sovereign_default': {
            'score': -0.75,
            'keywords': ['debt default', 'sovereign default', 'debt restructuring', 'bailout'],
            'explanation': 'Sovereign default -> contagion risk -> bond market turmoil -> risk-off flows'
        },
        'recession': {
            'score': -0.60,
            'keywords': ['recession', 'economic contraction', 'gdp decline', 'downturn'],
            'explanation': 'Recession confirmed -> earnings downgrades -> defensive rotation -> bearish equities'
        },
        
        # Commodity/Energy Shocks (MEDIUM-HIGH BEARISH)
        'oil_shock': {
            'score': -0.65,
            'keywords': ['oil crisis', 'energy crisis', 'opec cuts production', 'oil embargo'],
            'explanation': 'Energy shock -> inflation spike -> consumer spending down -> stagflation risk'
        },
        'commodity_spike': {
            'score': -0.50,
            'keywords': ['commodity surge', 'food prices spike', 'wheat shortage', 'supply shock'],
            'explanation': 'Commodity inflation -> input costs rise -> margin compression -> bearish cyclicals'
        },
        
        # Natural Disasters (MEDIUM BEARISH)
        'natural_disaster': {
            'score': -0.45,
            'keywords': ['earthquake', 'tsunami', 'hurricane', 'typhoon', 'flood', 'wildfire'],
            'explanation': 'Natural disaster -> supply disruption -> infrastructure damage -> regional bearish impact'
        },
        
        # Positive Events (BULLISH)
        'peace_agreement': {
            'score': +0.60,
            'keywords': ['peace deal', 'ceasefire', 'peace treaty', 'diplomatic breakthrough'],
            'explanation': 'Peace agreement -> risk-on sentiment -> reduced uncertainty -> bullish for risk assets'
        },
        'rate_cut': {
            'score': +0.55,
            'keywords': ['rate cut', 'lowers interest rate', 'monetary easing', 'dovish policy'],
            'explanation': 'Rate cut -> cheaper capital -> earnings boost -> bullish for equities'
        },
        'stimulus': {
            'score': +0.50,
            'keywords': ['stimulus', 'fiscal package', 'infrastructure spending', 'economic support'],
            'explanation': 'Fiscal stimulus -> demand boost -> growth acceleration -> bullish for cyclicals'
        },
        'trade_deal': {
            'score': +0.45,
            'keywords': ['trade agreement', 'free trade deal', 'bilateral trade', 'trade pact'],
            'explanation': 'Trade deal -> tariff reduction -> supply chain efficiency -> bullish for exporters'
        },
    }
    
    def __init__(self, use_ai: bool = True, use_fallback: bool = True):
        """
        Initialize AI Market Impact Analyzer
        
        Args:
            use_ai: Use LLM for intelligent analysis (default: True)
            use_fallback: Use keyword-based fallback if AI unavailable (default: True)
        """
        self.use_ai = use_ai and ai_client is not None
        self.use_fallback = use_fallback
        
        if self.use_ai:
            logger.info("[OK] AI Market Impact Analyzer: LLM mode enabled (GPT-5)")
        elif self.use_fallback:
            logger.info("[OK] AI Market Impact Analyzer: Fallback mode (keyword-based)")
        else:
            logger.warning("[!] AI Market Impact Analyzer: DISABLED")
    
    def analyze_market_impact(self, articles: List[Dict], market: str = 'US') -> Dict:
        """
        Analyze market impact of news articles
        
        Args:
            articles: List of article dicts with 'title', 'url', 'source', 'type'
            market: Market context ('US', 'ASX', 'UK')
        
        Returns:
            {
                'impact_score': float (-1.0 to +1.0),
                'confidence': float (0.0 to 1.0),
                'severity': str ('CRITICAL'|'HIGH'|'MODERATE'|'LOW'|'NEUTRAL'|'POSITIVE'),
                'explanation': str (human-readable reasoning),
                'analyzed_events': list of event dicts,
                'recommendation': str ('RISK_OFF'|'CAUTION'|'NEUTRAL'|'RISK_ON'),
                'timestamp': ISO datetime
            }
        """
        if not articles:
            return self._get_neutral_result(market)
        
        # Try AI analysis first
        if self.use_ai:
            try:
                return self._ai_analyze(articles, market)
            except Exception as e:
                logger.warning(f"[!] AI analysis failed: {e}, using fallback")
        
        # Fallback to keyword-based classification
        if self.use_fallback:
            return self._keyword_analyze(articles, market)
        
        return self._get_neutral_result(market)
    
    def _ai_analyze(self, articles: List[Dict], market: str) -> Dict:
        """
        Use GPT-5 to intelligently analyze market impact
        """
        # Prepare article summaries for LLM
        article_summaries = []
        for i, article in enumerate(articles[:15], 1):  # Top 15 articles
            summary = f"{i}. {article.get('title', 'N/A')}"
            if article.get('source'):
                summary += f" (Source: {article['source']})"
            article_summaries.append(summary)
        
        articles_text = '\n'.join(article_summaries)
        
        # Construct prompt for market impact analysis
        prompt = f"""You are an expert market analyst assessing the impact of today's news on {market} financial markets.

Today's Headlines:
{articles_text}

Task: Analyze these headlines and provide a comprehensive market impact assessment.

Consider:
1. Geopolitical events (wars, conflicts, political instability) -> typically bearish
2. Economic data (inflation, GDP, employment) -> context-dependent
3. Central bank policy (rate hikes/cuts, QE/QT) -> mixed impact
4. Trade policy (tariffs, sanctions) -> typically bearish
5. Financial crises (banking, sovereign debt) -> very bearish
6. Natural disasters -> regionally bearish
7. Peace agreements, stimulus -> bullish
8. Market psychology: how will traders react? Risk-on or risk-off?

Provide your analysis in JSON format:
{{
    "impact_score": <float from -1.0 (very bearish) to +1.0 (very bullish)>,
    "confidence": <float from 0.0 to 1.0>,
    "severity": "<CRITICAL|HIGH|MODERATE|LOW|NEUTRAL|POSITIVE>",
    "explanation": "<2-3 sentence reasoning>",
    "key_events": [
        {{"event": "<event name>", "impact": "<bearish|neutral|bullish>", "reasoning": "<why>"}}
    ],
    "recommendation": "<RISK_OFF|CAUTION|NEUTRAL|RISK_ON>"
}}

Focus on events that will move markets TODAY. Be realistic about severity.
"""
        
        # Call GPT-5
        try:
            response = ai_client.chat.completions.create(
                model='gpt-5',
                messages=[
                    {
                        'role': 'system',
                        'content': 'You are a professional market analyst with expertise in geopolitics, economics, and market psychology. Provide concise, actionable market impact assessments.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                temperature=0.3,  # Lower temperature for consistent analysis
                max_tokens=1000
            )
            
            # Parse JSON response
            content = response.choices[0].message.content
            
            # Extract JSON from response (handle markdown code blocks)
            if '```json' in content:
                json_start = content.index('```json') + 7
                json_end = content.index('```', json_start)
                json_str = content[json_start:json_end].strip()
            elif '```' in content:
                json_start = content.index('```') + 3
                json_end = content.index('```', json_start)
                json_str = content[json_start:json_end].strip()
            else:
                json_str = content.strip()
            
            result = json.loads(json_str)
            
            # Add metadata
            result['timestamp'] = datetime.now().isoformat()
            result['market'] = market
            result['method'] = 'AI (GPT-5)'
            result['analyzed_events'] = result.pop('key_events', [])
            
            logger.info(f"[OK] AI Analysis: Impact {result['impact_score']:+.2f}, "
                       f"Severity {result['severity']}, Confidence {result['confidence']:.0%}")
            
            return result
        
        except Exception as e:
            logger.error(f"[ERROR] AI analysis failed: {e}")
            raise
    
    def _keyword_analyze(self, articles: List[Dict], market: str) -> Dict:
        """
        Fallback: Keyword-based severity classification
        """
        logger.info("  Using keyword-based market impact analysis...")
        
        detected_events = []
        total_score = 0.0
        total_weight = 0.0
        
        for article in articles:
            title = article.get('title', '').lower()
            
            # Check each severity category
            for event_type, config in self.GEOPOLITICAL_SEVERITY.items():
                keywords = config['keywords']
                
                # Check if any keyword matches
                if any(kw in title for kw in keywords):
                    score = config['score']
                    explanation = config['explanation']
                    
                    # Weight by article position (earlier = more important)
                    weight = 1.0
                    
                    detected_events.append({
                        'event': event_type.replace('_', ' ').title(),
                        'impact': 'bearish' if score < 0 else 'bullish' if score > 0 else 'neutral',
                        'reasoning': explanation,
                        'score': score,
                        'article': article.get('title', '')[:80]
                    })
                    
                    total_score += score * weight
                    total_weight += weight
                    
                    # Only match first category per article
                    break
        
        # Calculate average weighted impact
        if total_weight > 0:
            impact_score = total_score / total_weight
            confidence = min(1.0, total_weight / 5.0)  # More events = higher confidence
        else:
            impact_score = 0.0
            confidence = 0.2  # Low confidence if no events detected
        
        # Determine severity
        if impact_score <= -0.70:
            severity = 'CRITICAL'
        elif impact_score <= -0.50:
            severity = 'HIGH'
        elif impact_score <= -0.30:
            severity = 'MODERATE'
        elif impact_score <= -0.10:
            severity = 'LOW'
        elif impact_score >= 0.40:
            severity = 'POSITIVE'
        else:
            severity = 'NEUTRAL'
        
        # Recommendation
        if impact_score <= -0.50:
            recommendation = 'RISK_OFF'
        elif impact_score <= -0.20:
            recommendation = 'CAUTION'
        elif impact_score >= 0.30:
            recommendation = 'RISK_ON'
        else:
            recommendation = 'NEUTRAL'
        
        # Generate explanation
        if detected_events:
            top_events = sorted(detected_events, key=lambda x: abs(x['score']), reverse=True)[:3]
            event_names = [e['event'] for e in top_events]
            explanation = f"Detected {len(detected_events)} significant events: {', '.join(event_names)}. "
            explanation += f"Net impact: {severity.lower()}. "
            explanation += top_events[0]['reasoning']
        else:
            explanation = f"No significant market-moving events detected in {len(articles)} articles. Neutral sentiment."
        
        result = {
            'impact_score': round(impact_score, 3),
            'confidence': round(confidence, 2),
            'severity': severity,
            'explanation': explanation,
            'analyzed_events': detected_events[:5],  # Top 5
            'recommendation': recommendation,
            'timestamp': datetime.now().isoformat(),
            'market': market,
            'method': 'Keyword-based'
        }
        
        logger.info(f"[OK] Keyword Analysis: Impact {impact_score:+.2f}, Severity {severity}, "
                   f"Events {len(detected_events)}")
        
        return result
    
    def _get_neutral_result(self, market: str) -> Dict:
        """Return neutral result when no analysis possible"""
        return {
            'impact_score': 0.0,
            'confidence': 0.1,
            'severity': 'NEUTRAL',
            'explanation': 'Insufficient data for market impact analysis.',
            'analyzed_events': [],
            'recommendation': 'NEUTRAL',
            'timestamp': datetime.now().isoformat(),
            'market': market,
            'method': 'Default'
        }


def test_ai_analyzer():
    """Test AI Market Impact Analyzer"""
    print("="*80)
    print("TESTING AI MARKET IMPACT ANALYZER")
    print("="*80)
    
    # Sample articles
    test_articles = [
        {
            'title': 'US launches airstrikes on Iranian military targets in response to Red Sea attacks',
            'source': 'Reuters',
            'type': 'geopolitical'
        },
        {
            'title': 'Oil prices surge 8% on Middle East escalation fears',
            'source': 'Bloomberg',
            'type': 'commodity'
        },
        {
            'title': 'Fed signals pause on rate hikes amid banking sector concerns',
            'source': 'Federal Reserve',
            'type': 'monetary_policy'
        },
        {
            'title': 'China economic growth slows to 4.2% in Q4',
            'source': 'China Daily',
            'type': 'economic_data'
        },
        {
            'title': 'Trump announces 25% tariffs on all Chinese imports',
            'source': 'White House',
            'type': 'trade_policy'
        }
    ]
    
    analyzer = AIMarketImpactAnalyzer(use_ai=True, use_fallback=True)
    
    result = analyzer.analyze_market_impact(test_articles, market='US')
    
    print(f"\nMarket Impact Analysis:")
    print(f"  Impact Score: {result['impact_score']:+.2f}")
    print(f"  Confidence: {result['confidence']:.0%}")
    print(f"  Severity: {result['severity']}")
    print(f"  Recommendation: {result['recommendation']}")
    print(f"  Method: {result['method']}")
    print(f"\n  Explanation:")
    print(f"    {result['explanation']}")
    print(f"\n  Key Events:")
    for event in result['analyzed_events']:
        print(f"    - {event.get('event', 'N/A')}: {event.get('impact', 'N/A')} ({event.get('reasoning', 'N/A')[:60]}...)")
    
    print("\n[OK] Test complete!")


if __name__ == '__main__':
    test_ai_analyzer()
