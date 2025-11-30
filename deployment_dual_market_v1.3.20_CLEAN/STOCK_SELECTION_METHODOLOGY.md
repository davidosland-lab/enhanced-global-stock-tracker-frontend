# 📊 Stock Selection Methodology
## How the Initial 240 Stocks Are Chosen

**Date**: November 27, 2025  
**Question**: "How do you choose the initial 240 stocks?"  
**Answer**: **Manually curated lists based on market cap, liquidity, and sector representation**

---

## 🎯 Stock Selection Approach

### **Method**: **Hardcoded, Curated Lists** (NOT Dynamic)

Both ASX and US pipelines use **static, manually curated lists** stored in JSON configuration files:

| Market | Config File | Stocks | Sectors | Method |
|--------|------------|--------|---------|--------|
| **ASX** | `models/config/asx_sectors.json` | 240 | 8 | Manual curation |
| **US** | `models/config/us_sectors.json` | 240 | 8 | Manual curation |

---

## 📋 Selection Criteria

### **General Principles**:

1. **Market Cap Focus**: Large-cap and mid-cap stocks
2. **Liquidity**: High average daily volume
3. **Sector Balance**: Equal distribution (30 stocks per sector)
4. **Index Representation**: Most stocks from major indices
5. **Stability**: Established companies with trading history

### **ASX Selection Criteria** (from `asx_sectors.json`):
```json
{
  "min_market_cap": 500000000,      // $500M minimum
  "min_avg_volume": 500000,         // 500K shares/day
  "min_price": 0.50,                // $0.50 minimum
  "max_price": 500.00,              // $500 maximum
  "beta_min": 0.5,                  // Not too stable
  "beta_max": 2.5,                  // Not too volatile
  "max_volatility": 0.5             // 50% max volatility
}
```

### **US Selection Criteria** (from `us_sectors.json`):
```json
{
  "min_price": 1.0,                 // $1 minimum
  "max_price": 2000.0,              // $2000 maximum
  "min_avg_volume": 500000,         // 500K shares/day
  "min_market_cap": 1000000000      // $1B minimum
}
```

---

## 🏢 Sector Breakdown

### **Both Markets Use 8 Sectors**:

| Sector | ASX Stocks | US Stocks | Weight | Focus |
|--------|-----------|-----------|--------|-------|
| **Technology** | 30 | 30 | 1.4 | High growth, innovation |
| **Healthcare** | 30 | 30 | 1.1-1.2 | Pharma, biotech, devices |
| **Financials** | 30 | 30 | 1.1-1.2 | Banks, insurance, services |
| **Materials** | 30 | N/A | 1.3 | Mining, resources (ASX only) |
| **Energy** | 30 | 30 | 1.0-1.2 | Oil, gas, renewables |
| **Industrials** | 30 | 30 | 1.0-1.1 | Manufacturing, infrastructure |
| **Consumer Staples** | 30 | 30 | 0.9-1.0 | Food, beverage, retail |
| **Consumer Discretionary** | N/A | 30 | 1.3 | Retail, automotive (US only) |
| **Communication Services** | N/A | 30 | 1.2 | Telecom, media (US only) |
| **Real Estate** | 30 | N/A | 0.9 | REITs, property (ASX only) |

**Note**: Sectors differ slightly between markets to reflect market characteristics.

---

## 🇺🇸 US Market Stock Selection

### **30 Stocks Per Sector** - Examples:

#### **Technology Sector** (30 stocks):
```
Mega-caps: AAPL, MSFT, GOOGL, NVDA, META
Large-caps: AVGO, ORCL, CSCO, ADBE, CRM
Mid-caps: INTC, AMD, NOW, QCOM, INTU
Growth stocks: AMAT, MU, LRCX, KLAC, SNPS
Emerging leaders: CDNS, MRVL, FTNT, PANW, CRWD
Cybersecurity: ZS, DDOG, NET, SNOW, PLTR
```

**Selection Logic**:
- ✅ Top 5: S&P 500 mega-caps by market cap
- ✅ Next 10: Established tech leaders (Oracle, Cisco, Adobe, etc.)
- ✅ Next 10: Semiconductor & hardware (Intel, AMD, AMAT, etc.)
- ✅ Last 5: High-growth cloud/cybersecurity (Snowflake, Palantir, etc.)

#### **Healthcare Sector** (30 stocks):
```
Insurance: UNH, CVS, CI, HUM, ELV
Big Pharma: JNJ, LLY, ABBV, MRK, PFE
Biotech: TMO, ABT, DHR, AMGN, GILD
Specialty: ISRG, VRTX, REGN, BIIB
Devices: BMY, BSX, SYK, IDXX
Others: ZTS, MCK, COR, IQV, DXCM, EW, GEHC
```

**Selection Logic**:
- ✅ Mix of insurance giants, pharma, biotech, devices
- ✅ S&P 500 healthcare constituents
- ✅ Focus on $1B+ market cap

#### **Financials Sector** (30 stocks):
```
Banks: JPM, BAC, WFC, C, MS, GS
Payment Networks: V, MA
Asset Managers: BRK.B, BLK, BX
Insurance: PGR, CB, MMC, AIG, MET, AFL, ALL, TRV, PRU
Brokers: SCHW, ICE, SPGI
Regional Banks: USB, PNC, TFC, COF
Others: AXP, AON, AMP
```

**Selection Logic**:
- ✅ Top 10 US banks by assets
- ✅ Payment networks (Visa, Mastercard)
- ✅ Major insurers and asset managers

---

## 🇦🇺 ASX Market Stock Selection

### **30 Stocks Per Sector** - Examples:

#### **Financials Sector** (30 stocks):
```
Big 4 Banks: CBA.AX, WBC.AX, ANZ.AX, NAB.AX
Investment: MQG.AX, AMP.AX
Insurance: SUN.AX, QBE.AX, IAG.AX
Smaller Banks: BEN.AX, BOQ.AX, AUB.AX
Wealth Management: HUB.AX, AFG.AX, CPU.AX
REITs: CIP.AX, CQR.AX, CLW.AX
Financial Services: EQT.AX, SDF.AX, NWL.AX
Others: APE.AX, BKW.AX, CHN.AX, IPP.AX, PDL.AX, PTM.AX, ASX.AX
```

**Selection Logic**:
- ✅ All ASX 200 financial sector stocks
- ✅ Focus on Big 4 banks (CBA, WBC, ANZ, NAB)
- ✅ Major insurers and wealth managers

#### **Materials Sector** (30 stocks):
```
Iron Ore: BHP.AX, RIO.AX, FMG.AX, MIN.AX
Diversified: S32.AX (South32)
Gold: NCM.AX, EVN.AX, NST.AX
Coal: WHC.AX, NHC.AX
Oil/Gas: STO.AX, WDS.AX
Nickel: IGO.AX, SFR.AX, OZL.AX
Lithium: PLS.AX, LYC.AX, ORE.AX
Others: AWC.AX, RRL.AX, ILU.AX, ALD.AX, RED.AX, GOR.AX, SAR.AX, JHX.AX, RSG.AX, WGX.AX, PNR.AX, DEG.AX
```

**Selection Logic**:
- ✅ Major miners (BHP, Rio Tinto, Fortescue)
- ✅ Gold producers
- ✅ Lithium/battery metals (focus on EV supply chain)
- ✅ ASX 200 materials constituents

---

## 🔄 How the Lists Were Created

### **Historical Process** (Based on Git History):

1. **Initial Creation**: November 24, 2025
   - Created as part of dual market system development
   - US stocks cloned/adapted from ASX methodology

2. **Selection Methodology**:
   ```
   Step 1: Identify major index constituents
           - ASX: ASX 200 stocks
           - US: S&P 500 stocks
   
   Step 2: Filter by criteria
           - Market cap > $500M (ASX) or $1B (US)
           - Average volume > 500K shares/day
           - Active trading (not suspended)
   
   Step 3: Sector classification
           - Group by GICS sector
           - Aim for 30 stocks per sector
   
   Step 4: Balance representation
           - Include market leaders
           - Add emerging players
           - Ensure liquidity
   
   Step 5: Manual review & adjustment
           - Remove problematic stocks
           - Add important stocks
           - Final curation
   ```

3. **No Dynamic Updates**: Lists are **static** until manually updated

---

## ⚙️ Why Static Lists Instead of Dynamic?

### **Advantages of Hardcoded Lists**:

✅ **Predictability**: Same stocks analyzed consistently  
✅ **Quality Control**: Manually vetted for liquidity and data quality  
✅ **Performance**: No need to query exchanges for stock lists  
✅ **Stability**: Historical analysis requires consistent stock universe  
✅ **LSTM Training**: Neural networks need stable training sets  

### **Disadvantages**:

❌ **Maintenance**: Requires manual updates when stocks delist/merge  
❌ **New Listings**: Doesn't automatically include IPOs or new additions  
❌ **Static Universe**: May miss emerging opportunities  

---

## 🔄 How to Update the Stock Lists

### **Option 1: Manual Update** (Current Method)

Edit the JSON files directly:

```bash
# Edit US stocks
nano models/config/us_sectors.json

# Edit ASX stocks
nano models/config/asx_sectors.json
```

**Example - Add a new stock**:
```json
{
  "sectors": {
    "Technology": {
      "stocks": [
        "AAPL", "MSFT", "GOOGL",
        "NEW_TICKER"  // Add new stock here
      ]
    }
  }
}
```

### **Option 2: Generate from Index** (Future Enhancement)

Create a script to dynamically fetch index constituents:

```python
# GENERATE_STOCK_LIST.py (not yet implemented)
import yfinance as yf

def get_sp500_constituents():
    """Fetch current S&P 500 constituents"""
    # Would fetch from Wikipedia or official source
    pass

def filter_by_criteria(stocks, min_market_cap, min_volume):
    """Apply filtering criteria"""
    pass

def group_by_sector(stocks):
    """Group stocks by GICS sector"""
    pass

def generate_config(stocks):
    """Generate us_sectors.json"""
    pass
```

### **Option 3: Hybrid Approach** (Recommended)

Combine static list with periodic validation:

```python
def validate_stock_list():
    """
    Check if stocks are still valid:
    - Still trading
    - Meet minimum criteria
    - No mergers/delistings
    """
    pass

def suggest_additions():
    """
    Suggest new stocks to add:
    - Recent IPOs
    - Market cap growth
    - Index additions
    """
    pass
```

---

## 📊 Stock Distribution Analysis

### **US Market** (240 stocks):

| Sector | Stocks | % of Total | Avg Market Cap | Examples |
|--------|--------|-----------|----------------|----------|
| Technology | 30 | 12.5% | ~$800B | AAPL, MSFT, NVDA |
| Healthcare | 30 | 12.5% | ~$200B | UNH, JNJ, LLY |
| Financials | 30 | 12.5% | ~$150B | JPM, BAC, V |
| Consumer Disc. | 30 | 12.5% | ~$300B | AMZN, TSLA, HD |
| Comm. Services | 30 | 12.5% | ~$500B | GOOGL, META, NFLX |
| Industrials | 30 | 12.5% | ~$100B | GE, CAT, UNP |
| Energy | 30 | 12.5% | ~$150B | XOM, CVX, COP |
| Consumer Stap. | 30 | 12.5% | ~$120B | WMT, PG, COST |

**Total Market Cap Coverage**: ~$5-8 trillion

### **ASX Market** (240 stocks):

| Sector | Stocks | % of Total | Avg Market Cap | Examples |
|--------|--------|-----------|----------------|----------|
| Financials | 30 | 12.5% | ~A$50B | CBA, WBC, ANZ |
| Materials | 30 | 12.5% | ~A$80B | BHP, RIO, FMG |
| Healthcare | 30 | 12.5% | ~A$30B | CSL, COH, RMD |
| Technology | 30 | 12.5% | ~A$10B | XRO, WTC, CPU |
| Energy | 30 | 12.5% | ~A$15B | ORG, STO, WDS |
| Industrials | 30 | 12.5% | ~A$8B | TCL, QAN, AZJ |
| Consumer Stap. | 30 | 12.5% | ~A$25B | WES, WOW, COL |
| Real Estate | 30 | 12.5% | ~A$12B | GMG, SCG, GPT |

**Total Market Cap Coverage**: ~A$1-2 trillion

---

## 🎯 Typical Stock Characteristics

### **US Stocks**:
- **Market Cap**: $1B - $3T (median ~$50B)
- **Daily Volume**: 1M - 50M shares (median ~5M)
- **Price Range**: $10 - $500 (median ~$100)
- **Beta**: 0.8 - 1.5 (market-relative volatility)

### **ASX Stocks**:
- **Market Cap**: A$500M - A$200B (median ~A$5B)
- **Daily Volume**: 500K - 10M shares (median ~2M)
- **Price Range**: A$0.50 - A$150 (median ~A$10)
- **Beta**: 0.5 - 2.0 (more volatile than US)

---

## 📝 Stock List Maintenance

### **When to Update**:

1. **Delistings**: Stock merges, bankrupt, or delisted → Remove
2. **Index Changes**: S&P 500 or ASX 200 constituent changes → Review
3. **Liquidity Changes**: Stock volume drops below threshold → Consider removal
4. **Market Cap Changes**: Stock grows/shrinks significantly → Review sector placement
5. **Sector Reclassification**: GICS sector changes → Move to new sector

### **Recommended Update Frequency**:
- **Quarterly**: Review for major changes
- **Annually**: Full stock list refresh
- **Ad-hoc**: When notified of delistings or major events

---

## 🚀 Future Enhancements

### **Potential Improvements**:

1. **Dynamic Stock Universe**:
   - Fetch index constituents automatically
   - Update quarterly based on index changes
   - Add stocks that meet criteria automatically

2. **ML-Based Selection**:
   - Use machine learning to identify "scannable" stocks
   - Predict which stocks will have good data quality
   - Optimize for prediction accuracy

3. **Multi-Tier System**:
   - **Tier 1**: Top 50 stocks (daily scan)
   - **Tier 2**: Next 150 stocks (weekly scan)
   - **Tier 3**: Remaining 500+ stocks (monthly scan)

4. **User Customization**:
   - Allow users to add/remove stocks
   - Create custom watchlists
   - Sector-specific scanning

---

## ✅ Summary

### **How Are the 240 Stocks Chosen?**

1. ✅ **Manually Curated Lists**: Hardcoded in JSON config files
2. ✅ **Based on Major Indices**: S&P 500 (US) and ASX 200 (Australia)
3. ✅ **Filtered by Criteria**: Market cap, volume, price, liquidity
4. ✅ **Sector Balanced**: 30 stocks per sector (8 sectors each)
5. ✅ **Static Until Updated**: No automatic additions/removals

### **Key Characteristics**:
- **US**: Large-cap focus ($1B+ market cap), high liquidity (500K+ volume)
- **ASX**: Mid-to-large cap (A$500M+), resource-heavy (Materials sector)

### **Maintenance**:
- ⚠️ **Currently Manual**: Requires editing JSON files
- 🔄 **Future**: Could be automated with index tracking
- 📅 **Recommended**: Review quarterly, refresh annually

### **Why This Approach?**:
- ✅ Ensures data quality and liquidity
- ✅ Provides stable universe for LSTM training
- ✅ Focuses on investable, liquid stocks
- ✅ Predictable and reliable results

---

**Configuration Files**:
- ASX: `models/config/asx_sectors.json`
- US: `models/config/us_sectors.json`

**Last Updated**: November 24, 2025  
**Total Stocks**: 240 (ASX) + 240 (US) = 480 stocks across both markets
