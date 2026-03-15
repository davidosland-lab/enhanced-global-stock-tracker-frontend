#!/bin/bash
# v1.3.11 Calibration Patch Installer
# Date: January 2, 2026

echo "========================================"
echo "  v1.3.11 Calibration Patch Installer"
echo "========================================"
echo ""
echo "This will install the calibration fix to your"
echo "existing Phase 3 Trading System installation."
echo ""
echo "IMPORTANT: Dashboard will be stopped during installation."
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."

# Default installation directory
DEFAULT_DIR="$HOME/Trading/phase3_trading_system_v1.3.10"

echo ""
echo "Enter your installation directory:"
echo "(Press Enter to use default: $DEFAULT_DIR)"
echo ""
read -p "Installation directory: " INSTALL_DIR

# Use default if no input
if [ -z "$INSTALL_DIR" ]; then
    INSTALL_DIR="$DEFAULT_DIR"
fi

# Verify directory exists
if [ ! -d "$INSTALL_DIR/phase3_intraday_deployment" ]; then
    echo ""
    echo "ERROR: Installation directory not found!"
    echo "Checked: $INSTALL_DIR/phase3_intraday_deployment"
    echo ""
    echo "Please verify your installation path and try again."
    exit 1
fi

echo ""
echo "Installation directory: $INSTALL_DIR"
echo ""

# Stop any running dashboard
echo "Step 1: Stopping dashboard..."
pkill -f unified_trading_dashboard 2>/dev/null
sleep 2
echo "Done."
echo ""

# Create backup
echo "Step 2: Creating backup..."
BACKUP_FILE="$INSTALL_DIR/phase3_intraday_deployment/unified_trading_dashboard.py.v1.3.10.backup"
cp "$INSTALL_DIR/phase3_intraday_deployment/unified_trading_dashboard.py" "$BACKUP_FILE" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "Backup created: unified_trading_dashboard.py.v1.3.10.backup"
else
    echo "WARNING: Could not create backup!"
    read -p "Continue anyway? (y/N): " CONTINUE
    if [ "$CONTINUE" != "y" ] && [ "$CONTINUE" != "Y" ]; then
        exit 1
    fi
fi
echo ""

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Copy updated file
echo "Step 3: Installing patch..."
cp "$SCRIPT_DIR/phase3_intraday_deployment/unified_trading_dashboard.py" "$INSTALL_DIR/phase3_intraday_deployment/" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "Patch installed successfully!"
else
    echo "ERROR: Failed to copy patch file!"
    echo ""
    echo "Restoring backup..."
    cp "$BACKUP_FILE" "$INSTALL_DIR/phase3_intraday_deployment/unified_trading_dashboard.py" 2>/dev/null
    echo "Backup restored."
    exit 1
fi
echo ""

# Verify installation
echo "Step 4: Verifying installation..."
if [ -f "$INSTALL_DIR/phase3_intraday_deployment/unified_trading_dashboard.py" ]; then
    echo "File verified: unified_trading_dashboard.py"
    echo ""
    echo "========================================"
    echo "  Installation Complete!"
    echo "========================================"
    echo ""
    echo "v1.3.11 Calibration Patch installed successfully."
    echo ""
    echo "Next steps:"
    echo "1. Read PATCH_INSTALLATION_GUIDE.md for details"
    echo "2. Restart your dashboard"
    echo "3. Verify charts show 'Change from Prev Close'"
    echo ""
    read -p "Start dashboard now? (y/N): " START_DASH
    
    if [ "$START_DASH" = "y" ] || [ "$START_DASH" = "Y" ]; then
        echo ""
        echo "Starting dashboard..."
        cd "$INSTALL_DIR/phase3_intraday_deployment"
        
        # Check for virtual environment
        if [ -f "../venv/bin/activate" ]; then
            source ../venv/bin/activate
        fi
        
        nohup python unified_trading_dashboard.py > /tmp/dashboard.log 2>&1 &
        sleep 2
        
        if pgrep -f unified_trading_dashboard > /dev/null; then
            echo "Dashboard started!"
            echo "Open browser: http://localhost:8050"
        else
            echo "Failed to start dashboard automatically."
            echo "Please start manually: python unified_trading_dashboard.py"
        fi
    fi
else
    echo "ERROR: Installation verification failed!"
    exit 1
fi

echo ""
echo "Installation complete."
echo ""
