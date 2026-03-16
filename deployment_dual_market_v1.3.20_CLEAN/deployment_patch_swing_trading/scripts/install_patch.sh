#!/bin/bash
#
# Swing Trading Backtest - Deployment Patch Installer
# Version: 1.0
# Date: December 6, 2025
#
# This script installs the 5-day swing trading backtest module
# into an existing FinBERT v4.4.4 installation
#

set -e  # Exit on error

echo "========================================="
echo "Swing Trading Backtest - Patch Installer"
echo "========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running from correct directory
if [ ! -d "code" ] || [ ! -d "docs" ] || [ ! -d "scripts" ]; then
    echo -e "${RED}ERROR: Please run this script from the deployment_patch_swing_trading directory${NC}"
    echo "Expected structure:"
    echo "  deployment_patch_swing_trading/"
    echo "  ├── code/"
    echo "  ├── docs/"
    echo "  └── scripts/"
    exit 1
fi

# Ask for FinBERT installation path
echo -e "${YELLOW}Enter the path to your FinBERT v4.4.4 installation:${NC}"
echo "Example: C:/Users/david/AATelS"
read -p "Path: " FINBERT_PATH

# Validate path
if [ ! -d "$FINBERT_PATH" ]; then
    echo -e "${RED}ERROR: Directory not found: $FINBERT_PATH${NC}"
    exit 1
fi

if [ ! -d "$FINBERT_PATH/finbert_v4.4.4" ]; then
    echo -e "${RED}ERROR: FinBERT v4.4.4 not found in: $FINBERT_PATH${NC}"
    exit 1
fi

BACKTESTING_DIR="$FINBERT_PATH/finbert_v4.4.4/models/backtesting"

if [ ! -d "$BACKTESTING_DIR" ]; then
    echo -e "${RED}ERROR: Backtesting directory not found: $BACKTESTING_DIR${NC}"
    exit 1
fi

echo -e "${GREEN}✓ FinBERT v4.4.4 installation found${NC}"
echo ""

# Create backup
BACKUP_DIR="$FINBERT_PATH/backups/swing_trading_patch_$(date +%Y%m%d_%H%M%S)"
echo "Creating backup at: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"

# Backup existing files (if any)
if [ -f "$BACKTESTING_DIR/swing_trader_engine.py" ]; then
    cp "$BACKTESTING_DIR/swing_trader_engine.py" "$BACKUP_DIR/"
    echo "  - Backed up swing_trader_engine.py"
fi

if [ -f "$BACKTESTING_DIR/news_sentiment_fetcher.py" ]; then
    cp "$BACKTESTING_DIR/news_sentiment_fetcher.py" "$BACKUP_DIR/"
    echo "  - Backed up news_sentiment_fetcher.py"
fi

if [ -f "$FINBERT_PATH/finbert_v4.4.4/app_finbert_v4_dev.py" ]; then
    cp "$FINBERT_PATH/finbert_v4.4.4/app_finbert_v4_dev.py" "$BACKUP_DIR/"
    echo "  - Backed up app_finbert_v4_dev.py"
fi

echo -e "${GREEN}✓ Backup created${NC}"
echo ""

# Install code files
echo "Installing code files..."
cp code/swing_trader_engine.py "$BACKTESTING_DIR/"
echo "  - Installed swing_trader_engine.py"

cp code/news_sentiment_fetcher.py "$BACKTESTING_DIR/"
echo "  - Installed news_sentiment_fetcher.py"

cp code/example_swing_backtest.py "$BACKTESTING_DIR/"
echo "  - Installed example_swing_backtest.py"

echo -e "${GREEN}✓ Code files installed${NC}"
echo ""

# Install documentation
echo "Installing documentation..."
DOCS_DIR="$FINBERT_PATH/docs/swing_trading"
mkdir -p "$DOCS_DIR"

cp docs/*.md "$DOCS_DIR/"
echo "  - Installed documentation to $DOCS_DIR"

echo -e "${GREEN}✓ Documentation installed${NC}"
echo ""

# Check for API endpoint
echo -e "${YELLOW}MANUAL STEP REQUIRED: API Endpoint Installation${NC}"
echo ""
echo "The API endpoint needs to be manually added to:"
echo "  $FINBERT_PATH/finbert_v4.4.4/app_finbert_v4_dev.py"
echo ""
echo "Add the following endpoint BEFORE the /api/backtest/optimize endpoint:"
echo "  (See code/swing_endpoint_patch.py for the complete code)"
echo ""
echo "OR use the provided Python script:"
echo "  python scripts/add_api_endpoint.py"
echo ""

# Check dependencies
echo "Checking dependencies..."
python3 -c "import tensorflow" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ TensorFlow available (LSTM will work)${NC}"
else
    echo -e "${YELLOW}⚠ TensorFlow not found (LSTM will use fallback mode)${NC}"
    echo "  To enable LSTM: pip install tensorflow"
fi

python3 -c "import transformers" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Transformers available (FinBERT will work)${NC}"
else
    echo -e "${YELLOW}⚠ Transformers not found (Sentiment will be limited)${NC}"
    echo "  To enable sentiment: pip install transformers"
fi

echo ""
echo "========================================="
echo -e "${GREEN}Installation Complete!${NC}"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Manually add API endpoint (see code/swing_endpoint_patch.py)"
echo "   OR run: python scripts/add_api_endpoint.py"
echo "2. Restart FinBERT v4.4.4 server"
echo "3. Test with: curl -X POST http://localhost:5001/api/backtest/swing ..."
echo ""
echo "Documentation available at:"
echo "  $DOCS_DIR/QUICK_TEST_GUIDE.md"
echo ""
echo "Backup saved at:"
echo "  $BACKUP_DIR"
echo ""
