# 🚀 Enhanced Global Stock Market Tracker - Monorepo Setup Guide

## Current Status
- **Frontend**: Located in `/frontend` directory (currently deployed on Netlify)
- **Backend**: Deployed on Railway at `https://web-production-68eaf.up.railway.app`
- **Backend Repository**: Needs to be cloned separately

## Recommended Monorepo Structure

```
enhanced-global-stock-tracker/
├── frontend/                 # Frontend application (Netlify deployment)
│   ├── index.html           # Enhanced Phase 4 landing page
│   ├── *.html               # All UI modules
│   ├── netlify.toml         # Netlify configuration
│   ├── _redirects           # Netlify redirects
│   └── package.json         # Frontend dependencies
│
├── backend/                  # Backend application (Railway deployment)
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   ├── models/              # Data models
│   ├── routes/              # API routes
│   └── services/            # Business logic
│
├── scripts/                  # Utility scripts
│   ├── dev.sh               # Start both frontend and backend
│   ├── deploy-frontend.sh   # Deploy to Netlify
│   └── deploy-backend.sh    # Deploy to Railway
│
├── docs/                     # Project documentation
│   ├── API.md               # API documentation
│   ├── DEPLOYMENT.md        # Deployment guide
│   └── ARCHITECTURE.md      # System architecture
│
├── .github/                  # GitHub Actions workflows
│   └── workflows/
│       ├── frontend.yml     # Frontend CI/CD
│       └── backend.yml      # Backend CI/CD
│
├── README.md                 # Main project README
├── .gitignore               # Git ignore rules
└── package.json             # Root package.json for scripts

```

## Setup Instructions

### 1. Clone Backend Repository

When you have the backend repository name/access:

```bash
# From the project root
git clone https://github.com/davidosland-lab/[BACKEND_REPO_NAME].git backend
```

### 2. Create Development Scripts

Create `scripts/dev.sh`:
```bash
#!/bin/bash
# Start both frontend and backend for development

echo "Starting backend..."
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!

echo "Starting frontend..."
cd ../frontend
python3 -m http.server 3000 &
FRONTEND_PID=$!

echo "Backend running on http://localhost:8000"
echo "Frontend running on http://localhost:3000"
echo "Press Ctrl+C to stop both services"

wait
```

### 3. Update Frontend API Configuration

Create `frontend/config.js`:
```javascript
// API configuration
const API_CONFIG = {
  // Use local backend in development
  BASE_URL: window.location.hostname === 'localhost' 
    ? 'http://localhost:8000/api'
    : 'https://web-production-68eaf.up.railway.app/api',
  
  // Timeout settings
  TIMEOUT: 30000,
  
  // Retry settings
  MAX_RETRIES: 3,
  RETRY_DELAY: 1000
};

// Export for use in other scripts
window.API_CONFIG = API_CONFIG;
```

### 4. Update HTML Files to Use Config

Add to each HTML file's head section:
```html
<script src="/config.js"></script>
```

Update API calls to use `API_CONFIG.BASE_URL`:
```javascript
fetch(`${API_CONFIG.BASE_URL}/endpoint`)
```

## Benefits of Monorepo Structure

1. **Unified Development**: Work on frontend and backend together
2. **Consistent APIs**: Ensure frontend/backend contracts stay in sync
3. **Shared Documentation**: Single source of truth for the project
4. **Simplified Testing**: Test full stack locally
5. **Atomic Changes**: Make coordinated changes across stack
6. **Shared CI/CD**: Coordinate deployments

## Current Deployment Setup

### Frontend (Netlify)
- Auto-deploys from `frontend/` directory
- Static HTML/CSS/JS hosting
- Configured redirects for SPA routing
- API proxy to Railway backend

### Backend (Railway)
- Deploys from backend repository
- FastAPI application
- Connected to database (if applicable)
- Provides REST API endpoints

## Working with Current Structure

While waiting for full monorepo setup, you can:

1. **Frontend Development**: Work in `/frontend` directory
2. **API Testing**: Use the deployed backend at `https://web-production-68eaf.up.railway.app`
3. **Local Testing**: Use Python HTTP server for frontend

## Next Steps

1. **Get Backend Repository Access**: Clone the backend repository
2. **Merge Repositories**: Combine into single monorepo
3. **Update CI/CD**: Configure for monorepo deployments
4. **Document API Contract**: Ensure frontend/backend alignment
5. **Setup Development Environment**: Create unified dev scripts

## Commands for Current Setup

```bash
# Frontend development
cd frontend
python3 -m http.server 3000

# Test API endpoints
curl https://web-production-68eaf.up.railway.app/api/docs

# Deploy frontend (after changes)
git add .
git commit -m "Update frontend"
git push origin main
# Netlify auto-deploys

# Create PR for changes
git checkout -b feature/your-feature
git add .
git commit -m "Your changes"
git push origin feature/your-feature
# Create PR on GitHub
```

## Environment Variables

### Frontend (.env)
```
VITE_API_URL=https://web-production-68eaf.up.railway.app
```

### Backend (.env)
```
DATABASE_URL=your_database_url
SECRET_KEY=your_secret_key
CORS_ORIGINS=["https://your-netlify-site.netlify.app"]
```

---

**Note**: This structure allows for independent deployment while maintaining a unified codebase for development.