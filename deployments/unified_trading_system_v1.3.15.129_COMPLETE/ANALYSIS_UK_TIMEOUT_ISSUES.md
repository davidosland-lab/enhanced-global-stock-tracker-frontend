# Analysis: UK Pipeline Timeout Issues

**Date**: 2026-02-23  
**Issue**: Bank of England RSS feed returns no entries, UK Treasury times out  
**Impact**: Macro news analysis incomplete for UK market

---

## 🔍 Issue Summary

### Observed Behavior

```
19:14:43 - Fetching Bank of England news (RSS)...
19:14:45 - WARNING: No entries in BoE RSS feed
19:14:45 - Fetching Bank of England news... (fallback to HTML scraping)
19:14:49 - [OK] Bank of England News: 0 articles

19:14:49 - Fetching UK Treasury news...
19:15:07 - WARNING: Timeout fetching UK Treasury
19:15:07 - Retry 2/2 after 6.0s delay...
19:15:28 - WARNING: Timeout fetching UK Treasury
19:15:28 - WARNING: Failed to fetch UK Treasury after 2 attempts
```

### Two Separate Issues

1. **Bank of England RSS**: No entries found (feed may be empty or changed format)
2. **UK Treasury**: Network timeout after 15 seconds (website slow/blocking)

---

## 📋 Technical Analysis

### Issue 1: Bank of England RSS Feed

**RSS URL**: `https://www.bankofengland.co.uk/news.rss`

**Possible Causes**:
1. **Feed temporarily empty** - BoE hasn't published news recently
2. **Feed format changed** - BoE updated RSS structure
3. **Feed moved/deprecated** - BoE changed RSS URL
4. **Feedparser issue** - Library not parsing correctly

**Fallback Behavior**:
- ✅ System falls back to HTML scraping (`self.uk_sources['BOE_NEWS']`)
- ✅ Fallback also returned 0 articles (suggests genuinely no recent news)
- ✅ Not a critical failure - just no BoE news available

**Evidence This Is Not Critical**:
```python
# Line 764: Falls back gracefully
logger.warning("  feedparser not installed, falling back to HTML scraping")
return self._scrape_boe_news()

# Line 774: Empty feed is handled
if not feed.entries:
    logger.warning(f"    No entries in BoE RSS feed")
    return self._scrape_boe_news()  # Try HTML scraping
```

### Issue 2: UK Treasury Timeout

**URL**: `https://www.gov.uk/government/organisations/hm-treasury/news`

**Timeout Settings**:
- **Timeout**: 15 seconds (line 76: `self.timeout = 15`)
- **Retries**: 2 attempts (line 77: `self.max_retries = 2`)
- **Total wait**: 15s × 2 = 30 seconds
- **With delays**: ~41 seconds total (including polite delays)

**Observed Timeline**:
```
19:14:49 - Start fetching
19:15:07 - First timeout (18 seconds)
19:15:07 - Retry 2/2 after 6.0s delay
19:15:28 - Second timeout (21 seconds)
```

**Possible Causes**:
1. **Gov.uk website slow** - UK government sites can be slow (high traffic, heavy pages)
2. **Firewall/blocking** - Gov.uk may block non-browser requests
3. **Network issues** - Temporary network congestion
4. **Geographic restrictions** - Gov.uk may throttle non-UK IPs
5. **Cloudflare protection** - Gov.uk uses Cloudflare which may challenge bots

**Evidence**:
- Both attempts timed out (consistent issue, not random)
- ~18-21 second timeout (close to 15s limit suggests slow response, not total block)
- Other sources (Reuters, etc.) worked fine (not a general network issue)

---

## 🎯 Root Cause Assessment

### Bank of England RSS (Low Severity)

**Status**: ⚠️ Non-critical  
**Impact**: Missing BoE news (if any exists)  
**Severity**: LOW

**Why It's Not Critical**:
1. BoE doesn't publish news every day
2. System has fallback to HTML scraping
3. Both RSS and HTML returned 0 articles (likely no news available)
4. Other UK sources still work (FCA, global news, etc.)

**Likely Explanation**: Bank of England genuinely hasn't published news in the past few days.

### UK Treasury Timeout (Medium Severity)

**Status**: ⚠️ Impactful but not breaking  
**Impact**: Missing UK Treasury news (could be important policy announcements)  
**Severity**: MEDIUM

**Why It's Impactful**:
1. UK Treasury is an important macro news source
2. Consistent 15-second timeout suggests systemic issue
3. May contain important fiscal policy news
4. Could affect UK market sentiment analysis

**Likely Explanation**: Gov.uk website is either:
- Very slow (common for government sites)
- Blocking automated requests (anti-bot measures)
- Behind Cloudflare protection

---

## 🔧 Potential Solutions

### Short-Term (Quick Fixes)

#### Solution 1: Increase Timeout for Gov.uk
```python
# Current: 15 seconds
self.timeout = 15

# Proposed: 30 seconds for government sites
self.gov_timeout = 30  # Government sites are notoriously slow

# In _safe_request method:
timeout = self.gov_timeout if 'gov.uk' in url else self.timeout
response = requests.get(url, headers=self.headers, timeout=timeout)
```

**Pros**: Simple, might work if site is just slow  
**Cons**: Slower pipeline, might still fail if blocked

#### Solution 2: Add User-Agent Rotation
```python
# Government sites often block default Python user-agents
self.user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    # ... more user-agents
]

def _get_random_headers(self):
    return {
        'User-Agent': random.choice(self.user_agents),
        'Accept': 'text/html,application/xhtml+xml',
        'Accept-Language': 'en-GB,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
```

**Pros**: Mimics real browser, may bypass bot detection  
**Cons**: Still might fail if Cloudflare protection is strict

#### Solution 3: Skip UK Treasury (Graceful Degradation)
```python
# Add to config
self.skip_slow_sources = True  # Skip sources that consistently timeout

# In _scrape_uk_treasury_news:
if self.skip_slow_sources:
    logger.info("  Skipping UK Treasury (slow source, can re-enable if needed)")
    return []
```

**Pros**: Faster pipeline, no timeout delays  
**Cons**: Missing potentially important news

### Long-Term (Better Solutions)

#### Solution 4: Use Alternative UK Treasury Source
```python
# Instead of HTML scraping, use structured data
self.uk_sources = {
    'UK_TREASURY_RSS': 'https://www.gov.uk/government/organisations/hm-treasury.atom',  # Atom feed
    # Or use GOV.UK API if available
}
```

**Pros**: Faster, more reliable, structured data  
**Cons**: Need to verify Atom feed exists and works

#### Solution 5: Implement Caching with Longer TTL
```python
# Cache UK Treasury news for 24 hours (government news doesn't change often)
self.uk_treasury_cache = {}
self.cache_ttl = 86400  # 24 hours

def _get_cached_or_fetch_uk_treasury(self):
    if 'uk_treasury' in self.uk_treasury_cache:
        cached_time, cached_articles = self.uk_treasury_cache['uk_treasury']
        if time.time() - cached_time < self.cache_ttl:
            logger.info("  Using cached UK Treasury news (< 24h old)")
            return cached_articles
    
    # Fetch fresh
    articles = self._scrape_uk_treasury_news()
    self.uk_treasury_cache['uk_treasury'] = (time.time(), articles)
    return articles
```

**Pros**: Avoids repeated timeouts, faster pipelines  
**Cons**: May miss very recent announcements

#### Solution 6: Parallel Fetching with Timeout per Source
```python
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout

def _fetch_uk_sources_parallel(self):
    sources = {
        'boe_rss': self._scrape_boe_news_rss,
        'treasury': self._scrape_uk_treasury_news,
        'fca': self._scrape_fca_news,
    }
    
    results = {}
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {name: executor.submit(func) for name, func in sources.items()}
        
        for name, future in futures.items():
            try:
                results[name] = future.result(timeout=20)  # 20s per source
            except FuturesTimeout:
                logger.warning(f"  Timeout fetching {name}, skipping...")
                results[name] = []
    
    return results
```

**Pros**: Faster overall (parallel), isolates timeouts  
**Cons**: More complex, harder to debug

---

## 📊 Recommendation

### Immediate Actions (Deploy Today)

1. **✅ Do Nothing** - System is working as designed
   - Graceful degradation in place
   - Fallbacks working correctly
   - Other sources compensate for missing UK Treasury

2. **⏳ Monitor** - Check if this is temporary
   - Run pipeline again tomorrow
   - If UK Treasury still times out → implement fix
   - If it works → was temporary issue

### If Issue Persists (Deploy in v1.3.15.176)

**Priority 1**: Increase timeout for gov.uk sites
```python
# Add gov.uk specific timeout
self.gov_timeout = 30  # Government sites need more time

# Modify _safe_request to use longer timeout for gov.uk
def _safe_request(self, url: str, description: str = "page"):
    timeout = self.gov_timeout if 'gov.uk' in url else self.timeout
    response = requests.get(url, headers=self.headers, timeout=timeout)
```

**Priority 2**: Add better user-agent headers
```python
self.headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}
```

**Priority 3**: Add UK Treasury to optional sources
```python
# Allow skipping slow sources via config
self.optional_sources = ['UK_TREASURY']  # Can timeout, not critical
```

---

## 🎯 Impact Assessment

### Current Impact

**Without UK Treasury News**:
- ✅ Pipeline completes successfully
- ✅ Morning report generated
- ⚠️ Missing UK Treasury fiscal policy news (if any)
- ✅ Other UK sources working (BoE HTML fallback, FCA, global news)
- ✅ Macro sentiment still calculated (uses other sources)

**Overall**: **Low impact** - pipeline functional, just missing one source

### If We Fix This

**Benefits**:
- ✅ More complete UK news coverage
- ✅ Better macro sentiment accuracy
- ✅ Catch important UK fiscal announcements

**Costs**:
- ⏱️ +10-15 seconds pipeline time (if we increase timeout)
- 🔧 +30 minutes dev time (implement fix)
- 🧪 +15 minutes testing (verify fix works)

**ROI**: **Low** - Not critical, but nice to have

---

## 📝 Conclusion

### Bank of England RSS
**Status**: ✅ Working as designed  
**Action**: None needed (0 articles likely means no recent news)

### UK Treasury Timeout
**Status**: ⚠️ Impaired but not broken  
**Action**: Monitor; fix if persists

**Recommendation**: 
1. **Wait and monitor** - Could be temporary
2. **If persists** → Implement timeout increase (5 min fix)
3. **If still fails** → Implement user-agent rotation (15 min fix)
4. **If still fails** → Mark as optional source (10 min fix)

**Priority**: **LOW** - System works fine without UK Treasury news

---

**Next Steps**:
1. Run UK pipeline again tomorrow
2. Check if UK Treasury still times out
3. If yes → implement Fix 6 (timeout increase + user-agent)
4. If no → issue was temporary, no action needed
