"""
ChatGPT Research Module

Integrates OpenAI's ChatGPT to perform deep research on top stock opportunities.
Generates comprehensive markdown reports with fundamental analysis, technical insights,
risk assessment, and trading recommendations.

Features:
- Deep fundamental analysis using ChatGPT
- Market context and sector analysis
- Risk assessment and recommendation
- Markdown report generation
- Configurable research parameters

Requirements:
- OPENAI_API_KEY environment variable must be set
- OpenAI Python SDK (pip install openai)
"""

import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None  # Define as None when not available
    logging.warning("OpenAI SDK not installed. Install with: pip install openai")

logger = logging.getLogger(__name__)


def _load_api_key_from_file() -> Optional[str]:
    """
    Load API key from configuration file.
    Searches multiple locations for API key file.
    
    Returns:
        API key string if found, None otherwise
    """
    # Get the base path (project root)
    base_path = Path(__file__).parent.parent.parent
    
    # Possible file locations (in order of priority)
    possible_locations = [
        base_path / "config" / "api_keys.env",
        base_path / "models" / "config" / "api_keys.env",
        base_path / ".env",
        base_path / "api_keys.env",
    ]
    
    for file_path in possible_locations:
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        # Skip comments and empty lines
                        if not line or line.startswith('#'):
                            continue
                        # Parse KEY=value format
                        if '=' in line and line.startswith('OPENAI_API_KEY'):
                            key = line.split('=', 1)[1].strip()
                            # Remove quotes if present
                            key = key.strip('"').strip("'")
                            if key and not key.startswith('sk-your'):
                                logger.info(f"✓ API key loaded from: {file_path.name}")
                                return key
            except Exception as e:
                logger.warning(f"Failed to read API key from {file_path}: {e}")
                continue
    
    return None


def get_client():
    """
    Get OpenAI client instance.
    
    Attempts to load API key from multiple sources (in order):
    1. Environment variable: OPENAI_API_KEY
    2. Config file: config/api_keys.env
    3. Config file: models/config/api_keys.env
    4. Config file: .env
    5. Config file: api_keys.env
    
    Returns:
        OpenAI client if API key is available, None otherwise
    """
    # Try environment variable first
    api_key = os.getenv("OPENAI_API_KEY")
    
    # If not in environment, try loading from file
    if not api_key:
        api_key = _load_api_key_from_file()
    
    if not api_key:
        logger.error("❌ OPENAI_API_KEY not found")
        logger.error("   Searched locations:")
        logger.error("   1. Environment variable: OPENAI_API_KEY")
        logger.error("   2. Config file: config/api_keys.env")
        logger.error("   3. Config file: models/config/api_keys.env")
        logger.error("   4. Config file: .env")
        logger.error("   5. Config file: api_keys.env")
        logger.error("")
        logger.error("   To set up:")
        logger.error("   1. Copy config/.env.example to config/api_keys.env")
        logger.error("   2. Edit config/api_keys.env and add your key")
        logger.error("   3. Or set environment variable: $env:OPENAI_API_KEY='your-key'")
        return None
    
    if not OPENAI_AVAILABLE:
        logger.error("❌ OpenAI SDK not installed")
        return None
    
    try:
        client = OpenAI(api_key=api_key)
        return client
    except Exception as e:
        logger.error(f"❌ Failed to initialize OpenAI client: {e}")
        return None


def ai_quick_filter(
    stocks: List[Dict],
    model: str = "gpt-4o-mini",
    market: str = "ASX"
) -> Dict[str, Dict]:
    """
    Quick AI filter to flag high-risk stocks and identify hidden gems.
    Uses batch processing for efficiency.
    
    Args:
        stocks: List of stock dictionaries to filter
        model: OpenAI model to use
        market: Market identifier ("ASX" or "US")
        
    Returns:
        Dictionary mapping symbols to filter results:
        {
            'AAPL': {
                'risk_flag': 'low',  # low, medium, high
                'opportunity_flag': 'high',  # low, medium, high
                'quick_score': 75,  # 0-100
                'reason': 'Strong fundamentals...'
            }
        }
    """
    logger.info(f"🔍 AI Quick Filter: Analyzing {len(stocks)} {market} stocks...")
    
    client = get_client()
    if not client:
        logger.warning("⚠️ AI Quick Filter unavailable - returning empty results")
        return {}
    
    # Process in batches of 20 for efficiency
    batch_size = 20
    filter_results = {}
    
    for i in range(0, len(stocks), batch_size):
        batch = stocks[i:i + batch_size]
        batch_symbols = [s.get('symbol', 'N/A') for s in batch]
        
        # Build concise batch prompt
        stock_summaries = []
        for stock in batch:
            symbol = stock.get('symbol', 'N/A')
            sector = stock.get('sector', 'Unknown')
            
            # Convert to float (might be strings)
            try:
                prediction = float(stock.get('prediction', 0))
            except (ValueError, TypeError):
                prediction = 0.0
            
            try:
                confidence = float(stock.get('confidence', 0))
            except (ValueError, TypeError):
                confidence = 0.0
            
            stock_summaries.append(
                f"{symbol} ({sector}): Prediction {prediction:+.2f}, Confidence {confidence:.1f}%"
            )
        
        prompt = f"""Analyze these {market} stocks for risk and opportunity. Provide quick assessment.

Stocks:
{chr(10).join(stock_summaries)}

For EACH stock, provide:
1. Risk level (low/medium/high)
2. Opportunity level (low/medium/high)  
3. Score (0-100)
4. Brief reason (max 15 words)

Format: SYMBOL|risk|opportunity|score|reason
Example: AAPL|low|high|85|Strong earnings, sector leader, low debt

Be concise. Focus on fundamental red flags and hidden strengths."""
        
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a stock screening AI. Provide concise risk/opportunity assessments."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            # Parse response
            content = response.choices[0].message.content
            for line in content.strip().split('\n'):
                if '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 5:
                        symbol = parts[0].strip()
                        filter_results[symbol] = {
                            'risk_flag': parts[1].strip().lower(),
                            'opportunity_flag': parts[2].strip().lower(),
                            'quick_score': int(parts[3].strip()) if parts[3].strip().isdigit() else 50,
                            'reason': parts[4].strip()
                        }
            
            logger.info(f"  ✓ Batch {i//batch_size + 1}: {len(batch)} stocks filtered")
            
        except Exception as e:
            logger.error(f"  ✗ Batch {i//batch_size + 1} failed: {e}")
            continue
    
    logger.info(f"✅ AI Quick Filter complete: {len(filter_results)} stocks analyzed")
    return filter_results


def ai_score_opportunity(
    opportunity: Dict,
    model: str = "gpt-4o-mini",
    market: str = "ASX"
) -> Dict:
    """
    Get detailed AI scoring for a stock opportunity.
    
    Args:
        opportunity: Stock opportunity dictionary
        model: OpenAI model to use
        market: Market identifier ("ASX" or "US")
        
    Returns:
        Dictionary with AI scores:
        {
            'fundamental_score': 85,  # 0-100
            'risk_score': 75,  # 0-100 (higher = lower risk)
            'recommendation_score': 90,  # 0-100
            'overall_ai_score': 83,  # weighted average
            'recommendation': 'Strong Buy',
            'confidence': 88,  # 0-100
            'key_points': ['Strong earnings', 'Low debt', ...]
        }
    """
    client = get_client()
    if not client:
        return None
    
    symbol = opportunity.get('symbol', 'N/A')
    company = opportunity.get('company_name', 'Unknown')
    sector = opportunity.get('sector', 'Unknown')
    
    # Convert prediction and confidence to float (they might be strings)
    try:
        prediction = float(opportunity.get('prediction', 0))
    except (ValueError, TypeError):
        prediction = 0.0
    
    try:
        confidence = float(opportunity.get('confidence', 0))
    except (ValueError, TypeError):
        confidence = 0.0
    
    prompt = f"""Provide numeric scores for this stock opportunity:

Stock: {symbol} - {company}
Market: {market}
Sector: {sector}
Current Prediction: {prediction:+.2f}
Confidence: {confidence:.1f}%

Analyze and provide scores (0-100):

1. FUNDAMENTAL_SCORE: Financial health, earnings, growth (0-100)
2. RISK_SCORE: Safety level, bankruptcy risk, volatility (0-100, higher=safer)
3. RECOMMENDATION_SCORE: Buy/Hold/Sell strength (0-100)
4. Overall recommendation (Strong Buy/Buy/Hold/Sell/Strong Sell)
5. Confidence in recommendation (0-100)
6. Top 3 key points (brief)

Format:
FUNDAMENTAL: [score]
RISK: [score]
RECOMMENDATION: [score]
OVERALL: [recommendation]
CONFIDENCE: [score]
POINTS: [point1] | [point2] | [point3]

Be precise with numeric scores."""
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a quantitative stock analyst. Provide precise numeric scores."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=300
        )
        
        content = response.choices[0].message.content
        
        # Parse scores
        scores = {
            'fundamental_score': 50,
            'risk_score': 50,
            'recommendation_score': 50,
            'overall_ai_score': 50,
            'recommendation': 'Hold',
            'confidence': 50,
            'key_points': []
        }
        
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('FUNDAMENTAL:'):
                scores['fundamental_score'] = int(''.join(filter(str.isdigit, line.split(':')[1])))
            elif line.startswith('RISK:'):
                scores['risk_score'] = int(''.join(filter(str.isdigit, line.split(':')[1])))
            elif line.startswith('RECOMMENDATION:'):
                scores['recommendation_score'] = int(''.join(filter(str.isdigit, line.split(':')[1])))
            elif line.startswith('OVERALL:'):
                scores['recommendation'] = line.split(':')[1].strip()
            elif line.startswith('CONFIDENCE:'):
                scores['confidence'] = int(''.join(filter(str.isdigit, line.split(':')[1])))
            elif line.startswith('POINTS:'):
                points = line.split(':')[1].split('|')
                scores['key_points'] = [p.strip() for p in points if p.strip()]
        
        # Calculate overall AI score (weighted average)
        scores['overall_ai_score'] = int(
            scores['fundamental_score'] * 0.4 +
            scores['risk_score'] * 0.3 +
            scores['recommendation_score'] * 0.3
        )
        
        return scores
        
    except Exception as e:
        logger.error(f"AI scoring failed for {symbol}: {e}")
        return None


def ai_rerank_opportunities(
    opportunities: List[Dict],
    model: str = "gpt-4o-mini",
    market: str = "ASX",
    top_n: int = 10
) -> List[Dict]:
    """
    Use AI to re-rank top opportunities based on qualitative factors.
    
    Args:
        opportunities: List of scored opportunities (should be top 20-30)
        model: OpenAI model to use
        market: Market identifier ("ASX" or "US")
        top_n: Number of stocks to return
        
    Returns:
        Re-ranked list of opportunities with AI adjustments
    """
    logger.info(f"🎯 AI Re-Ranking: Analyzing top {len(opportunities)} {market} opportunities...")
    
    client = get_client()
    if not client:
        logger.warning("⚠️ AI Re-Ranking unavailable - returning original order")
        return opportunities[:top_n]
    
    # Build comparison prompt
    stock_summaries = []
    for i, opp in enumerate(opportunities, 1):
        symbol = opp.get('symbol', 'N/A')
        
        # Convert to float (might be strings)
        try:
            score = float(opp.get('opportunity_score', 0))
        except (ValueError, TypeError):
            score = 0.0
        
        try:
            prediction = float(opp.get('prediction', 0))
        except (ValueError, TypeError):
            prediction = 0.0
        
        sector = opp.get('sector', 'Unknown')
        
        stock_summaries.append(
            f"{i}. {symbol} (Score: {score:.1f}, Pred: {prediction:+.2f}, Sector: {sector})"
        )
    
    prompt = f"""Re-rank these top {market} stock opportunities considering qualitative factors:

{chr(10).join(stock_summaries)}

Consider:
- Sector momentum and outlook
- Recent news and catalysts
- Competitive advantages
- Management quality
- Market conditions

Provide re-ranked order (top {top_n}) with brief justification.

Format:
1. SYMBOL - adjustment (+5 / -3 / 0) - reason
2. SYMBOL - adjustment - reason
...

Be concise but precise."""
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert portfolio manager. Re-rank stocks considering qualitative factors."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=500
        )
        
        content = response.choices[0].message.content
        
        # Parse AI adjustments
        adjustments = {}
        for line in content.split('\n'):
            if '. ' in line and ('(' in line or '+' in line or '-' in line):
                parts = line.split('-')
                if len(parts) >= 2:
                    symbol_part = parts[0].split('.')[1].strip() if '.' in parts[0] else parts[0].strip()
                    symbol = symbol_part.split()[0].strip()
                    
                    adjustment_str = parts[1].strip()
                    adjustment = 0
                    if '+' in adjustment_str:
                        adjustment = int(''.join(filter(str.isdigit, adjustment_str.split('+')[1].split()[0])))
                    elif '-' in adjustment_str:
                        adjustment = -int(''.join(filter(str.isdigit, adjustment_str.split('-')[1].split()[0])))
                    
                    reason = parts[2].strip() if len(parts) > 2 else "AI adjustment"
                    adjustments[symbol] = {'adjustment': adjustment, 'reason': reason}
        
        # Apply AI adjustments
        for opp in opportunities:
            symbol = opp.get('symbol', '')
            if symbol in adjustments:
                # Convert to float (might be strings)
                try:
                    old_score = float(opp.get('opportunity_score', 0))
                except (ValueError, TypeError):
                    old_score = 0.0
                
                adjustment = adjustments[symbol]['adjustment']
                new_score = max(0, min(100, old_score + adjustment))
                
                opp['opportunity_score'] = new_score
                opp['ai_adjustment'] = adjustment
                opp['ai_reason'] = adjustments[symbol]['reason']
                
                logger.info(f"  {symbol}: {old_score:.1f} → {new_score:.1f} ({adjustment:+d}) - {adjustments[symbol]['reason']}")
        
        # Re-sort by adjusted scores
        opportunities.sort(key=lambda x: x.get('opportunity_score', 0), reverse=True)
        
        logger.info(f"✅ AI Re-Ranking complete: {len(adjustments)} stocks adjusted")
        return opportunities[:top_n]
        
    except Exception as e:
        logger.error(f"AI re-ranking failed: {e}")
        return opportunities[:top_n]


def build_prompt(opportunity: Dict, market: str = "ASX") -> str:
    """
    Build a comprehensive research prompt for ChatGPT.
    
    Args:
        opportunity: Stock opportunity data with predictions and scores
        market: Market identifier ("ASX" or "US")
        
    Returns:
        Formatted prompt string for ChatGPT
    """
    symbol = opportunity.get('symbol', 'N/A')
    company = opportunity.get('company_name', 'Unknown')
    sector = opportunity.get('sector', 'Unknown')
    
    # Convert numeric fields to float (might be strings)
    try:
        opp_score = float(opportunity.get('opportunity_score', 0))
    except (ValueError, TypeError):
        opp_score = 0.0
    
    try:
        prediction = float(opportunity.get('prediction', 0))
    except (ValueError, TypeError):
        prediction = 0.0
    
    try:
        confidence = float(opportunity.get('confidence', 0))
    except (ValueError, TypeError):
        confidence = 0.0
    
    # Extract technical indicators
    technical = opportunity.get('technical', {})
    rsi = technical.get('rsi', 'N/A')
    macd = technical.get('macd_signal', 'N/A')
    volume_trend = technical.get('volume_trend', 'N/A')
    
    # Extract sentiment
    sentiment = opportunity.get('sentiment', {})
    sent_direction = sentiment.get('direction', 'neutral')
    
    try:
        sent_confidence = float(sentiment.get('confidence', 0))
    except (ValueError, TypeError):
        sent_confidence = 0.0
    
    # Market-specific context
    market_context = ""
    if market == "ASX":
        market_context = "Australian market (ASX)"
    elif market == "US":
        market_context = "US market"
    
    prompt = f"""You are a professional stock market analyst. Perform a comprehensive research analysis on the following stock opportunity identified by our overnight screening system.

**Stock Details:**
- Symbol: {symbol}
- Company: {company}
- Market: {market_context}
- Sector: {sector}
- Opportunity Score: {opp_score:.1f}/100

**Screening Predictions:**
- Predicted Direction: {'Bullish' if prediction > 0 else 'Bearish'} ({prediction:+.2f})
- Confidence Level: {confidence:.1f}%

**Technical Indicators:**
- RSI: {rsi}
- MACD Signal: {macd}
- Volume Trend: {volume_trend}

**Sentiment Analysis:**
- Direction: {sent_direction}
- Confidence: {sent_confidence:.1f}%

**Research Requirements:**
Please provide a comprehensive analysis covering:

1. **Company Overview**
   - Business model and core operations
   - Competitive position in {sector} sector
   - Key products/services and revenue streams

2. **Fundamental Analysis**
   - Recent financial performance (if publicly available)
   - Key financial metrics and ratios
   - Management quality and corporate governance
   - Growth drivers and catalysts

3. **Technical Analysis Context**
   - Current price action and trend
   - Support and resistance levels (if applicable)
   - Volume analysis and market interest
   - Integration with provided technical indicators

4. **Market Context**
   - Sector trends and outlook for {sector}
   - {market_context} conditions and impact
   - Competitive landscape
   - Regulatory or industry-specific factors

5. **Risk Assessment**
   - Key risks and challenges
   - Volatility considerations
   - Downside scenarios
   - Risk mitigation strategies

6. **Investment Thesis**
   - Bull case: Why this is a good opportunity
   - Bear case: What could go wrong
   - Expected holding period
   - Price targets (if applicable)

7. **Recommendation Summary**
   - Overall recommendation (Strong Buy/Buy/Hold/Sell/Strong Sell)
   - Rationale for recommendation
   - Entry points and stop-loss suggestions
   - Position sizing considerations

**Output Format:**
Please provide your analysis in clear, professional markdown format with proper headers and bullet points. Focus on actionable insights for traders and investors.
"""
    
    return prompt


def run_chatgpt_research(
    opportunities: List[Dict],
    model: str = "gpt-4o-mini",
    max_stocks: int = 5,
    market: str = "ASX"
) -> Dict[str, str]:
    """
    Run ChatGPT research on top stock opportunities.
    
    Args:
        opportunities: List of opportunity dictionaries from pipeline
        model: OpenAI model to use (default: gpt-4o-mini)
        max_stocks: Maximum number of stocks to research
        market: Market identifier ("ASX" or "US")
        
    Returns:
        Dictionary mapping symbols to research markdown
    """
    logger.info(f"🔬 Starting ChatGPT research for top {max_stocks} {market} opportunities...")
    
    # Check OpenAI availability
    client = get_client()
    if not client:
        logger.error("❌ ChatGPT research unavailable - OpenAI client not initialized")
        return {}
    
    # Limit to max_stocks
    top_opportunities = opportunities[:max_stocks]
    
    research_results = {}
    
    for idx, opportunity in enumerate(top_opportunities, 1):
        symbol = opportunity.get('symbol', 'UNKNOWN')
        
        try:
            logger.info(f"  📊 Researching {symbol} ({idx}/{len(top_opportunities)})...")
            
            # Build prompt
            prompt = build_prompt(opportunity, market=market)
            
            # Call ChatGPT API
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert stock market analyst with deep knowledge of fundamental and technical analysis. Provide detailed, actionable investment research."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            # Extract research content
            research_content = response.choices[0].message.content
            research_results[symbol] = research_content
            
            logger.info(f"  ✅ Research complete for {symbol} ({len(research_content)} chars)")
            
        except Exception as e:
            logger.error(f"  ❌ Research failed for {symbol}: {e}")
            research_results[symbol] = f"# Research Error\n\nFailed to generate research for {symbol}: {str(e)}"
    
    logger.info(f"✅ ChatGPT research complete: {len(research_results)}/{len(top_opportunities)} successful")
    
    return research_results


def save_markdown(
    research_results: Dict[str, str],
    output_path: Path,
    market: str = "ASX",
    pipeline_metadata: Optional[Dict] = None
) -> Path:
    """
    Save research results to a markdown file.
    
    Args:
        research_results: Dictionary mapping symbols to research markdown
        output_path: Path to output markdown file
        market: Market identifier ("ASX" or "US")
        pipeline_metadata: Optional metadata from pipeline (timestamp, scores, etc.)
        
    Returns:
        Path to saved markdown file
    """
    try:
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Build markdown document
        markdown_content = []
        
        # Header
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        markdown_content.append(f"# {market} Stock Research Report")
        markdown_content.append(f"\n**Generated:** {timestamp}")
        markdown_content.append(f"\n**Market:** {market}")
        
        if pipeline_metadata:
            markdown_content.append(f"\n**Pipeline Run:** {pipeline_metadata.get('run_id', 'N/A')}")
            markdown_content.append(f"\n**Total Opportunities:** {pipeline_metadata.get('total_opportunities', 'N/A')}")
        
        markdown_content.append("\n---\n")
        
        # Table of contents
        markdown_content.append("## Table of Contents\n")
        for idx, symbol in enumerate(research_results.keys(), 1):
            markdown_content.append(f"{idx}. [{symbol}](#{symbol.lower().replace('.', '-')})")
        markdown_content.append("\n---\n")
        
        # Individual research sections
        for symbol, research in research_results.items():
            markdown_content.append(f"\n## {symbol}\n")
            markdown_content.append(research)
            markdown_content.append("\n---\n")
        
        # Footer
        markdown_content.append("\n---")
        markdown_content.append("\n*This research report was generated by the Overnight Stock Screener with ChatGPT analysis.*")
        markdown_content.append("\n*Disclaimer: This is not financial advice. Always conduct your own research and consult with a licensed financial advisor.*")
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(markdown_content))
        
        logger.info(f"💾 Research report saved: {output_path}")
        logger.info(f"   - {len(research_results)} stocks analyzed")
        logger.info(f"   - {len('\n'.join(markdown_content))} characters")
        
        return output_path
        
    except Exception as e:
        logger.error(f"❌ Failed to save research markdown: {e}")
        raise


def test_chatgpt_connection() -> bool:
    """
    Test ChatGPT connection and API key.
    
    Returns:
        True if connection successful, False otherwise
    """
    client = get_client()
    if not client:
        return False
    
    try:
        # Test with minimal request
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )
        logger.info("✅ ChatGPT connection test successful")
        return True
    except Exception as e:
        logger.error(f"❌ ChatGPT connection test failed: {e}")
        return False


if __name__ == "__main__":
    # Test module
    print("ChatGPT Research Module Test")
    print("=" * 50)
    
    # Test connection
    print("\n1. Testing OpenAI connection...")
    if test_chatgpt_connection():
        print("   ✅ Connection successful")
    else:
        print("   ❌ Connection failed")
        print("   Make sure OPENAI_API_KEY is set")
    
    # Test with sample data
    print("\n2. Testing research generation...")
    sample_opportunity = {
        'symbol': 'AAPL',
        'company_name': 'Apple Inc.',
        'sector': 'Technology',
        'opportunity_score': 85.5,
        'prediction': 0.65,
        'confidence': 78.2,
        'technical': {
            'rsi': 55.2,
            'macd_signal': 'bullish',
            'volume_trend': 'increasing'
        },
        'sentiment': {
            'direction': 'positive',
            'confidence': 72.5
        }
    }
    
    results = run_chatgpt_research(
        [sample_opportunity],
        model="gpt-4o-mini",
        max_stocks=1,
        market="US"
    )
    
    if results:
        print(f"   ✅ Generated {len(results)} research report(s)")
        
        # Save test report
        test_path = Path("test_research_report.md")
        save_markdown(results, test_path, market="US")
        print(f"   💾 Saved to: {test_path}")
    else:
        print("   ❌ Research generation failed")
