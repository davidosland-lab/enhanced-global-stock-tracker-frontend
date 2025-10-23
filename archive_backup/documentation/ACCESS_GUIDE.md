# 🌐 Stock Tracker Access Guide

## 📍 Current Environment: E2B Sandbox

Since you're accessing the Stock Tracker from a sandbox environment, you need to use the sandbox URLs instead of localhost.

## 🔗 Direct Access URLs

### Main Services:
- **Main Dashboard**: https://8000-i2ch499gc6d7qpm0yvxy4-6532622b.e2b.dev
- **ML Backend API**: https://8002-i2ch499gc6d7qpm0yvxy4-6532622b.e2b.dev
- **Web Scraper API**: https://8006-i2ch499gc6d7qpm0yvxy4-6532622b.e2b.dev

### Test the Web Scraper Directly:
1. **Health Check**: https://8006-i2ch499gc6d7qpm0yvxy4-6532622b.e2b.dev/health
2. **Sources List**: https://8006-i2ch499gc6d7qpm0yvxy4-6532622b.e2b.dev/sources

### HTML Pages:
- **Universal Sentiment Scraper**: https://8000-i2ch499gc6d7qpm0yvxy4-6532622b.e2b.dev/sentiment_scraper_universal.html
- **Prediction Center**: https://8000-i2ch499gc6d7qpm0yvxy4-6532622b.e2b.dev/prediction_center.html

## ✅ Service Status

All services are currently **RUNNING**:
- ✅ Main Backend (Port 8000)
- ✅ ML Backend (Port 8002) 
- ✅ Web Scraper (Port 8006)

## 🧪 Test Web Scraper via cURL

```bash
# Test from command line (works internally)
curl -X POST https://8006-i2ch499gc6d7qpm0yvxy4-6532622b.e2b.dev/scrape \
  -H "Content-Type: application/json" \
  -d '{"symbol":"AAPL","sources":["yahoo"]}'
```

## 🔧 Why "localhost" Doesn't Work

When running in a sandbox/cloud environment:
- `localhost` refers to YOUR local machine, not the sandbox
- The services are running in the sandbox container
- You must use the sandbox URLs to access them from your browser

## 💡 Solution for Your HTML Files

I've created `sentiment_scraper_universal.html` which:
1. Auto-detects if you're in sandbox or local environment
2. Uses the correct URLs automatically
3. Shows the configuration being used
4. Works in both environments

## 🚀 Quick Test

1. Open this URL in your browser:
   https://8000-i2ch499gc6d7qpm0yvxy4-6532622b.e2b.dev/sentiment_scraper_universal.html

2. You should see:
   - "Sandbox/Cloud Environment" in the configuration
   - Web Scraper status as "Online"
   - Correct API URL displayed

3. Try scraping:
   - Enter a symbol (e.g., AAPL)
   - Select sources
   - Click "Scrape & Analyze"

## 📝 For Windows Deployment

When you deploy this on your local Windows machine:
- All the `localhost` URLs will work correctly
- The HTML files will automatically detect local environment
- No changes needed to the code

## 🎯 Current Working Services

| Service | Local URL | Sandbox URL | Status |
|---------|-----------|-------------|--------|
| Main Backend | http://localhost:8000 | https://8000-i2ch499gc6d7qpm0yvxy4-6532622b.e2b.dev | ✅ Running |
| ML Backend | http://localhost:8002 | https://8002-i2ch499gc6d7qpm0yvxy4-6532622b.e2b.dev | ✅ Running |
| Web Scraper | http://localhost:8006 | https://8006-i2ch499gc6d7qpm0yvxy4-6532622b.e2b.dev | ✅ Running |

---
**Note**: The web scraper IS working - it's just that browser security (CORS) prevents `localhost` URLs from working when you're accessing from outside the sandbox. Use the sandbox URLs provided above!