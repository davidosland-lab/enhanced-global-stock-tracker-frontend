#!/usr/bin/env python3
"""
Comprehensive Sentiment Analyzer
Analyzes market sentiment from multiple sources including:
- Earnings reports
- Global conditions (war, pandemic, geopolitical events)
- Interest rate announcements
- Government economic announcements
- GDP data
- Jobs figures
- Budget announcements
"""

import yfinance as yf
import requests
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class ComprehensiveSentimentAnalyzer:
    """
    Analyzes sentiment from multiple economic and market sources
    """
    
    def __init__(self):
        self.sentiment_cache = {}
        self.last_update = {}
        
        # Sentiment keywords for different categories
        self.keywords = {
            'positive_economic': [
                'growth', 'surge', 'rally', 'breakthrough', 'record high', 'beat expectations',
                'strong earnings', 'bullish', 'expansion', 'recovery', 'boost', 'gain',
                'outperform', 'upgrade', 'positive', 'optimistic', 'improve'
            ],
            'negative_economic': [
                'recession', 'crisis', 'crash', 'decline', 'plunge', 'bear', 'downturn',
                'layoffs', 'unemployment', 'inflation', 'stagflation', 'default', 'bankruptcy',
                'miss expectations', 'downgrade', 'concern', 'fear', 'uncertainty', 'volatile'
            ],
            'war_conflict': [
                'war', 'conflict', 'invasion', 'military', 'sanctions', 'geopolitical',
                'tensions', 'escalation', 'nuclear', 'missile', 'attack', 'hostility'
            ],
            'pandemic_health': [
                'pandemic', 'covid', 'virus', 'outbreak', 'lockdown', 'quarantine',
                'variant', 'surge in cases', 'health crisis', 'emergency'
            ],
            'interest_rates': [
                'fed', 'federal reserve', 'interest rate', 'fomc', 'monetary policy',
                'hawkish', 'dovish', 'tightening', 'easing', 'inflation target'
            ],
            'economic_data': [
                'gdp', 'jobs report', 'employment', 'cpi', 'ppi', 'retail sales',
                'manufacturing', 'services', 'trade balance', 'consumer confidence'
            ]
        }
        
        # Impact weights for different event types
        self.impact_weights = {
            'earnings': 0.15,
            'interest_rates': 0.20,
            'economic_data': 0.15,
            'geopolitical': 0.20,
            'pandemic': 0.10,
            'government_policy': 0.10,
            'market_technical': 0.10
        }
    
    def analyze_earnings_sentiment(self, symbol: str) -> Dict:
        """
        Analyze sentiment from earnings reports and guidance
        """
        try:
            ticker = yf.Ticker(symbol)
            
            # Get earnings data
            earnings = ticker.earnings_history if hasattr(ticker, 'earnings_history') else pd.DataFrame()
            
            if not earnings.empty and len(earnings) > 0:
                # Check last 4 quarters
                recent_earnings = earnings.tail(4)
                
                # Calculate beat/miss ratio
                beats = sum(1 for _, row in recent_earnings.iterrows() 
                          if row.get('epsActual', 0) > row.get('epsEstimate', 0))
                beat_ratio = beats / len(recent_earnings)
                
                # Get revenue growth
                info = ticker.info
                revenue_growth = info.get('revenueGrowth', 0) if info else 0
                
                # Calculate earnings sentiment score
                earnings_score = 0.5  # Neutral base
                earnings_score += (beat_ratio - 0.5) * 0.4  # Adjust based on beat ratio
                earnings_score += min(max(revenue_growth, -0.2), 0.2) * 0.5  # Revenue impact
                
                return {
                    'score': float(min(max(earnings_score, 0), 1)),
                    'beat_ratio': float(beat_ratio),
                    'revenue_growth': float(revenue_growth) if revenue_growth else 0,
                    'confidence': 0.8 if len(recent_earnings) >= 4 else 0.5
                }
            
        except Exception as e:
            logger.warning(f"Error analyzing earnings for {symbol}: {e}")
        
        return {'score': 0.5, 'beat_ratio': 0.5, 'revenue_growth': 0, 'confidence': 0.3}
    
    def analyze_global_conditions(self) -> Dict:
        """
        Analyze global conditions including war, pandemic, geopolitical events
        """
        sentiment_score = 0.5  # Neutral base
        events = []
        
        try:
            # Check VIX for market fear
            vix = yf.Ticker("^VIX").history(period="5d")
            if not vix.empty:
                current_vix = vix['Close'].iloc[-1]
                vix_change = (vix['Close'].iloc[-1] - vix['Close'].iloc[0]) / vix['Close'].iloc[0]
                
                # High VIX indicates fear
                if current_vix > 30:
                    sentiment_score -= 0.2
                    events.append("High market volatility (VIX > 30)")
                elif current_vix < 15:
                    sentiment_score += 0.1
                    events.append("Low market volatility (VIX < 15)")
                
                # Rapid VIX increase indicates emerging crisis
                if vix_change > 0.2:
                    sentiment_score -= 0.15
                    events.append("Rapidly increasing volatility")
            
            # Check global indices for coordination
            indices = {
                '^GSPC': 'S&P 500',
                '^DJI': 'Dow Jones',
                '^IXIC': 'NASDAQ',
                '^FTSE': 'FTSE 100',
                '^N225': 'Nikkei'
            }
            
            declining = 0
            for idx, name in indices.items():
                try:
                    data = yf.Ticker(idx).history(period="5d")
                    if not data.empty:
                        change = (data['Close'].iloc[-1] - data['Close'].iloc[0]) / data['Close'].iloc[0]
                        if change < -0.03:  # 3% decline in 5 days
                            declining += 1
                except:
                    pass
            
            if declining >= 3:
                sentiment_score -= 0.15
                events.append(f"Global market decline ({declining}/5 indices down)")
            elif declining == 0:
                sentiment_score += 0.05
                events.append("Global markets stable")
            
            # Check for specific crisis indicators
            # In production, this would connect to news APIs
            # For now, use proxy indicators
            
            # Gold as safe haven indicator
            gold = yf.Ticker("GLD").history(period="5d")
            if not gold.empty:
                gold_change = (gold['Close'].iloc[-1] - gold['Close'].iloc[0]) / gold['Close'].iloc[0]
                if gold_change > 0.02:  # Gold up 2% in 5 days
                    sentiment_score -= 0.1
                    events.append("Flight to safety (Gold rising)")
            
            # Dollar strength as crisis indicator
            dxy = yf.Ticker("DX-Y.NYB").history(period="5d")
            if not dxy.empty:
                dxy_change = (dxy['Close'].iloc[-1] - dxy['Close'].iloc[0]) / dxy['Close'].iloc[0]
                if dxy_change > 0.02:
                    sentiment_score -= 0.05
                    events.append("Dollar strengthening (risk-off)")
                    
        except Exception as e:
            logger.warning(f"Error analyzing global conditions: {e}")
        
        return {
            'score': float(min(max(sentiment_score, 0), 1)),
            'events': events,
            'confidence': 0.7
        }
    
    def analyze_interest_rates(self) -> Dict:
        """
        Analyze interest rate environment and central bank policy
        """
        sentiment_score = 0.5
        rate_info = {}
        
        try:
            # 10-Year Treasury Yield
            tny = yf.Ticker("^TNX").history(period="1mo")
            if not tny.empty:
                current_yield = tny['Close'].iloc[-1]
                yield_change = (tny['Close'].iloc[-1] - tny['Close'].iloc[0]) / tny['Close'].iloc[0]
                
                rate_info['10y_yield'] = float(current_yield)
                rate_info['yield_change'] = float(yield_change)
                
                # Rising rates typically negative for stocks
                if yield_change > 0.1:  # 10% increase in yields
                    sentiment_score -= 0.15
                    rate_info['trend'] = 'Rising sharply'
                elif yield_change > 0.05:
                    sentiment_score -= 0.08
                    rate_info['trend'] = 'Rising'
                elif yield_change < -0.05:
                    sentiment_score += 0.05
                    rate_info['trend'] = 'Falling'
                else:
                    rate_info['trend'] = 'Stable'
                
                # Absolute level matters too
                if current_yield > 4.5:
                    sentiment_score -= 0.1
                    rate_info['level'] = 'High'
                elif current_yield < 3.0:
                    sentiment_score += 0.05
                    rate_info['level'] = 'Low'
                else:
                    rate_info['level'] = 'Moderate'
            
            # Check yield curve (2y vs 10y)
            tny2 = yf.Ticker("^IRX").history(period="1mo")  # 3-month as proxy
            if not tny2.empty and not tny.empty:
                curve = tny['Close'].iloc[-1] - (tny2['Close'].iloc[-1] * 4)  # Approximate 2y
                if curve < 0:
                    sentiment_score -= 0.15
                    rate_info['yield_curve'] = 'Inverted (recession signal)'
                else:
                    rate_info['yield_curve'] = 'Normal'
                    
        except Exception as e:
            logger.warning(f"Error analyzing interest rates: {e}")
            
        return {
            'score': float(min(max(sentiment_score, 0), 1)),
            'rate_info': rate_info,
            'confidence': 0.8
        }
    
    def analyze_economic_data(self) -> Dict:
        """
        Analyze economic indicators (GDP, jobs, CPI, etc.)
        """
        sentiment_score = 0.5
        indicators = {}
        
        try:
            # Use sector ETFs as proxy for economic health
            sectors = {
                'XLF': 'Financials',  # Interest rate sensitive
                'XLY': 'Consumer Discretionary',  # Economic health
                'XLP': 'Consumer Staples',  # Defensive
                'XLI': 'Industrials',  # Economic activity
                'XLE': 'Energy',  # Inflation/growth
            }
            
            bullish_sectors = 0
            for symbol, name in sectors.items():
                try:
                    data = yf.Ticker(symbol).history(period="1mo")
                    if not data.empty:
                        change = (data['Close'].iloc[-1] - data['Close'].iloc[0]) / data['Close'].iloc[0]
                        indicators[name] = float(change)
                        if change > 0.02:  # 2% gain in a month
                            bullish_sectors += 1
                except:
                    pass
            
            # Adjust sentiment based on sector performance
            sector_sentiment = (bullish_sectors / len(sectors))
            sentiment_score = 0.3 + (sector_sentiment * 0.4)
            
            # Check unemployment proxy (inverse correlation)
            # In production, would use actual data feeds
            indicators['sector_strength'] = bullish_sectors
            
            # Check commodity prices as economic indicators
            oil = yf.Ticker("CL=F").history(period="1mo")
            if not oil.empty:
                oil_change = (oil['Close'].iloc[-1] - oil['Close'].iloc[0]) / oil['Close'].iloc[0]
                indicators['oil_change'] = float(oil_change)
                
                # Moderate oil prices are good, extremes are bad
                if -0.1 < oil_change < 0.1:
                    sentiment_score += 0.05
                elif oil_change > 0.2 or oil_change < -0.2:
                    sentiment_score -= 0.1
                    
        except Exception as e:
            logger.warning(f"Error analyzing economic data: {e}")
            
        return {
            'score': float(min(max(sentiment_score, 0), 1)),
            'indicators': indicators,
            'confidence': 0.6
        }
    
    def analyze_government_policy(self, region: str = "US") -> Dict:
        """
        Analyze government policy impacts (budget, stimulus, regulations)
        """
        sentiment_score = 0.5
        policy_factors = {}
        
        try:
            # Check government bond yields for fiscal health
            if region == "US":
                # Check treasury yields for fiscal concerns
                tlt = yf.Ticker("TLT").history(period="1mo")  # Long-term bonds
                if not tlt.empty:
                    bond_change = (tlt['Close'].iloc[-1] - tlt['Close'].iloc[0]) / tlt['Close'].iloc[0]
                    
                    if bond_change < -0.03:  # Bonds selling off
                        sentiment_score -= 0.1
                        policy_factors['fiscal_concern'] = 'Rising'
                    elif bond_change > 0.03:  # Flight to safety
                        sentiment_score -= 0.05
                        policy_factors['fiscal_concern'] = 'Risk aversion'
                    else:
                        policy_factors['fiscal_concern'] = 'Stable'
                
                # Check infrastructure/government spending proxies
                infra = yf.Ticker("PAVE").history(period="1mo")  # Infrastructure ETF
                if not infra.empty:
                    infra_change = (infra['Close'].iloc[-1] - infra['Close'].iloc[0]) / infra['Close'].iloc[0]
                    policy_factors['infrastructure'] = float(infra_change)
                    if infra_change > 0.03:
                        sentiment_score += 0.05
                        
        except Exception as e:
            logger.warning(f"Error analyzing government policy: {e}")
            
        return {
            'score': float(min(max(sentiment_score, 0), 1)),
            'policy_factors': policy_factors,
            'confidence': 0.5
        }
    
    def calculate_comprehensive_sentiment(self, symbol: str) -> float:
        """
        Calculate the comprehensive sentiment score (0-1) as the 36th feature
        This is the main method that will be called by the ML system
        """
        
        # Get all component scores
        earnings = self.analyze_earnings_sentiment(symbol)
        global_conditions = self.analyze_global_conditions()
        interest_rates = self.analyze_interest_rates()
        economic_data = self.analyze_economic_data()
        government_policy = self.analyze_government_policy()
        
        # Calculate weighted sentiment
        components = {
            'earnings': earnings['score'] * self.impact_weights['earnings'],
            'global': global_conditions['score'] * self.impact_weights['geopolitical'],
            'rates': interest_rates['score'] * self.impact_weights['interest_rates'],
            'economic': economic_data['score'] * self.impact_weights['economic_data'],
            'policy': government_policy['score'] * self.impact_weights['government_policy']
        }
        
        # Market technical sentiment (simplified)
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1mo")
            if not hist.empty:
                # Simple technical sentiment
                price_change = (hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0]
                sma_20 = hist['Close'].rolling(window=20).mean().iloc[-1]
                technical_score = 0.5
                
                if hist['Close'].iloc[-1] > sma_20:
                    technical_score += 0.2
                if price_change > 0:
                    technical_score += min(price_change, 0.3)
                    
                components['technical'] = technical_score * self.impact_weights['market_technical']
            else:
                components['technical'] = 0.5 * self.impact_weights['market_technical']
        except:
            components['technical'] = 0.5 * self.impact_weights['market_technical']
        
        # Sum all weighted components
        comprehensive_sentiment = sum(components.values())
        
        # Ensure score is between 0 and 1
        comprehensive_sentiment = min(max(comprehensive_sentiment, 0), 1)
        
        # Store detailed breakdown for analysis
        self.last_sentiment_breakdown = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'comprehensive_score': float(comprehensive_sentiment),
            'components': components,
            'details': {
                'earnings': earnings,
                'global_conditions': global_conditions,
                'interest_rates': interest_rates,
                'economic_data': economic_data,
                'government_policy': government_policy
            }
        }
        
        return float(comprehensive_sentiment)
    
    def get_sentiment_interpretation(self, score: float) -> Dict:
        """
        Interpret the sentiment score for trading decisions
        """
        if score >= 0.7:
            return {
                'label': 'VERY BULLISH',
                'action': 'Strong Buy',
                'description': 'Highly favorable conditions across multiple factors'
            }
        elif score >= 0.6:
            return {
                'label': 'BULLISH',
                'action': 'Buy',
                'description': 'Positive sentiment with good economic backdrop'
            }
        elif score >= 0.4:
            return {
                'label': 'NEUTRAL',
                'action': 'Hold',
                'description': 'Mixed signals, no clear direction'
            }
        elif score >= 0.3:
            return {
                'label': 'BEARISH',
                'action': 'Reduce/Sell',
                'description': 'Negative sentiment emerging'
            }
        else:
            return {
                'label': 'VERY BEARISH',
                'action': 'Strong Sell',
                'description': 'Multiple risk factors present'
            }


# Singleton instance for use in ML system
sentiment_analyzer = ComprehensiveSentimentAnalyzer()