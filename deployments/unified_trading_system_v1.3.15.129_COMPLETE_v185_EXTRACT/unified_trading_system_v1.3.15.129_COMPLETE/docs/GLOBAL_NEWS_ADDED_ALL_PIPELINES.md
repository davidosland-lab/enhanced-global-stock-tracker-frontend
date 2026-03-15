# Global News Added to All Pipelines - v1.3.15.132

## What Was Changed

### Before (v1.3.15.131)
- **US Pipeline:** Fed news only
- **AU Pipeline:** RBA news only ❌
- **UK Pipeline:** BoE + HM Treasury + Global news ✅

### After (v1.3.15.132)
- **US Pipeline:** Fed news + Global news ✅
- **AU Pipeline:** RBA news + Global news ✅
- **UK Pipeline:** BoE + HM Treasury + Global news ✅

---

## Why This Matters

### Australia (ASX)
Australian markets are **heavily influenced** by global events:
- **China Trade**: Major trading partner, commodities demand
- **US Policies**: Trade tariffs, dollar strength
- **Commodities**: Iron ore, coal, LNG prices affected by global supply/demand
- **Currency**: AUD heavily influenced by USD, commodity prices
- **Asian Markets**: Regional contagion effects

**Example Impact:**
- US-China trade war → Lower iron ore demand → ASX Materials sector down
- Middle East conflict → Oil prices up → ASX Energy sector up
- US Fed rate hike → Strong USD → Weak AUD → ASX exporters benefit

### United States (NYSE/NASDAQ)
Even though the US is a **major global driver**, it's still affected by:
- **Geopolitical Events**: Wars, conflicts affecting oil prices, defense stocks
- **European Crisis**: EU debt, Brexit affecting financial sector
- **Asian Manufacturing**: Supply chain disruptions, China slowdowns
- **Currency Wars**: Competitive devaluation affecting exports
- **Commodity Shocks**: OPEC decisions, energy crises

**Example Impact:**
- Russia-Ukraine war → Energy prices surge → US inflation up
- China lockdowns → Supply chain disruption → US tech stocks down
- European banking crisis → Contagion to US financial sector

---

## Global News Sources (31 Sources)

### Major News Agencies
- Reuters Markets, US, World
- BBC Business, World, US Canada
- Bloomberg Markets
- AP News Business
- AFP News Hub
- Al Jazeera Economy

### Government & Policy
- White House Briefing Room
- US Treasury Press Releases
- US State Department

### European Sources
- European Commission
- ECB News
- European Parliament

### Asian Sources
- PBOC News (China)
- BOJ News (Japan)
- China Daily Business
- Japan Times Business

### Financial Institutions
- IMF News
- World Bank
- BIS Press Releases

---

## Global Keywords Monitored (200+)

### Geopolitical Conflicts
- War, warfare, conflict, military, invasion, occupation
- Ukraine, Russia, Putin, Zelensky, Crimea, Donbas
- Middle East, Gaza, Israel, Palestine, Hamas, Hezbollah
- Iran, Tehran, nuclear, enrichment
- China, Beijing, Xi Jinping, Taiwan, South China Sea
- North Korea, Kim Jong, Pyongyang
- NATO, alliance, military aid, weapons

### US Political Events
- Trump, Biden, president, presidential, administration
- Executive order, veto, policy change, regulatory
- Tariff, duty, trade policy, sanctions
- Immigration, border, deportation
- Shutdown, debt ceiling, default
- Election, campaign, Supreme Court

### International Trade
- Trade war, trade dispute, protectionism
- WTO, free trade agreements
- Supply chain, logistics, shipping, disruption
- Bottleneck, shortage, scarcity

### Market Volatility & Risk
- Uncertainty, volatility, turbulence, instability
- Risk-off, risk-on, safe haven
- Selloff, crash, collapse, plunge, turmoil
- VIX, fear gauge, panic

### Energy & Commodities
- Oil, crude, Brent, WTI, petroleum
- Oil price, oil shock, energy crisis
- OPEC, OPEC+, production cut
- Gas, natural gas, LNG, pipeline
- Coal, fossil fuel, renewable energy
- Metals, gold, silver, copper, iron ore
- Wheat, corn, soy, agriculture, food prices

### Financial Crises & Banking
- Banking crisis, bank failure, bank run
- Financial crisis, credit crisis, liquidity crisis
- Sovereign debt, debt crisis, default
- Contagion, spillover, systemic risk
- Bailout, rescue, intervention

### Currency & Exchange Rates
- Dollar, euro, pound, yen, yuan
- Devaluation, depreciation, appreciation
- Currency war, forex intervention
- Reserve currency

### European Issues
- Brexit, EU, Brussels, European Commission
- Eurozone, Greece, Italy debt
- Migration, refugee crisis

### Asian Economic Issues
- China economy, Chinese growth, China slowdown
- Evergrande, property crisis, real estate
- Japan deflation, Abenomics
- India, Modi, rupee

### Technology & Cyber
- Tech war, chip war, semiconductor
- Huawei, TikTok, tech ban
- Cyber attack, hack, ransomware

### Climate & Environment
- Climate change, global warming
- Carbon emissions, net zero
- Natural disaster, extreme weather
- Hurricane, typhoon, earthquake, flood, wildfire

### Health & Pandemic
- Pandemic, epidemic, outbreak
- COVID, coronavirus, lockdown, vaccine
- WHO, World Health Organization

### Social & Political Unrest
- Protest, demonstration, riot
- Civil unrest, uprising, revolution
- Coup, military takeover, dictatorship
- Corruption, scandal, election fraud

---

## Updated News Flow

### US Pipeline
```
US Overnight Pipeline
    └─> MacroNewsMonitor(market='US')
            ├─> Federal Reserve (Official)
            │   ├─> Press releases
            │   ├─> Speeches (Jerome Powell, etc.)
            │   └─> FOMC calendar
            │
            └─> Global News (31 sources)
                ├─> Reuters (markets, US, world)
                ├─> BBC (business, world, US)
                ├─> Bloomberg Markets
                ├─> Al Jazeera Economy
                └─> 27 more sources...
                
    → FinBERT Sentiment Analysis on all articles
    → Returns US_macro_sentiment
```

### AU Pipeline
```
AU Overnight Pipeline
    └─> MacroNewsMonitor(market='ASX')
            ├─> Reserve Bank of Australia (Official)
            │   ├─> Media releases
            │   ├─> Speeches (Michele Bullock, etc.)
            │   └─> Board minutes
            │
            └─> Global News (31 sources) ← NEWLY ADDED
                ├─> China trade & economy (major impact)
                ├─> US policies & tariffs
                ├─> Commodities (iron ore, coal, LNG)
                ├─> Geopolitical events
                ├─> Currency movements (USD, CNY)
                └─> Regional Asia-Pacific news
                
    → FinBERT Sentiment Analysis on all articles
    → Returns ASX_macro_sentiment
```

### UK Pipeline
```
UK Overnight Pipeline
    └─> MacroNewsMonitor(market='UK')
            ├─> Bank of England (Official)
            │   ├─> News (RSS feed)
            │   ├─> Speeches (Andrew Bailey, etc.)
            │   └─> MPC decisions
            │
            ├─> HM Treasury
            │   ├─> Budget announcements
            │   ├─> Fiscal policy
            │   └─> Government statements
            │
            └─> Global News (31 sources)
                ├─> Brexit impact
                ├─> European Union
                ├─> US-UK relations
                ├─> Global trade
                └─> Geopolitical events
                
    → FinBERT Sentiment Analysis on all articles
    → Returns UK_macro_sentiment
```

---

## Expected Output Changes

### Before (AU Pipeline - RBA Only)
```
================================================================================
MACRO NEWS ANALYSIS - ASX MARKET
================================================================================
  Fetching RBA media releases...
  [OK] RBA Media Releases: 2 articles
  Fetching RBA speeches...
  [OK] RBA Speeches: 1 articles
  FinBERT sentiment: -0.050 (from 3 articles)
[OK] ASX Macro News: 3 articles, Sentiment: NEUTRAL (-0.050)
```

**Issues:**
- Only 3 articles (limited data)
- Misses China trade news affecting ASX Materials
- Misses US tariff news affecting AUD
- Misses commodity price shocks

### After (AU Pipeline - RBA + Global)
```
================================================================================
MACRO NEWS ANALYSIS - ASX MARKET
================================================================================
  Fetching RBA media releases...
  [OK] RBA Media Releases: 2 articles
  Fetching RBA speeches...
  [OK] RBA Speeches: 1 articles
  Fetching comprehensive global news...
    [OK] Found: China announces economic stimulus package...
    [OK] Found: US-China trade talks resume...
    [OK] Found: Iron ore prices surge on supply concerns...
    [OK] Found Geopolitical: Middle East tensions escalate...
    [OK] Found US: Federal Reserve signals rate cuts...
  [OK] Global News: 8 articles (Reuters + BBC + Al Jazeera)
  FinBERT sentiment: +0.185 (from 11 articles)
[OK] ASX Macro News: 11 articles (RBA + Global), Sentiment: BULLISH (+0.185)
```

**Benefits:**
- 11 articles (more comprehensive)
- Captures China stimulus → Positive for ASX
- Captures iron ore surge → Positive for Materials sector
- Captures geopolitical risk → Risk-off sentiment
- Better overall market sentiment assessment

---

## Impact on Trading Decisions

### Scenario 1: China Stimulus Announced
**Without Global News (RBA Only):**
- RBA: Neutral
- Pipeline sentiment: 50 (neutral)
- Trading: Miss bullish opportunity in ASX Materials stocks

**With Global News:**
- RBA: Neutral
- Global: China stimulus + iron ore demand
- Pipeline sentiment: 72 (bullish)
- Trading: ✅ Identify BHP, RIO as BUY opportunities

### Scenario 2: US-China Trade War Escalates
**Without Global News:**
- RBA: Neutral
- Pipeline sentiment: 50
- Trading: Miss bearish signal

**With Global News:**
- RBA: Neutral
- Global: Trade war + commodity demand drop
- Pipeline sentiment: 35 (bearish)
- Trading: ✅ Reduce exposure, avoid commodity stocks

### Scenario 3: Middle East Conflict → Oil Shock
**Without Global News:**
- RBA: Neutral
- Pipeline sentiment: 50
- Trading: Miss energy sector opportunity

**With Global News:**
- RBA: Neutral
- Global: Oil shock + energy crisis
- Pipeline sentiment: 68 (bullish for energy)
- Trading: ✅ Identify WPL, STO as BUY in Energy sector

---

## Files Modified

1. `pipelines/models/screening/macro_news_monitor.py`
   - Line 411-449: `_get_aus_macro_sentiment()` - Added global news scraping
   - Line 373-409: `_get_us_macro_sentiment()` - Added global news scraping
   - Line 449-489: `_get_uk_macro_sentiment()` - Already had global news

---

## Testing

### Test AU Pipeline with Global News
```bash
cd pipelines/models/screening
python -c "from macro_news_monitor import MacroNewsMonitor; monitor = MacroNewsMonitor(market='ASX'); result = monitor.get_macro_sentiment(); print(f'Total Articles: {result[\"article_count\"]}'); print(f'RBA Articles: {sum(1 for a in result[\"articles\"] if \"RBA\" in a[\"source\"])}'); print(f'Global Articles: {sum(1 for a in result[\"articles\"] if \"Global\" in a.get(\"type\", \"\"))}'); print(f'Sentiment: {result[\"sentiment_label\"]} ({result[\"sentiment_score\"]:+.3f})')"
```

### Expected Output
```
Total Articles: 10-15
RBA Articles: 2-4
Global Articles: 6-11
Sentiment: BULLISH/BEARISH/NEUTRAL (±0.XXX)
```

---

## Summary

✅ **Global news added to US pipeline** (Fed + Global)  
✅ **Global news added to AU pipeline** (RBA + Global)  
✅ **UK pipeline unchanged** (already had BoE + HM Treasury + Global)

**Impact:**
- More comprehensive market sentiment (10-15 articles instead of 2-4)
- Better capture of global events affecting local markets
- Improved trading signals for commodity-exposed stocks (ASX)
- Better risk assessment during geopolitical crises

**Version:** v1.3.15.132  
**Status:** ✅ READY FOR TESTING

---

**Next Steps:**
1. Run AU pipeline and verify global news appears in logs
2. Check article count increases from ~3 to ~10-15
3. Verify FinBERT analyzes all articles (RBA + Global)
4. Compare sentiment scores before/after global news integration
