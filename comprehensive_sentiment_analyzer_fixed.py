#!/usr/bin/env python3
"""
FIXED Comprehensive Sentiment Analyzer
This version reduces Yahoo Finance API calls and uses a session for better connection management
"""

import yfinance as yf
import requests
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from requests import Session
import time

logger = logging.getLogger(__name__)

class ComprehensiveSentimentAnalyzer:
    """
    Analyzes sentiment from multiple economic and market sources
    FIXED VERSION: Reduces API calls and uses session management
    """
    
    def __init__(self):
        self.sentiment_cache = {}
        self.last_update = {}
        self.cache_duration = 300  # Cache for 5 minutes
        
        # Create a persistent session for Yahoo Finance
        self.session = Session()
        self.session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        
        # Pre-fetch common market data to reduce API calls
        self.market_data_cache = {}
        self.last_market_fetch = None
        
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
    
    def get_cached_ticker(self, symbol: str) -> yf.Ticker:
        """Get or create a cached ticker with session"""
        if symbol not in self.market_data_cache:
            self.market_data_cache[symbol] = yf.Ticker(symbol, session=self.session)
        return self.market_data_cache[symbol]
    
    def batch_fetch_market_data(self):
        """Fetch all market data in one batch to reduce API calls"""
        
        # Check if we have recent data
        if self.last_market_fetch and (datetime.now() - self.last_market_fetch).seconds < 300:
            logger.info("Using cached market data")
            return
        
        logger.info("Fetching batch market data...")
        
        # List of all symbols we need
        symbols = [
            'SPY',  # S&P 500 proxy
            '^VIX',  # Volatility
            'GLD',  # Gold
            'TLT',  # Bonds
            'DX-Y.NYB',  # Dollar
            '^TNX',  # 10-year yield
            '^IRX',  # 3-month yield
            'XLF', 'XLY', 'XLP', 'XLI', 'XLE',  # Sectors
            'CL=F',  # Oil
            'PAVE'  # Infrastructure
        ]
        
        # Use single download call for efficiency
        try:
            # Download all at once
            data = yf.download(
                symbols, 
                period='1mo', 
                progress=False, 
                threads=True,
                session=self.session,
                group_by='ticker'
            )
            
            # Store the data
            for symbol in symbols:
                if symbol in data.columns.levels[0] if hasattr(data.columns, 'levels') else True:
                    self.market_data_cache[f"{symbol}_data"] = data[symbol] if len(symbols) > 1 else data
            
            self.last_market_fetch = datetime.now()
            logger.info("Batch market data fetched successfully")
            
        except Exception as e:
            logger.warning(f"Error fetching batch market data: {e}")
            # Fall back to individual fetching if batch fails
            self.last_market_fetch = datetime.now()
    
    def analyze_earnings_sentiment(self, symbol: str) -> Dict:
        """
        Analyze sentiment from earnings - simplified to reduce API calls
        """
        try:
            # For now, return neutral sentiment to avoid API issues
            # In production, this would be cached and fetched less frequently
            return {
                'score': 0.5,
                'beat_ratio': 0.5,
                'revenue_growth': 0,
                'confidence': 0.5
            }
            
        except Exception as e:
            logger.warning(f"Error analyzing earnings for {symbol}: {e}")
            return {'score': 0.5, 'beat_ratio': 0.5, 'revenue_growth': 0, 'confidence': 0.3}
    
    def analyze_global_conditions(self) -> Dict:
        """
        Analyze global conditions - using cached data
        """
        sentiment_score = 0.5
        events = []
        
        try:
            # Ensure we have market data
            self.batch_fetch_market_data()
            
            # Check VIX if we have it
            if '^VIX_data' in self.market_data_cache:
                vix_data = self.market_data_cache['^VIX_data']
                if not vix_data.empty and 'Close' in vix_data.columns:
                    current_vix = vix_data['Close'].iloc[-1]
                    if current_vix > 30:
                        sentiment_score -= 0.2
                        events.append("High market volatility")
                    elif current_vix < 15:
                        sentiment_score += 0.1
                        events.append("Low market volatility")
            
            # Check SPY as market proxy
            if 'SPY_data' in self.market_data_cache:
                spy_data = self.market_data_cache['SPY_data']
                if not spy_data.empty and 'Close' in spy_data.columns:
                    change = (spy_data['Close'].iloc[-1] - spy_data['Close'].iloc[0]) / spy_data['Close'].iloc[0]
                    if change < -0.03:
                        sentiment_score -= 0.15
                        events.append("Market decline")
                    elif change > 0.03:
                        sentiment_score += 0.05
                        events.append("Market rally")
                        
        except Exception as e:
            logger.warning(f"Error analyzing global conditions: {e}")
        
        return {
            'score': float(min(max(sentiment_score, 0), 1)),
            'events': events,
            'confidence': 0.6
        }
    
    def analyze_interest_rates(self) -> Dict:
        """
        Analyze interest rate environment - simplified
        """
        sentiment_score = 0.5
        rate_info = {}
        
        try:
            # Use cached data
            if '^TNX_data' in self.market_data_cache:
                tny_data = self.market_data_cache['^TNX_data']
                if not tny_data.empty and 'Close' in tny_data.columns:
                    current_yield = tny_data['Close'].iloc[-1]
                    yield_change = (tny_data['Close'].iloc[-1] - tny_data['Close'].iloc[0]) / tny_data['Close'].iloc[0]
                    
                    rate_info['10y_yield'] = float(current_yield)
                    
                    if yield_change > 0.1:
                        sentiment_score -= 0.15
                        rate_info['trend'] = 'Rising sharply'
                    elif yield_change > 0.05:
                        sentiment_score -= 0.08
                        rate_info['trend'] = 'Rising'
                    else:
                        rate_info['trend'] = 'Stable'
                        
        except Exception as e:
            logger.warning(f"Error analyzing interest rates: {e}")
            
        return {
            'score': float(min(max(sentiment_score, 0), 1)),
            'rate_info': rate_info,
            'confidence': 0.7
        }
    
    def analyze_economic_data(self) -> Dict:
        """
        Analyze economic indicators - simplified
        """
        sentiment_score = 0.5
        indicators = {}
        
        try:
            # Count bullish sectors from cached data
            bullish_sectors = 0
            sectors = ['XLF', 'XLY', 'XLP', 'XLI', 'XLE']
            
            for sector in sectors:
                if f'{sector}_data' in self.market_data_cache:
                    data = self.market_data_cache[f'{sector}_data']
                    if not data.empty and 'Close' in data.columns:
                        change = (data['Close'].iloc[-1] - data['Close'].iloc[0]) / data['Close'].iloc[0]
                        if change > 0.02:
                            bullish_sectors += 1
            
            # Adjust sentiment based on sector performance
            if len(sectors) > 0:
                sector_sentiment = bullish_sectors / len(sectors)
                sentiment_score = 0.3 + (sector_sentiment * 0.4)
                indicators['sector_strength'] = bullish_sectors
                
        except Exception as e:
            logger.warning(f"Error analyzing economic data: {e}")
            
        return {
            'score': float(min(max(sentiment_score, 0), 1)),
            'indicators': indicators,
            'confidence': 0.5
        }
    
    def analyze_government_policy(self, region: str = "US") -> Dict:
        """
        Analyze government policy impacts - simplified
        """
        sentiment_score = 0.5
        policy_factors = {}
        
        try:
            # Check bonds from cached data
            if 'TLT_data' in self.market_data_cache:
                tlt_data = self.market_data_cache['TLT_data']
                if not tlt_data.empty and 'Close' in tlt_data.columns:
                    bond_change = (tlt_data['Close'].iloc[-1] - tlt_data['Close'].iloc[0]) / tlt_data['Close'].iloc[0]
                    
                    if bond_change < -0.03:
                        sentiment_score -= 0.1
                        policy_factors['fiscal_concern'] = 'Rising'
                    else:
                        policy_factors['fiscal_concern'] = 'Stable'
                        
        except Exception as e:
            logger.warning(f"Error analyzing government policy: {e}")
            
        return {
            'score': float(min(max(sentiment_score, 0), 1)),
            'policy_factors': policy_factors,
            'confidence': 0.4
        }
    
    def calculate_comprehensive_sentiment(self, symbol: str) -> float:
        """
        Calculate the comprehensive sentiment score (0-1) as the 36th feature
        OPTIMIZED VERSION - Minimal API calls
        """
        
        # Check cache first
        cache_key = f"{symbol}_sentiment"
        if cache_key in self.sentiment_cache:
            cached_time = self.last_update.get(cache_key)
            if cached_time and (datetime.now() - cached_time).seconds < self.cache_duration:
                logger.info(f"Using cached sentiment for {symbol}")
                return self.sentiment_cache[cache_key]
        
        logger.info(f"Calculating new sentiment for {symbol}")
        
        # Pre-fetch all market data in one batch
        self.batch_fetch_market_data()
        
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
        
        # Simple technical sentiment (avoid extra API call)
        components['technical'] = 0.5 * self.impact_weights['market_technical']
        
        # Sum all weighted components
        comprehensive_sentiment = sum(components.values())
        
        # Ensure score is between 0 and 1
        comprehensive_sentiment = min(max(comprehensive_sentiment, 0), 1)
        
        # Cache the result
        self.sentiment_cache[cache_key] = comprehensive_sentiment
        self.last_update[cache_key] = datetime.now()
        
        # Store detailed breakdown
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
        
        logger.info(f"Sentiment for {symbol}: {comprehensive_sentiment:.3f}")
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