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


def get_client():
    """
    Get OpenAI client instance.
    
    Returns:
        OpenAI client if API key is available, None otherwise
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("❌ OPENAI_API_KEY environment variable not set")
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
    opp_score = opportunity.get('opportunity_score', 0)
    prediction = opportunity.get('prediction', 0)
    confidence = opportunity.get('confidence', 0)
    
    # Extract technical indicators
    technical = opportunity.get('technical', {})
    rsi = technical.get('rsi', 'N/A')
    macd = technical.get('macd_signal', 'N/A')
    volume_trend = technical.get('volume_trend', 'N/A')
    
    # Extract sentiment
    sentiment = opportunity.get('sentiment', {})
    sent_direction = sentiment.get('direction', 'neutral')
    sent_confidence = sentiment.get('confidence', 0)
    
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
