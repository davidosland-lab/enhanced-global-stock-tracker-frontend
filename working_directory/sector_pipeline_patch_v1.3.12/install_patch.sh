#!/bin/bash
# ============================================================================
# SECTOR-BASED PIPELINE PATCH v1.3.12 - INSTALLATION SCRIPT (Linux/Mac)
# ============================================================================
# 
# This script installs the sector-based pipeline update for AU/US/UK markets
# 
# Installation:
#   1. Extract this ZIP to a temporary folder
#   2. Run: chmod +x install_patch.sh
#   3. Run: ./install_patch.sh
#   4. Follow the prompts
#
# Date: January 3, 2026
# Version: 1.3.12
# ============================================================================

echo ""
echo "============================================================================"
echo "SECTOR-BASED PIPELINE PATCH v1.3.12 - INSTALLATION"
echo "============================================================================"
echo ""
echo "This patch adds sector-based scanning to all three market pipelines:"
echo "  - AU Pipeline: 240 ASX stocks (8 sectors x 30 stocks)"
echo "  - US Pipeline: 240 US stocks (8 sectors x 30 stocks)"
echo "  - UK Pipeline: 240 LSE stocks (8 sectors x 30 stocks)"
echo ""
echo "Total Coverage: 720 stocks across all markets"
echo ""
echo "============================================================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 not found. Please install Python 3.8+ first."
    echo ""
    echo "Download from: https://www.python.org/downloads/"
    exit 1
fi

echo "[OK] Python found"
python3 --version
echo ""

# Ask for installation directory
DEFAULT_DIR="$(cd .. && pwd)/phase3_intraday_deployment"
echo "Where is your phase3_intraday_deployment directory?"
echo ""
echo "Default: $DEFAULT_DIR"
echo ""
read -p "Enter path (or press Enter for default): " INSTALL_DIR

if [ -z "$INSTALL_DIR" ]; then
    INSTALL_DIR="$DEFAULT_DIR"
fi

echo ""
echo "Installation Directory: $INSTALL_DIR"
echo ""

# Check if directory exists
if [ ! -d "$INSTALL_DIR" ]; then
    echo "[WARNING] Directory does not exist: $INSTALL_DIR"
    echo ""
    read -p "Create it? (y/n): " CREATE
    if [ "$CREATE" = "y" ] || [ "$CREATE" = "Y" ]; then
        mkdir -p "$INSTALL_DIR"
        if [ $? -ne 0 ]; then
            echo "[ERROR] Failed to create directory"
            exit 1
        fi
        echo "[OK] Directory created"
    else
        echo "[CANCELLED] Installation aborted"
        exit 0
    fi
fi

echo ""
echo "============================================================================"
echo "INSTALLATION STEPS"
echo "============================================================================"
echo ""

# Step 1: Create directories
echo "[1/6] Creating directories..."
mkdir -p "$INSTALL_DIR/config"
mkdir -p "$INSTALL_DIR/models"
mkdir -p "$INSTALL_DIR/docs"
echo "[OK] Directories ready"
echo ""

# Step 2: Backup existing files
echo "[2/6] Backing up existing files..."
BACKUP_DIR="$INSTALL_DIR/backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

if [ -f "$INSTALL_DIR/run_au_pipeline.py" ]; then
    cp "$INSTALL_DIR/run_au_pipeline.py" "$BACKUP_DIR/"
    echo "  - Backed up: run_au_pipeline.py"
fi
if [ -f "$INSTALL_DIR/run_us_pipeline.py" ]; then
    cp "$INSTALL_DIR/run_us_pipeline.py" "$BACKUP_DIR/"
    echo "  - Backed up: run_us_pipeline.py"
fi
if [ -f "$INSTALL_DIR/run_uk_pipeline.py" ]; then
    cp "$INSTALL_DIR/run_uk_pipeline.py" "$BACKUP_DIR/"
    echo "  - Backed up: run_uk_pipeline.py"
fi

echo "[OK] Backup created: $BACKUP_DIR"
echo ""

# Step 3: Copy configuration files
echo "[3/6] Installing configuration files..."
cp "config/asx_sectors.json" "$INSTALL_DIR/config/"
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to copy asx_sectors.json"
    exit 1
fi
echo "  - Installed: config/asx_sectors.json (240 ASX stocks)"

cp "config/us_sectors.json" "$INSTALL_DIR/config/"
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to copy us_sectors.json"
    exit 1
fi
echo "  - Installed: config/us_sectors.json (240 US stocks)"

cp "config/uk_sectors.json" "$INSTALL_DIR/config/"
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to copy uk_sectors.json"
    exit 1
fi
echo "  - Installed: config/uk_sectors.json (240 LSE stocks)"

cp "config/screening_config.json" "$INSTALL_DIR/config/"
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to copy screening_config.json"
    exit 1
fi
echo "  - Installed: config/screening_config.json"

echo "[OK] Configuration files installed"
echo ""

# Step 4: Copy model files
echo "[4/6] Installing model files..."
cp "models/sector_stock_scanner.py" "$INSTALL_DIR/models/"
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to copy sector_stock_scanner.py"
    exit 1
fi
echo "  - Installed: models/sector_stock_scanner.py"
echo "[OK] Model files installed"
echo ""

# Step 5: Copy pipeline scripts
echo "[5/6] Installing pipeline scripts..."
cp "scripts/run_au_pipeline.py" "$INSTALL_DIR/"
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to copy run_au_pipeline.py"
    exit 1
fi
echo "  - Installed: run_au_pipeline.py (v1.3.12)"

cp "scripts/run_us_pipeline.py" "$INSTALL_DIR/"
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to copy run_us_pipeline.py"
    exit 1
fi
echo "  - Installed: run_us_pipeline.py (v1.3.12)"

cp "scripts/run_uk_pipeline.py" "$INSTALL_DIR/"
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to copy run_uk_pipeline.py"
    exit 1
fi
echo "  - Installed: run_uk_pipeline.py (v1.3.12)"

# Make scripts executable
chmod +x "$INSTALL_DIR/run_au_pipeline.py"
chmod +x "$INSTALL_DIR/run_us_pipeline.py"
chmod +x "$INSTALL_DIR/run_uk_pipeline.py"

echo "[OK] Pipeline scripts installed"
echo ""

# Step 6: Copy documentation
echo "[6/6] Installing documentation..."
cp docs/*.md "$INSTALL_DIR/docs/" 2>/dev/null
echo "  - Installed: Documentation files"
echo "[OK] Documentation installed"
echo ""

echo "============================================================================"
echo "INSTALLATION COMPLETE!"
echo "============================================================================"
echo ""
echo "Patch v1.3.12 has been successfully installed."
echo ""
echo "NEW FEATURES:"
echo "  - Full sector scanning: 240 stocks per market"
echo "  - 8 sectors x 30 stocks per sector"
echo "  - Total coverage: 720 stocks (AU + US + UK)"
echo "  - ML ensemble prediction with 5-layer filtering"
echo ""
echo "NEW COMMANDS:"
echo "  # Full sector scan (recommended)"
echo "  python3 run_au_pipeline.py --full-scan --capital 100000"
echo "  python3 run_us_pipeline.py --full-scan --capital 100000"
echo "  python3 run_uk_pipeline.py --full-scan --capital 100000"
echo ""
echo "LEGACY COMMANDS (still supported):"
echo "  # Preset mode"
echo "  python3 run_au_pipeline.py --preset \"ASX Blue Chips\" --capital 100000"
echo ""
echo "NEXT STEPS:"
echo "  1. Review documentation in: $INSTALL_DIR/docs/"
echo "  2. Test the pipelines with: --full-scan --ignore-market-hours"
echo "  3. Update your scripts if needed"
echo ""
echo "BACKUP LOCATION:"
echo "  $BACKUP_DIR"
echo ""
echo "============================================================================"
echo ""
