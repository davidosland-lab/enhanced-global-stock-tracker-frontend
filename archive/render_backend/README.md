# Market Indices Backend for Render.com

This is an optimized backend for deployment on Render.com that provides real-time market data via Yahoo Finance.

## Quick Deploy to Render

1. **Fork or push this folder to a GitHub repository**

2. **Go to [Render.com](https://render.com)** and sign up/login

3. **Create New Web Service**:
   - Connect your GitHub account
   - Select your repository
   - Choose the branch (main)
   - **Root Directory**: Set to `render_backend` (if in a subfolder)
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

4. **Deploy** and get your URL like: `https://your-app.onrender.com`

5. **Update your frontend** `config.js`:
   ```javascript
   BACKEND_URL: 'https://your-app.onrender.com'
   ```

## Endpoints

- `GET /` - API info
- `GET /health` - Health check
- `GET /api/stock/{symbol}` - Get stock/index data
- `GET /api/indices` - List of supported indices

## Testing

Test your deployment:
```bash
curl https://your-app.onrender.com/health
curl https://your-app.onrender.com/api/stock/^N225?period=1d&interval=5m
```

## Environment Variables (Optional)

- `ENVIRONMENT` - Set to "production" or "development"
- `PORT` - Port number (Render sets this automatically)

## Notes

- Free tier sleeps after 15 minutes of inactivity
- First request after sleep takes ~30 seconds to wake up
- Upgrade to paid tier for always-on service