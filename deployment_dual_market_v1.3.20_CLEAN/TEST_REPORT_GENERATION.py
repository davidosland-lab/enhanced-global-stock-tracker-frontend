"""
Test Report Generation

This script tests if the report generator can create reports successfully.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from models.screening.report_generator import ReportGenerator
from datetime import datetime

def test_report_generation():
    """Test basic report generation"""
    print("="*80)
    print("REPORT GENERATION TEST")
    print("="*80)
    
    # Create report generator
    print("\n1. Initializing Report Generator...")
    try:
        generator = ReportGenerator()
        print("   ✓ Report Generator initialized")
        print(f"   Report directory: {generator.report_dir}")
    except Exception as e:
        print(f"   ✗ Failed to initialize: {e}")
        return False
    
    # Check if directory was created
    print("\n2. Checking if report directory exists...")
    if generator.report_dir.exists():
        print(f"   ✓ Directory exists: {generator.report_dir}")
    else:
        print(f"   ✗ Directory does NOT exist: {generator.report_dir}")
        return False
    
    # Create sample data
    print("\n3. Creating sample data...")
    sample_stocks = [
        {
            'symbol': 'CBA.AX',
            'company_name': 'Commonwealth Bank',
            'sector': 'Financials',
            'prediction': 0.05,
            'confidence': 75.0,
            'opportunity_score': 85.5,
            'technical': {
                'rsi': 65.0,
                'macd_signal': 'bullish',
                'volume_trend': 'increasing'
            },
            'sentiment': {
                'direction': 'positive',
                'confidence': 70.0
            }
        },
        {
            'symbol': 'BHP.AX',
            'company_name': 'BHP Group',
            'sector': 'Materials',
            'prediction': 0.03,
            'confidence': 68.0,
            'opportunity_score': 78.2,
            'technical': {
                'rsi': 55.0,
                'macd_signal': 'bullish',
                'volume_trend': 'stable'
            },
            'sentiment': {
                'direction': 'neutral',
                'confidence': 60.0
            }
        }
    ]
    
    sample_spi = {
        'gap': 0.5,
        'direction': 'bullish',
        'confidence': 70,
        'indices': {
            'us': {
                'sp500': {'change': 0.8},
                'nasdaq': {'change': 1.2}
            }
        }
    }
    
    print("   ✓ Sample data created")
    
    # Generate report
    print("\n4. Generating report...")
    try:
        report_path = generator.generate_morning_report(
            opportunities=sample_stocks,
            spi_sentiment=sample_spi,
            scan_time=datetime.now(),
            total_scanned=240,
            high_confidence_count=50
        )
        print(f"   ✓ Report generated: {report_path}")
        
        # Check if file exists
        if Path(report_path).exists():
            file_size = Path(report_path).stat().st_size / 1024
            print(f"   ✓ Report file exists ({file_size:.1f} KB)")
            print(f"\n   Open in browser: file://{Path(report_path).absolute()}")
            return True
        else:
            print(f"   ✗ Report file NOT found: {report_path}")
            return False
            
    except Exception as e:
        print(f"   ✗ Failed to generate report: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_directory_permissions():
    """Test if we can create the reports directory"""
    print("\n5. Testing directory creation...")
    
    test_dir = Path("reports/test_reports")
    try:
        test_dir.mkdir(parents=True, exist_ok=True)
        print(f"   ✓ Can create directory: {test_dir}")
        
        # Try to write a file
        test_file = test_dir / "test.txt"
        test_file.write_text("Test content")
        print(f"   ✓ Can write files: {test_file}")
        
        # Clean up
        test_file.unlink()
        test_dir.rmdir()
        print("   ✓ Cleanup successful")
        
        return True
    except Exception as e:
        print(f"   ✗ Directory test failed: {e}")
        return False

if __name__ == "__main__":
    print("\nRunning Report Generation Tests...\n")
    
    # Test directory permissions
    dir_test = test_directory_permissions()
    
    # Test report generation
    report_test = test_report_generation()
    
    print("\n" + "="*80)
    print("TEST RESULTS")
    print("="*80)
    print(f"Directory Test: {'✓ PASS' if dir_test else '✗ FAIL'}")
    print(f"Report Test:    {'✓ PASS' if report_test else '✗ FAIL'}")
    print("="*80)
    
    if dir_test and report_test:
        print("\n✅ All tests passed! Report generation is working.")
        print("\nIf the pipeline still doesn't generate reports, check:")
        print("  1. Does the pipeline complete without errors?")
        print("  2. Are there any stocks in 'final_opportunities'?")
        print("  3. Check logs in logs/screening/overnight_pipeline.log")
    else:
        print("\n❌ Some tests failed. Report generation has issues.")
        sys.exit(1)
