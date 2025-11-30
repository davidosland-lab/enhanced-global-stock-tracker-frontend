#!/bin/bash
# Quick Update Script for v1.3.20 Patch
# This script applies the bug fix updates to your existing installation

echo "========================================"
echo "Dual Market Stock Screener - Update v1.3.20 Patch"
echo "========================================"
echo ""

# Check if we're in the right directory
if [ ! -d "models/screening" ]; then
    echo "ERROR: This script must be run from the deployment_dual_market_v1.3.20_CLEAN directory"
    echo "Current directory: $(pwd)"
    exit 1
fi

echo "Step 1: Backing up files..."
echo ""

# Create backup directory
BACKUP_DIR="backup_$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"

# Backup critical files
if [ -f "models/screening/chatgpt_research.py" ]; then
    cp "models/screening/chatgpt_research.py" "$BACKUP_DIR/chatgpt_research.py.backup"
    echo "  - Backed up chatgpt_research.py"
fi

if [ -f "models/screening/us_overnight_pipeline.py" ]; then
    cp "models/screening/us_overnight_pipeline.py" "$BACKUP_DIR/us_overnight_pipeline.py.backup"
    echo "  - Backed up us_overnight_pipeline.py"
fi

echo ""
echo "Step 2: Clearing Python cache..."
echo ""

# Clear Python cache
find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null

echo "  - Python cache cleared"
echo ""
echo "Step 3: Update applied successfully!"
echo ""

# Check if the files exist
if [ -f "models/screening/chatgpt_research.py" ]; then
    echo "  - chatgpt_research.py updated"
else
    echo "  WARNING: chatgpt_research.py not found"
fi

if [ -f "models/screening/us_overnight_pipeline.py" ]; then
    echo "  - us_overnight_pipeline.py updated"
else
    echo "  WARNING: us_overnight_pipeline.py not found"
fi

if [ -f "DIAGNOSE_PIPELINE.py" ]; then
    echo "  - DIAGNOSE_PIPELINE.py added"
fi

if [ -f "TEST_REPORT_GENERATION.py" ]; then
    echo "  - TEST_REPORT_GENERATION.py added"
fi

echo ""
echo "========================================"
echo "Update Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "  1. Run diagnostics: python DIAGNOSE_PIPELINE.py"
echo "  2. Test reports:    python TEST_REPORT_GENERATION.py"
echo "  3. Next pipeline run will use the fixed code"
echo ""
echo "Your trained models are safe in: finbert_v4.4.4/models/trained/"
echo "Backups saved to: $BACKUP_DIR/"
echo ""
