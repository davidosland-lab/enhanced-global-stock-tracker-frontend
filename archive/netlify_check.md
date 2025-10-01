# Netlify Deployment Checklist

## Current Status
- Main site: **NOT FOUND** (entire site is down)
- Files in GitHub: ✅ All files are committed and pushed
- Local test server: ✅ Working at port 8081

## Required Netlify Settings

### 1. Site Settings
- **Site name**: enhanced-global-stock-tracker-frontend
- **Repository**: github.com/davidosland-lab/enhanced-global-stock-tracker-frontend

### 2. Build & Deploy Settings
- **Production branch**: `main` (NOT master)
- **Branch deploys**: All branches
- **Build command**: (leave empty)
- **Publish directory**: `.` or `/`
- **Functions directory**: (leave empty)

### 3. Files that MUST be deployed
- index.html ✅
- indices_ver_105.html ✅
- config.js ✅
- netlify.toml ✅
- All other HTML files ✅

## How to Fix in Netlify Dashboard

1. Go to: https://app.netlify.com
2. Select your site
3. Go to "Site configuration" > "Build & deploy" > "Continuous deployment"
4. Check "Production branch" is set to `main`
5. Check "Build settings":
   - Base directory: (leave empty)
   - Build command: (leave empty)
   - Publish directory: `.`
6. Go to "Deploys" tab
7. Click "Trigger deploy" > "Clear cache and deploy site"

## If Still Not Working

1. Unlink the repository:
   - Site configuration > Build & deploy > Continuous deployment
   - Click "Unlink this repository"

2. Re-link the repository:
   - Click "Link repository" 
   - Choose GitHub
   - Select "enhanced-global-stock-tracker-frontend"
   - Set branch to `main`
   - Leave build settings empty

## Manual Deploy Option

If auto-deploy isn't working, you can manually deploy:
1. Download the repository as ZIP from GitHub
2. Drag and drop the folder to Netlify dashboard