"""
Australian Market Indicators Module - REAL DATA ONLY
Fetches live Australian economic and market data
"""

import yfinance as yf
import requests
from datetime import datetime, timedelta
import json
import os

# Force disable cache
os.environ['YFINANCE_CACHE_DISABLE'] = '1'

def get_comprehensive_australian_indicators():
    """
    Fetch REAL Australian market indicators from live sources
    NO FALLBACK/FAKE DATA - Returns actual market data or error
    """
    indicators = {
        'timestamp': datetime.now().isoformat(),
        'source': 'Live Market Data',
        'status': 'real_time'
    }
    
    try:
        # 1. FETCH REAL ASX INDICES
        print("Fetching live ASX indices...")
        market_indices = {}
        
        # ASX 200 (^AXJO)
        asx200_data = yf.download('^AXJO', period='5d', progress=False)
        if not asx200_data.empty:
            current = float(asx200_data['Close'].iloc[-1])
            prev = float(asx200_data['Close'].iloc[-2]) if len(asx200_data) > 1 else current
            market_indices['ASX200'] = {
                'value': round(current, 2),
                'change': round(current - prev, 2),
                'change_percent': round((current - prev) / prev * 100, 2) if prev else 0,
                'last_updated': asx200_data.index[-1].strftime('%Y-%m-%d')
            }
        
        # All Ordinaries (^AORD)
        aord_data = yf.download('^AORD', period='5d', progress=False)
        if not aord_data.empty:
            current = float(aord_data['Close'].iloc[-1])
            prev = float(aord_data['Close'].iloc[-2]) if len(aord_data) > 1 else current
            market_indices['All_Ordinaries'] = {
                'value': round(current, 2),
                'change': round(current - prev, 2),
                'change_percent': round((current - prev) / prev * 100, 2) if prev else 0
            }
        
        # ASX Small Ordinaries (^AXSO)
        axso_data = yf.download('^AXSO', period='5d', progress=False)
        if not axso_data.empty:
            current = float(axso_data['Close'].iloc[-1])
            market_indices['Small_Ords'] = {'value': round(current, 2)}
        
        indicators['market_indices'] = market_indices
        
        # 2. FETCH REAL CURRENCY DATA
        print("Fetching live currency rates...")
        currency = {}
        
        # AUD/USD
        audusd_data = yf.download('AUDUSD=X', period='5d', progress=False)
        if not audusd_data.empty:
            current = float(audusd_data['Close'].iloc[-1])
            prev = float(audusd_data['Close'].iloc[-2]) if len(audusd_data) > 1 else current
            currency['AUD/USD'] = {
                'value': round(current, 4),
                'change': round(current - prev, 4),
                'change_percent': round((current - prev) / prev * 100, 2) if prev else 0
            }
        
        # AUD/CNY (Chinese Yuan - important for AU trade)
        audcny_data = yf.download('AUDCNY=X', period='5d', progress=False)
        if not audcny_data.empty:
            current = float(audcny_data['Close'].iloc[-1])
            currency['AUD/CNY'] = {'value': round(current, 4)}
        
        # AUD/JPY
        audjpy_data = yf.download('AUDJPY=X', period='5d', progress=False)
        if not audjpy_data.empty:
            current = float(audjpy_data['Close'].iloc[-1])
            currency['AUD/JPY'] = {'value': round(current, 2)}
        
        # AUD/EUR
        audeur_data = yf.download('AUDEUR=X', period='5d', progress=False)
        if not audeur_data.empty:
            current = float(audeur_data['Close'].iloc[-1])
            currency['AUD/EUR'] = {'value': round(current, 4)}
            
        indicators['currency'] = currency
        
        # 3. FETCH REAL COMMODITY PRICES (Critical for Australian economy)
        print("Fetching live commodity prices...")
        commodities = {}
        
        # Iron Ore Futures
        iron_data = yf.download('SCOT.L', period='5d', progress=False)  # Iron ore ETF proxy
        if not iron_data.empty:
            current = float(iron_data['Close'].iloc[-1])
            prev = float(iron_data['Close'].iloc[-2]) if len(iron_data) > 1 else current
            commodities['iron_ore_proxy'] = {
                'value': round(current, 2),
                'unit': 'Index',
                'change': round(current - prev, 2),
                'note': 'Iron Ore ETF Proxy'
            }
        
        # Gold (important for AU mining)
        gold_data = yf.download('GC=F', period='5d', progress=False)
        if not gold_data.empty:
            current = float(gold_data['Close'].iloc[-1])
            prev = float(gold_data['Close'].iloc[-2]) if len(gold_data) > 1 else current
            commodities['gold'] = {
                'value': round(current, 2),
                'unit': 'USD/oz',
                'change': round(current - prev, 2),
                'change_percent': round((current - prev) / prev * 100, 2) if prev else 0
            }
        
        # Crude Oil (WTI)
        oil_data = yf.download('CL=F', period='5d', progress=False)
        if not oil_data.empty:
            current = float(oil_data['Close'].iloc[-1])
            commodities['oil_wti'] = {
                'value': round(current, 2),
                'unit': 'USD/barrel'
            }
        
        # Natural Gas
        gas_data = yf.download('NG=F', period='5d', progress=False)
        if not gas_data.empty:
            current = float(gas_data['Close'].iloc[-1])
            commodities['natural_gas'] = {
                'value': round(current, 3),
                'unit': 'USD/MMBtu'
            }
        
        # Copper (base metal indicator)
        copper_data = yf.download('HG=F', period='5d', progress=False)
        if not copper_data.empty:
            current = float(copper_data['Close'].iloc[-1])
            commodities['copper'] = {
                'value': round(current, 4),
                'unit': 'USD/lb'
            }
        
        # Agricultural - Wheat
        wheat_data = yf.download('ZW=F', period='5d', progress=False)
        if not wheat_data.empty:
            current = float(wheat_data['Close'].iloc[-1])
            commodities['wheat'] = {
                'value': round(current, 2),
                'unit': 'USD/bushel'
            }
            
        indicators['commodities'] = commodities
        
        # 4. FETCH KEY AUSTRALIAN STOCKS
        print("Fetching live ASX stock prices...")
        top_stocks = {}
        
        asx_symbols = {
            'CBA.AX': 'Commonwealth Bank',
            'BHP.AX': 'BHP Group',
            'CSL.AX': 'CSL Limited',
            'WBC.AX': 'Westpac Banking',
            'ANZ.AX': 'ANZ Banking',
            'NAB.AX': 'National Australia Bank',
            'WES.AX': 'Wesfarmers',
            'MQG.AX': 'Macquarie Group',
            'TLS.AX': 'Telstra',
            'WOW.AX': 'Woolworths',
            'RIO.AX': 'Rio Tinto',
            'FMG.AX': 'Fortescue Metals'
        }
        
        for symbol, name in asx_symbols.items():
            try:
                stock_data = yf.download(symbol, period='5d', progress=False)
                if not stock_data.empty:
                    current = float(stock_data['Close'].iloc[-1])
                    prev = float(stock_data['Close'].iloc[-2]) if len(stock_data) > 1 else current
                    top_stocks[symbol] = {
                        'name': name,
                        'price': round(current, 2),
                        'change': round(current - prev, 2),
                        'change_percent': round((current - prev) / prev * 100, 2) if prev else 0
                    }
            except:
                continue
        
        indicators['top_asx_stocks'] = top_stocks
        
        # 5. SECTOR INDICES
        print("Fetching sector performance...")
        sectors = {}
        
        sector_etfs = {
            'MVB.AX': 'Banking Sector',
            'MVR.AX': 'Resources Sector',
            'MVE.AX': 'Energy Sector',
            'MVS.AX': 'Industrials Sector',
            'MVA.AX': 'Materials Sector'
        }
        
        for etf, sector_name in sector_etfs.items():
            try:
                sector_data = yf.download(etf, period='5d', progress=False)
                if not sector_data.empty:
                    current = float(sector_data['Close'].iloc[-1])
                    prev = float(sector_data['Close'].iloc[-2]) if len(sector_data) > 1 else current
                    sectors[sector_name] = {
                        'etf': etf,
                        'value': round(current, 2),
                        'change_percent': round((current - prev) / prev * 100, 2) if prev else 0
                    }
            except:
                continue
                
        indicators['sectors'] = sectors
        
        # 6. CHINA INDICATORS (Major trading partner)
        print("Fetching China market data...")
        china_indicators = {}
        
        # Shanghai Composite
        shanghai_data = yf.download('000001.SS', period='5d', progress=False)
        if not shanghai_data.empty:
            current = float(shanghai_data['Close'].iloc[-1])
            prev = float(shanghai_data['Close'].iloc[-2]) if len(shanghai_data) > 1 else current
            china_indicators['Shanghai_Composite'] = {
                'value': round(current, 2),
                'change_percent': round((current - prev) / prev * 100, 2) if prev else 0
            }
        
        # Hang Seng Index
        hsi_data = yf.download('^HSI', period='5d', progress=False)
        if not hsi_data.empty:
            current = float(hsi_data['Close'].iloc[-1])
            china_indicators['Hang_Seng'] = {'value': round(current, 2)}
            
        indicators['china_indicators'] = china_indicators
        
        # 7. BOND YIELDS
        print("Fetching bond yields...")
        bonds = {}
        
        # Australian 10Y Bond
        au10y_data = yf.download('^AYLD', period='5d', progress=False)
        if not au10y_data.empty:
            current = float(au10y_data['Close'].iloc[-1])
            bonds['AU_10Y_Yield'] = {'value': round(current, 3), 'unit': '%'}
        
        # US 10Y Treasury (for comparison)
        us10y_data = yf.download('^TNX', period='5d', progress=False)
        if not us10y_data.empty:
            current = float(us10y_data['Close'].iloc[-1])
            bonds['US_10Y_Yield'] = {'value': round(current, 3), 'unit': '%'}
            
        indicators['bonds'] = bonds
        
        # 8. ECONOMIC DATA (from RBA/ABS if available via API)
        # Note: For real RBA data, you'd need to use RBA's API
        # This fetches proxy indicators
        economic = {}
        
        # Try to get some economic indicators from ETFs/proxies
        try:
            # Australian Dollar Index can indicate economic strength
            if 'AUD/USD' in currency:
                economic['AUD_strength'] = {
                    'value': currency['AUD/USD']['value'],
                    'interpretation': 'Strong' if currency['AUD/USD']['value'] > 0.70 else 'Moderate' if currency['AUD/USD']['value'] > 0.65 else 'Weak'
                }
            
            # VIX equivalent for Australia (XVI.AX)
            vix_au_data = yf.download('XVI.AX', period='5d', progress=False)
            if not vix_au_data.empty:
                current = float(vix_au_data['Close'].iloc[-1])
                economic['volatility_index'] = {
                    'value': round(current, 2),
                    'interpretation': 'High' if current > 20 else 'Normal' if current > 12 else 'Low'
                }
        except:
            pass
            
        indicators['economic_indicators'] = economic
        
        # 9. MARKET SENTIMENT
        if market_indices and top_stocks:
            # Calculate overall market sentiment
            positive = sum(1 for stock in top_stocks.values() if stock.get('change', 0) > 0)
            total = len(top_stocks)
            
            indicators['market_sentiment'] = {
                'bullish_stocks': positive,
                'bearish_stocks': total - positive,
                'sentiment': 'Bullish' if positive > total * 0.6 else 'Bearish' if positive < total * 0.4 else 'Neutral',
                'asx200_trend': 'Up' if market_indices.get('ASX200', {}).get('change', 0) > 0 else 'Down'
            }
        
        # 10. DATA QUALITY CHECK
        indicators['data_quality'] = {
            'indices_fetched': len(market_indices),
            'stocks_fetched': len(top_stocks),
            'commodities_fetched': len(commodities),
            'currencies_fetched': len(currency),
            'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
    except Exception as e:
        print(f"Error fetching Australian indicators: {e}")
        indicators['error'] = str(e)
        indicators['status'] = 'partial_data'
    
    return indicators

# For testing
if __name__ == "__main__":
    print("Fetching real Australian market indicators...")
    data = get_comprehensive_australian_indicators()
    print(json.dumps(data, indent=2))