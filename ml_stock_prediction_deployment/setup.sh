#!/bin/bash
# ML Stock Prediction System - Quick Setup Script

echo "🚀 ML Stock Prediction System Setup"
echo "===================================="

# Check Python version
python3 --version

echo ""
echo "📋 Step 1: Running diagnostic tool..."
python3 diagnostic_tool.py

echo ""
echo "📦 Step 2: Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the system:"
echo "  python3 ml_core_enhanced_production_fixed.py"
echo ""
echo "Then open: http://localhost:8000"
