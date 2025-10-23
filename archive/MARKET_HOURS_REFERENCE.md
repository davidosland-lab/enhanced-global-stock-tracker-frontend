# Global Market Hours Reference Guide
## All Times in Australian Eastern Time (AEST/AEDT)

## 📊 Three Primary Market Sessions for Tracking

### 1. 🇦🇺 **Australian Market Session**
- **ASX (Australian Securities Exchange)**
  - **Opening:** 10:00 AEST
  - **Closing:** 16:00 AEST
  - **Duration:** 6 hours
  - **Key Indices:** ^AXJO (ASX 200), ^AORD (All Ordinaries)

### 2. 🇬🇧 **European Market Session**
- **Major European Exchanges**
  - **Opening:** 18:00 AEST (Standard) / 19:00 AEDT (Summer)
  - **Closing:** 02:30 AEST (Standard) / 03:30 AEDT (Summer)
  - **Duration:** 8.5 hours
  - **Key Markets:**
    - London Stock Exchange (LSE) - FTSE 100
    - Frankfurt (DAX)
    - Paris (CAC 40)
    - Zurich (SMI)
    - Madrid (IBEX)
    - Stockholm, Copenhagen

### 3. 🇺🇸 **US Market Session**
- **NYSE & NASDAQ**
  - **Opening:** 00:30 AEST (Standard) / 23:30 AEDT (Daylight Saving)
  - **Closing:** 07:00 AEST (Standard) / 06:00 AEDT (Daylight Saving)
  - **Duration:** 6.5 hours
  - **Key Indices:** S&P 500, Dow Jones, NASDAQ

## 🌏 Additional Asian Markets (For Reference)

### Japanese Market
- **Tokyo Stock Exchange**
  - **Opening:** 10:00 AEST
  - **Closing:** 16:00 AEST (with lunch break 12:30-13:30)
  - **Key Index:** Nikkei 225

### Chinese Markets
- **Shanghai Stock Exchange**
  - **Opening:** 11:30 AEST
  - **Closing:** 18:00 AEST
  - **Key Index:** Shanghai Composite

### Hong Kong Market
- **Hong Kong Stock Exchange**
  - **Opening:** 11:30 AEST
  - **Closing:** 17:00 AEST
  - **Key Index:** Hang Seng

### Korean Market
- **Korea Exchange**
  - **Opening:** 11:30 AEST
  - **Closing:** 17:00 AEST
  - **Key Index:** KOSPI

### Indian Market
- **BSE/NSE**
  - **Opening:** 13:45 AEST
  - **Closing:** 20:00 AEST
  - **Key Index:** SENSEX, NIFTY 50

## 📅 Market Overlap Periods (AEST)

### Key Trading Overlaps:
1. **Australia + Asia:** 11:30 - 16:00 AEST
   - High liquidity in Asian-Pacific region
   - ASX, Nikkei, Shanghai, Hong Kong all active

2. **Europe + US:** 00:30 - 02:30 AEST
   - Most liquid period globally
   - London and New York both open

3. **Asia + Europe:** 18:00 - 18:00 AEST
   - Brief overlap with late Asian and early European trading

## 🕐 24-Hour Market Flow (AEST)

```
00:00 ├─ US Market Active (until 07:00)
      │
07:00 ├─ US Market Closes
      │
10:00 ├─ Australian Market Opens
      ├─ Japanese Market Opens
      │
11:30 ├─ Chinese/HK Markets Open
      │
16:00 ├─ Australian Market Closes
      ├─ Japanese Market Closes
      │
18:00 ├─ European Markets Open
      ├─ Chinese Market Closes
      │
20:00 ├─ Indian Market Closes
      │
23:30 ├─ US Market Opens (during AEDT)
      │
00:30 ├─ US Market Opens (during AEST)
      │
02:30 ├─ European Markets Close
      │
```

## ⚠️ Important Considerations

### Daylight Saving Time Impacts:
- **Australia:** October - April (AEDT = AEST + 1 hour)
- **US:** March - November (affects market open/close by 1 hour)
- **Europe:** March - October (affects market open/close by 1 hour)

### Holiday Schedules:
- Each market has different public holidays
- US markets closed: Thanksgiving, Independence Day, etc.
- Australian markets closed: Australia Day, ANZAC Day, etc.
- European markets: Various national holidays

### Pre-Market and After-Hours:
- **US Pre-Market:** 20:00 - 00:30 AEST
- **US After-Hours:** 07:00 - 11:00 AEST
- Limited liquidity and wider spreads

## 📊 Implementation in Chart

The chart visualization shows these market periods as colored backgrounds:
- **Amber/Yellow:** Australian Market Hours (10:00-16:00)
- **Blue:** European Market Hours (18:00-02:30)
- **Green:** US Market Hours (00:30-07:00)
- **Purple:** Asian Market Hours (10:00-18:00)

## 🎯 Trading Strategy Implications

### Best Times for Different Markets:
1. **ASX Trading:** 10:00-16:00 AEST - Full liquidity
2. **US Stock Trading from Australia:** 00:30-07:00 AEST - Live market
3. **European Stock Trading:** 18:00-02:30 AEST - Live market
4. **Global FX Trading:** 00:30-02:30 AEST - Maximum liquidity (London/NY overlap)

### Quietest Periods:
- 07:00-10:00 AEST - Between US close and ASX open
- 16:00-18:00 AEST - Between ASX close and Europe open

## 💻 Using the Tracker

The new tracker (`global_indices_tracker_au_markets.html`) displays:
1. **Live Market Status:** Shows which markets are currently open
2. **Current AEST Time:** Always visible for reference
3. **Market Period Overlays:** Visual representation on charts
4. **Auto-Detection:** Automatically determines market status based on current time

---

**Note:** This reference is based on standard trading hours and doesn't account for half-days, early closes, or special trading sessions. Always verify current market hours, especially around daylight saving transitions.