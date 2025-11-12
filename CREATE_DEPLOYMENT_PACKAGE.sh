#!/bin/bash

# FinBERT v4.0 - Deployment Package Creator
# Creates production-ready deployment archives
# Usage: ./CREATE_DEPLOYMENT_PACKAGE.sh [deploy|enhanced|both]

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
WORKING_DIR="/home/user/webapp"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="$WORKING_DIR/deployment_packages"

# Package paths
DEPLOY_DIR="$WORKING_DIR/FinBERT_v4.0_Windows11_DEPLOY"
ENHANCED_DIR="$WORKING_DIR/FinBERT_v4.0_Windows11_ENHANCED"

# Output files
DEPLOY_TAR="FinBERT_v4.0_DEPLOY_${TIMESTAMP}.tar.gz"
DEPLOY_ZIP="FinBERT_v4.0_DEPLOY_${TIMESTAMP}.zip"
ENHANCED_TAR="FinBERT_v4.0_ENHANCED_${TIMESTAMP}.tar.gz"
ENHANCED_ZIP="FinBERT_v4.0_ENHANCED_${TIMESTAMP}.zip"

# Functions
print_header() {
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE}  FinBERT v4.0 - Deployment Package Creator${NC}"
    echo -e "${BLUE}================================================${NC}"
    echo ""
}

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_directory() {
    local dir=$1
    local name=$2
    
    if [ ! -d "$dir" ]; then
        print_error "Directory not found: $dir"
        print_error "Cannot create $name package"
        return 1
    fi
    
    print_info "Found $name directory: $dir"
    return 0
}

verify_critical_files() {
    local dir=$1
    local name=$2
    local missing=0
    
    print_info "Verifying critical files in $name..."
    
    # Critical files that must exist
    local critical_files=(
        "app_finbert_v4_dev.py"
        "config_dev.py"
        "START_FINBERT_V4.bat"
        "scripts/INSTALL_WINDOWS11.bat"
        "templates/finbert_v4_enhanced_ui.html"
        "models/backtesting/backtest_engine.py"
        "models/backtesting/trading_simulator.py"
        "models/backtesting/parameter_optimizer.py"
        "requirements-full.txt"
        "requirements-minimal.txt"
        "README.md"
    )
    
    for file in "${critical_files[@]}"; do
        if [ ! -f "$dir/$file" ]; then
            print_error "Missing critical file: $file"
            missing=$((missing + 1))
        fi
    done
    
    if [ $missing -gt 0 ]; then
        print_error "$name: $missing critical files missing!"
        return 1
    fi
    
    print_info "$name: All critical files present ✓"
    return 0
}

verify_new_features() {
    local dir=$1
    local name=$2
    
    print_info "Verifying new features in $name..."
    
    # Check for embargo period implementation
    if grep -q "embargo_days" "$dir/models/backtesting/parameter_optimizer.py" 2>/dev/null; then
        print_info "✓ Embargo period feature found"
    else
        print_warning "✗ Embargo period feature not found"
        return 1
    fi
    
    # Check for stop-loss implementation
    if grep -q "stop_loss_pct" "$dir/models/backtesting/trading_simulator.py" 2>/dev/null; then
        print_info "✓ Stop-loss feature found"
    else
        print_warning "✗ Stop-loss feature not found"
        return 1
    fi
    
    # Check for take-profit implementation
    if grep -q "take_profit_pct" "$dir/models/backtesting/trading_simulator.py" 2>/dev/null; then
        print_info "✓ Take-profit feature found"
    else
        print_warning "✗ Take-profit feature not found"
        return 1
    fi
    
    # Check for embargo slider in UI
    if grep -q "embargoDays" "$dir/templates/finbert_v4_enhanced_ui.html" 2>/dev/null; then
        print_info "✓ Embargo UI controls found"
    else
        print_warning "✗ Embargo UI controls not found"
        return 1
    fi
    
    print_info "$name: All new features verified ✓"
    return 0
}

create_package() {
    local source_dir=$1
    local package_name=$2
    local tar_file=$3
    local zip_file=$4
    
    print_info "Creating $package_name package..."
    
    # Create output directory if it doesn't exist
    mkdir -p "$OUTPUT_DIR"
    
    # Change to working directory
    cd "$WORKING_DIR"
    
    # Get the directory name for the package
    local dir_name=$(basename "$source_dir")
    
    # Create tar.gz archive
    print_info "Creating tar.gz archive..."
    tar -czf "$OUTPUT_DIR/$tar_file" \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='*.pyo' \
        --exclude='.pytest_cache' \
        --exclude='*.log' \
        --exclude='*.db' \
        --exclude='venv' \
        --exclude='.venv' \
        "$dir_name"
    
    if [ $? -eq 0 ]; then
        local tar_size=$(du -h "$OUTPUT_DIR/$tar_file" | cut -f1)
        print_info "✓ Created: $tar_file ($tar_size)"
    else
        print_error "Failed to create tar.gz archive"
        return 1
    fi
    
    # Create ZIP archive (better for Windows)
    print_info "Creating ZIP archive..."
    zip -r -q "$OUTPUT_DIR/$zip_file" "$dir_name" \
        -x '*/\__pycache__/*' \
        -x '*/*.pyc' \
        -x '*/*.pyo' \
        -x '*/.pytest_cache/*' \
        -x '*/*.log' \
        -x '*/*.db' \
        -x '*/venv/*' \
        -x '*/.venv/*'
    
    if [ $? -eq 0 ]; then
        local zip_size=$(du -h "$OUTPUT_DIR/$zip_file" | cut -f1)
        print_info "✓ Created: $zip_file ($zip_size)"
    else
        print_error "Failed to create ZIP archive"
        return 1
    fi
    
    return 0
}

create_manifest() {
    local manifest_file="$OUTPUT_DIR/DEPLOYMENT_MANIFEST_${TIMESTAMP}.txt"
    
    print_info "Creating deployment manifest..."
    
    cat > "$manifest_file" << EOF
================================================================================
FinBERT v4.0 - Deployment Package Manifest
================================================================================

Created: $(date)
Git Commit: $(cd "$WORKING_DIR" && git rev-parse --short HEAD 2>/dev/null || echo "N/A")
Git Branch: $(cd "$WORKING_DIR" && git branch --show-current 2>/dev/null || echo "N/A")

================================================================================
DEPLOYMENT PACKAGES
================================================================================

EOF

    # List all files in output directory
    echo "Files Created:" >> "$manifest_file"
    echo "" >> "$manifest_file"
    ls -lh "$OUTPUT_DIR" | tail -n +2 >> "$manifest_file"
    
    echo "" >> "$manifest_file"
    echo "================================================================================\n" >> "$manifest_file"
    echo "PACKAGE CONTENTS\n" >> "$manifest_file"
    echo "================================================================================\n" >> "$manifest_file"
    
    # Add file tree for DEPLOY package if it exists
    if [ -d "$DEPLOY_DIR" ]; then
        echo "\n--- DEPLOY Package Structure ---\n" >> "$manifest_file"
        tree -L 2 -I '__pycache__|*.pyc|venv|.venv' "$DEPLOY_DIR" >> "$manifest_file" 2>/dev/null || \
            find "$DEPLOY_DIR" -maxdepth 2 -type f -o -type d | grep -v '__pycache__\|\.pyc\|venv' >> "$manifest_file"
        echo "" >> "$manifest_file"
    fi
    
    # Add file tree for ENHANCED package if it exists
    if [ -d "$ENHANCED_DIR" ]; then
        echo "\n--- ENHANCED Package Structure ---\n" >> "$manifest_file"
        tree -L 2 -I '__pycache__|*.pyc|venv|.venv' "$ENHANCED_DIR" >> "$manifest_file" 2>/dev/null || \
            find "$ENHANCED_DIR" -maxdepth 2 -type f -o -type d | grep -v '__pycache__\|\.pyc\|venv' >> "$manifest_file"
        echo "" >> "$manifest_file"
    fi
    
    echo "\n================================================================================\n" >> "$manifest_file"
    echo "NEW FEATURES (v4.0 Risk Management Edition)\n" >> "$manifest_file"
    echo "================================================================================\n" >> "$manifest_file"
    echo "" >> "$manifest_file"
    echo "✓ Embargo Period:    3-day default (1-10 configurable)" >> "$manifest_file"
    echo "✓ Stop-Loss:         3% default (2%, 3%, 5% options)" >> "$manifest_file"
    echo "✓ Take-Profit:       10% default (5%, 10%, 15% options)" >> "$manifest_file"
    echo "✓ UI Controls:       Embargo slider, stop/profit display" >> "$manifest_file"
    echo "✓ Testing:           Comprehensive test suite (test_embargo_stoploss.py)" >> "$manifest_file"
    echo "✓ Documentation:     Complete implementation guide" >> "$manifest_file"
    echo "" >> "$manifest_file"
    echo "================================================================================\n" >> "$manifest_file"
    echo "DEPLOYMENT INSTRUCTIONS\n" >> "$manifest_file"
    echo "================================================================================\n" >> "$manifest_file"
    echo "" >> "$manifest_file"
    echo "1. Extract package to Windows machine" >> "$manifest_file"
    echo "   Example: C:\\FinBERT_v4.0\\" >> "$manifest_file"
    echo "" >> "$manifest_file"
    echo "2. Run installation script as Administrator" >> "$manifest_file"
    echo "   Location: scripts\\INSTALL_WINDOWS11.bat" >> "$manifest_file"
    echo "   Right-click → 'Run as Administrator'" >> "$manifest_file"
    echo "" >> "$manifest_file"
    echo "3. Choose FULL installation (recommended)" >> "$manifest_file"
    echo "   Press: 1" >> "$manifest_file"
    echo "" >> "$manifest_file"
    echo "4. Start application" >> "$manifest_file"
    echo "   Double-click: START_FINBERT_V4.bat" >> "$manifest_file"
    echo "" >> "$manifest_file"
    echo "5. Open browser" >> "$manifest_file"
    echo "   Navigate to: http://127.0.0.1:5001" >> "$manifest_file"
    echo "" >> "$manifest_file"
    echo "For detailed instructions, see DEPLOYMENT_INSTRUCTIONS.md" >> "$manifest_file"
    echo "" >> "$manifest_file"
    echo "================================================================================\n" >> "$manifest_file"
    
    print_info "✓ Created manifest: $(basename $manifest_file)"
}

# Main execution
main() {
    print_header
    
    local mode="${1:-both}"
    local deploy_success=0
    local enhanced_success=0
    
    case "$mode" in
        deploy)
            print_info "Mode: DEPLOY package only"
            ;;
        enhanced)
            print_info "Mode: ENHANCED package only"
            ;;
        both)
            print_info "Mode: Both DEPLOY and ENHANCED packages"
            ;;
        *)
            print_error "Invalid mode: $mode"
            echo "Usage: $0 [deploy|enhanced|both]"
            exit 1
            ;;
    esac
    
    echo ""
    
    # Process DEPLOY package
    if [ "$mode" = "deploy" ] || [ "$mode" = "both" ]; then
        print_info "Processing DEPLOY package..."
        echo ""
        
        if check_directory "$DEPLOY_DIR" "DEPLOY"; then
            if verify_critical_files "$DEPLOY_DIR" "DEPLOY"; then
                if verify_new_features "$DEPLOY_DIR" "DEPLOY"; then
                    if create_package "$DEPLOY_DIR" "DEPLOY" "$DEPLOY_TAR" "$DEPLOY_ZIP"; then
                        deploy_success=1
                        print_info "✓ DEPLOY package created successfully!"
                    fi
                fi
            fi
        fi
        echo ""
    fi
    
    # Process ENHANCED package
    if [ "$mode" = "enhanced" ] || [ "$mode" = "both" ]; then
        print_info "Processing ENHANCED package..."
        echo ""
        
        if check_directory "$ENHANCED_DIR" "ENHANCED"; then
            if verify_critical_files "$ENHANCED_DIR" "ENHANCED"; then
                if verify_new_features "$ENHANCED_DIR" "ENHANCED"; then
                    if create_package "$ENHANCED_DIR" "ENHANCED" "$ENHANCED_TAR" "$ENHANCED_ZIP"; then
                        enhanced_success=1
                        print_info "✓ ENHANCED package created successfully!"
                    fi
                fi
            fi
        fi
        echo ""
    fi
    
    # Create manifest if any packages were created
    if [ $deploy_success -eq 1 ] || [ $enhanced_success -eq 1 ]; then
        create_manifest
        echo ""
    fi
    
    # Print summary
    print_header
    print_info "Deployment Package Creation Summary"
    echo ""
    
    if [ "$mode" = "deploy" ] || [ "$mode" = "both" ]; then
        if [ $deploy_success -eq 1 ]; then
            print_info "✓ DEPLOY package: SUCCESS"
        else
            print_error "✗ DEPLOY package: FAILED"
        fi
    fi
    
    if [ "$mode" = "enhanced" ] || [ "$mode" = "both" ]; then
        if [ $enhanced_success -eq 1 ]; then
            print_info "✓ ENHANCED package: SUCCESS"
        else
            print_error "✗ ENHANCED package: FAILED"
        fi
    fi
    
    echo ""
    print_info "Output directory: $OUTPUT_DIR"
    echo ""
    
    if [ -d "$OUTPUT_DIR" ]; then
        print_info "Created files:"
        ls -lh "$OUTPUT_DIR" | tail -n +2 | awk '{print "  - " $9 " (" $5 ")"}'
    fi
    
    echo ""
    print_info "For deployment instructions, see: DEPLOYMENT_INSTRUCTIONS.md"
    echo ""
    
    # Exit with appropriate code
    if [ "$mode" = "both" ]; then
        if [ $deploy_success -eq 1 ] && [ $enhanced_success -eq 1 ]; then
            exit 0
        else
            exit 1
        fi
    elif [ "$mode" = "deploy" ]; then
        [ $deploy_success -eq 1 ] && exit 0 || exit 1
    elif [ "$mode" = "enhanced" ]; then
        [ $enhanced_success -eq 1 ] && exit 0 || exit 1
    fi
}

# Run main function
main "$@"
