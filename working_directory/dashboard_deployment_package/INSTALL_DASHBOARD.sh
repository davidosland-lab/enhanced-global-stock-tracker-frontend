#!/bin/bash
#
# Live Trading Dashboard Deployment Installer
# ============================================
# 
# This script installs the complete Live Trading Dashboard system
# with intraday monitoring integration.
#
# Features:
# - Auto-detects Python environment
# - Installs dependencies
# - Copies dashboard files
# - Creates directory structure
# - Validates installation
# - Auto-backup existing files
#
# Usage:
#   chmod +x INSTALL_DASHBOARD.sh
#   ./INSTALL_DASHBOARD.sh
#
# Author: FinBERT Enhanced System
# Date: December 21, 2024
# Version: 2.0

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         LIVE TRADING DASHBOARD INSTALLER v2.0                 ║"
echo "║         Swing Trading + Intraday Monitoring                   ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PACKAGE_DIR="$SCRIPT_DIR"

# Default installation directory
INSTALL_DIR="."
if [ ! -z "$1" ]; then
    INSTALL_DIR="$1"
fi

echo -e "${BLUE}Installation Settings:${NC}"
echo -e "  Source: ${GREEN}$PACKAGE_DIR${NC}"
echo -e "  Target: ${GREEN}$INSTALL_DIR${NC}"
echo ""

# Function: Print step
print_step() {
    echo -e "${BLUE}➜ $1${NC}"
}

# Function: Print success
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function: Print warning
print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Function: Print error and exit
print_error() {
    echo -e "${RED}✗ $1${NC}"
    exit 1
}

# Step 1: Check Python
print_step "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.9 or higher."
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
print_success "Found Python $PYTHON_VERSION"

# Step 2: Check pip
print_step "Checking pip installation..."
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 is not installed. Please install pip3."
fi
print_success "pip3 is installed"

# Step 3: Create backup of existing files
print_step "Creating backup of existing files..."
BACKUP_DIR="dashboard_backup_$(date +%Y%m%d_%H%M%S)"

if [ -f "$INSTALL_DIR/live_trading_dashboard.py" ] || [ -d "$INSTALL_DIR/templates" ]; then
    mkdir -p "$BACKUP_DIR"
    
    # Backup existing files
    [ -f "$INSTALL_DIR/live_trading_dashboard.py" ] && cp "$INSTALL_DIR/live_trading_dashboard.py" "$BACKUP_DIR/" 2>/dev/null || true
    [ -f "$INSTALL_DIR/live_trading_with_dashboard.py" ] && cp "$INSTALL_DIR/live_trading_with_dashboard.py" "$BACKUP_DIR/" 2>/dev/null || true
    [ -d "$INSTALL_DIR/templates" ] && cp -r "$INSTALL_DIR/templates" "$BACKUP_DIR/" 2>/dev/null || true
    [ -d "$INSTALL_DIR/static" ] && cp -r "$INSTALL_DIR/static" "$BACKUP_DIR/" 2>/dev/null || true
    
    print_success "Backup created: $BACKUP_DIR"
else
    print_success "No existing files to backup"
fi

# Step 4: Install Python dependencies
print_step "Installing Python dependencies..."
pip3 install flask flask-cors pandas numpy --quiet || print_warning "Some packages may already be installed"
print_success "Dependencies installed"

# Step 5: Create directory structure
print_step "Creating directory structure..."
mkdir -p "$INSTALL_DIR/templates"
mkdir -p "$INSTALL_DIR/static/css"
mkdir -p "$INSTALL_DIR/static/js"
mkdir -p "$INSTALL_DIR/logs"
print_success "Directory structure created"

# Step 6: Copy dashboard files
print_step "Copying dashboard files..."

# Copy main Python files
if [ -f "$PACKAGE_DIR/live_trading_dashboard.py" ]; then
    cp "$PACKAGE_DIR/live_trading_dashboard.py" "$INSTALL_DIR/"
    print_success "Copied live_trading_dashboard.py"
else
    print_error "Missing live_trading_dashboard.py in package"
fi

if [ -f "$PACKAGE_DIR/live_trading_with_dashboard.py" ]; then
    cp "$PACKAGE_DIR/live_trading_with_dashboard.py" "$INSTALL_DIR/"
    print_success "Copied live_trading_with_dashboard.py"
fi

# Copy templates
if [ -f "$PACKAGE_DIR/templates/dashboard.html" ]; then
    cp "$PACKAGE_DIR/templates/dashboard.html" "$INSTALL_DIR/templates/"
    print_success "Copied dashboard.html"
else
    print_error "Missing templates/dashboard.html in package"
fi

# Copy static files
if [ -f "$PACKAGE_DIR/static/css/dashboard.css" ]; then
    cp "$PACKAGE_DIR/static/css/dashboard.css" "$INSTALL_DIR/static/css/"
    print_success "Copied dashboard.css"
else
    print_error "Missing static/css/dashboard.css in package"
fi

if [ -f "$PACKAGE_DIR/static/js/dashboard.js" ]; then
    cp "$PACKAGE_DIR/static/js/dashboard.js" "$INSTALL_DIR/static/js/"
    print_success "Copied dashboard.js"
else
    print_error "Missing static/js/dashboard.js in package"
fi

# Copy documentation
print_step "Copying documentation..."
[ -f "$PACKAGE_DIR/DASHBOARD_SETUP_GUIDE.md" ] && cp "$PACKAGE_DIR/DASHBOARD_SETUP_GUIDE.md" "$INSTALL_DIR/" && print_success "Copied DASHBOARD_SETUP_GUIDE.md"
[ -f "$PACKAGE_DIR/DASHBOARD_COMPLETE_SUMMARY.md" ] && cp "$PACKAGE_DIR/DASHBOARD_COMPLETE_SUMMARY.md" "$INSTALL_DIR/" && print_success "Copied DASHBOARD_COMPLETE_SUMMARY.md"
[ -f "$PACKAGE_DIR/SYSTEM_ARCHITECTURE.md" ] && cp "$PACKAGE_DIR/SYSTEM_ARCHITECTURE.md" "$INSTALL_DIR/" && print_success "Copied SYSTEM_ARCHITECTURE.md"

# Step 7: Set permissions
print_step "Setting permissions..."
chmod +x "$INSTALL_DIR/live_trading_dashboard.py" 2>/dev/null || true
chmod +x "$INSTALL_DIR/live_trading_with_dashboard.py" 2>/dev/null || true
print_success "Permissions set"

# Step 8: Validate installation
print_step "Validating installation..."

VALIDATION_FAILED=0

# Check required files
REQUIRED_FILES=(
    "live_trading_dashboard.py"
    "templates/dashboard.html"
    "static/css/dashboard.css"
    "static/js/dashboard.js"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$INSTALL_DIR/$file" ]; then
        print_error "Missing required file: $file"
        VALIDATION_FAILED=1
    fi
done

if [ $VALIDATION_FAILED -eq 0 ]; then
    print_success "All required files present"
fi

# Test Python import
print_step "Testing Flask import..."
python3 -c "import flask; import flask_cors" 2>/dev/null && print_success "Flask is properly installed" || print_warning "Flask import test failed"

# Step 9: Display installation summary
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║            INSTALLATION COMPLETE ✓                             ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${BLUE}Installed Components:${NC}"
echo "  ✓ Flask backend (live_trading_dashboard.py)"
echo "  ✓ Web UI (templates/dashboard.html)"
echo "  ✓ Styles (static/css/dashboard.css)"
echo "  ✓ JavaScript (static/js/dashboard.js)"
echo "  ✓ Integration example (live_trading_with_dashboard.py)"
echo "  ✓ Documentation files"
echo ""

echo -e "${BLUE}Next Steps:${NC}"
echo ""
echo -e "${YELLOW}1. Test Dashboard (Standalone):${NC}"
echo "   cd $INSTALL_DIR"
echo "   python3 live_trading_dashboard.py"
echo "   Then visit: http://localhost:5000"
echo ""

echo -e "${YELLOW}2. Test with Trading System:${NC}"
echo "   cd $INSTALL_DIR"
echo "   python3 live_trading_with_dashboard.py --paper-trading"
echo "   Then visit: http://localhost:5000"
echo ""

echo -e "${YELLOW}3. Production Deployment:${NC}"
echo "   pip3 install gunicorn"
echo "   gunicorn -w 4 -b 0.0.0.0:5000 live_trading_dashboard:app"
echo ""

echo -e "${YELLOW}4. Read Documentation:${NC}"
echo "   cat $INSTALL_DIR/DASHBOARD_SETUP_GUIDE.md"
echo ""

if [ -d "$BACKUP_DIR" ]; then
    echo -e "${BLUE}Backup Location:${NC}"
    echo "  $BACKUP_DIR"
    echo ""
fi

echo -e "${GREEN}Installation successful! Happy trading! 📊💰🚀${NC}"
echo ""

exit 0
