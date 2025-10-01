#!/bin/bash

echo "================================================"
echo "DEPLOYMENT UPDATE SCRIPT"
echo "================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check current git status
echo -e "${YELLOW}📊 Checking Git Status...${NC}"
git status --short
echo ""

# Count unpushed commits
UNPUSHED=$(git rev-list @{u}.. --count 2>/dev/null || echo "unknown")
if [ "$UNPUSHED" != "0" ] && [ "$UNPUSHED" != "unknown" ]; then
    echo -e "${RED}⚠️  You have $UNPUSHED unpushed commits${NC}"
    git log --oneline @{u}.. | head -5
    echo ""
fi

# Check GitHub authentication
echo -e "${YELLOW}🔐 Checking GitHub Authentication...${NC}"
if git ls-remote &>/dev/null; then
    echo -e "${GREEN}✅ GitHub authentication working${NC}"
else
    echo -e "${RED}❌ GitHub authentication failed${NC}"
    echo "Please configure GitHub token:"
    echo "  git remote set-url origin https://<token>@github.com/davidosland-lab/enhanced-global-stock-tracker-frontend.git"
    exit 1
fi
echo ""

# Check for deployment configs
echo -e "${YELLOW}📋 Checking Deployment Configurations...${NC}"

if [ -f "netlify.toml" ]; then
    echo -e "${GREEN}✅ Netlify config found${NC}"
else
    echo -e "${RED}❌ Netlify config missing${NC}"
fi

if [ -f "render_backend/render.yaml" ]; then
    echo -e "${GREEN}✅ Render config found${NC}"
else
    echo -e "${RED}❌ Render config missing${NC}"
fi
echo ""

# Prompt for deployment
echo -e "${YELLOW}Would you like to push changes to GitHub? (y/n)${NC}"
read -r response

if [ "$response" = "y" ]; then
    echo -e "${YELLOW}Pushing to GitHub...${NC}"
    git push origin main
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Successfully pushed to GitHub${NC}"
        echo ""
        echo -e "${GREEN}🚀 Deployment Status:${NC}"
        echo "  - Netlify will auto-deploy frontend in ~2-3 minutes"
        echo "  - Render will auto-deploy backend in ~5-10 minutes"
        echo ""
        echo -e "${YELLOW}📌 Production URLs:${NC}"
        echo "  Frontend: https://enhanced-global-stock-tracker-frontend.netlify.app/"
        echo "  Backend: https://enhanced-global-stock-tracker-backend.onrender.com/"
        echo ""
        echo -e "${YELLOW}📊 Monitor deployment:${NC}"
        echo "  Netlify: https://app.netlify.com/"
        echo "  Render: https://dashboard.render.com/"
    else
        echo -e "${RED}❌ Push failed. Please check your authentication.${NC}"
        exit 1
    fi
else
    echo "Deployment cancelled."
fi

echo ""
echo "================================================"
echo "For manual deployment instructions, see DEPLOYMENT_STATUS.md"
echo "================================================"