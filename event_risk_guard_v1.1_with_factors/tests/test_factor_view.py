"""
Unit tests for Factor View Builder module

Tests the factor attribution analysis functionality including:
- Factor extraction from stock records
- Sector aggregations
- Portfolio summary generation
- File output creation
"""

import unittest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import pytz

# Add parent directory to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.screening.factor_view import FactorViewBuilder


class TestFactorViewBuilder(unittest.TestCase):
    """Test cases for FactorViewBuilder class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.timezone = pytz.timezone("Australia/Sydney")
        self.temp_dir = tempfile.mkdtemp()
        
        # Create builder with temp output directory
        self.builder = FactorViewBuilder(timezone=self.timezone)
        self.builder.output_dir = Path(self.temp_dir)
        
        # Sample scored stock data
        self.sample_stocks = [
            {
                'symbol': 'CBA.AX',
                'name': 'Commonwealth Bank',
                'sector': 'Financials',
                'opportunity_score': 87.3,
                'prediction': 'BUY',
                'score_breakdown': {
                    'prediction_confidence': 89.2,
                    'technical_strength': 85.4,
                    'spi_alignment': 72.5,
                    'liquidity': 95.0,
                    'volatility': 68.3,
                    'sector_momentum': 78.9
                },
                'adjustments': {
                    'total': 5.2,
                    'penalties': [],
                    'bonuses': ['spi_alignment', 'liquidity']
                },
                'macro_betas': {
                    'xjo': 0.85,
                    'lithium': 0.12
                },
                'confidence': 89.2
            },
            {
                'symbol': 'BHP.AX',
                'name': 'BHP Group',
                'sector': 'Materials',
                'opportunity_score': 84.6,
                'prediction': 'BUY',
                'score_breakdown': {
                    'prediction_confidence': 86.8,
                    'technical_strength': 88.2,
                    'spi_alignment': 75.3,
                    'liquidity': 92.5,
                    'volatility': 65.8,
                    'sector_momentum': 82.1
                },
                'adjustments': {
                    'total': 3.1,
                    'penalties': [],
                    'bonuses': ['technical_strength']
                },
                'macro_betas': {
                    'xjo': 1.20,
                    'lithium': 0.65
                },
                'confidence': 86.8
            },
            {
                'symbol': 'CSL.AX',
                'name': 'CSL Limited',
                'sector': 'Healthcare',
                'opportunity_score': 82.4,
                'prediction': 'BUY',
                'score_breakdown': {
                    'prediction_confidence': 91.5,
                    'technical_strength': 79.8,
                    'spi_alignment': 68.2,
                    'liquidity': 88.3,
                    'volatility': 72.5,
                    'sector_momentum': 75.6
                },
                'adjustments': {
                    'total': 2.5,
                    'penalties': ['spi_alignment'],
                    'bonuses': ['prediction_confidence']
                },
                'macro_betas': {
                    'xjo': 0.68,
                    'lithium': 0.05
                },
                'confidence': 91.5
            }
        ]
    
    def tearDown(self):
        """Clean up test fixtures"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_builder_initialization(self):
        """Test that builder initializes correctly"""
        self.assertIsNotNone(self.builder)
        self.assertEqual(self.builder.timezone, self.timezone)
        self.assertTrue(self.builder.output_dir.exists())
    
    def test_build_factor_view_structure(self):
        """Test that factor view builds correct structure"""
        result = self.builder.build_factor_view(self.sample_stocks)
        
        # Check top-level structure
        self.assertIn('stocks', result)
        self.assertIn('summary', result)
        
        # Check stocks data
        self.assertEqual(len(result['stocks']), 3)
        
        # Check summary structure
        summary = result['summary']
        self.assertIn('total_stocks', summary)
        self.assertIn('sectors', summary)
        self.assertIn('overall', summary)
        
        # Verify counts
        self.assertEqual(summary['total_stocks'], 3)
        self.assertEqual(len(summary['sectors']), 3)  # Financials, Materials, Healthcare
    
    def test_factor_extraction(self):
        """Test that all factors are extracted correctly"""
        result = self.builder.build_factor_view(self.sample_stocks)
        stock = result['stocks'][0]
        
        # Check all expected fields present
        expected_fields = [
            'symbol', 'name', 'sector', 'opportunity_score',
            'prediction_confidence', 'technical_strength', 'spi_alignment',
            'liquidity', 'volatility', 'sector_momentum',
            'base_total', 'total_adjustment', 'penalty_count', 'bonus_count',
            'beta_xjo', 'beta_lithium', 'prediction', 'confidence_pct'
        ]
        
        for field in expected_fields:
            self.assertIn(field, stock, f"Missing field: {field}")
    
    def test_sector_aggregation(self):
        """Test that sector aggregation calculates correctly"""
        result = self.builder.build_factor_view(self.sample_stocks)
        sectors = result['summary']['sectors']
        
        # Check Financials sector (1 stock)
        financials = sectors['Financials']
        self.assertEqual(financials['count'], 1)
        self.assertEqual(financials['avg_score'], 87.3)
        self.assertEqual(financials['buy_count'], 1)
        
        # Check Materials sector (1 stock)
        materials = sectors['Materials']
        self.assertEqual(materials['count'], 1)
        self.assertAlmostEqual(materials['avg_beta_xjo'], 1.20, places=2)
        self.assertAlmostEqual(materials['avg_beta_lithium'], 0.65, places=2)
    
    def test_beta_handling(self):
        """Test that beta values are correctly extracted and averaged"""
        result = self.builder.build_factor_view(self.sample_stocks)
        
        # Check individual stock betas
        stock = result['stocks'][0]
        self.assertEqual(stock['beta_xjo'], 0.85)
        self.assertEqual(stock['beta_lithium'], 0.12)
        
        # Check overall average betas
        overall = result['summary']['overall']
        expected_avg_xjo = (0.85 + 1.20 + 0.68) / 3
        self.assertAlmostEqual(overall['avg_beta_xjo'], expected_avg_xjo, places=2)
    
    def test_adjustment_tracking(self):
        """Test that bonuses and penalties are counted correctly"""
        result = self.builder.build_factor_view(self.sample_stocks)
        
        # CBA.AX: 0 penalties, 2 bonuses
        cba = result['stocks'][0]
        self.assertEqual(cba['penalty_count'], 0)
        self.assertEqual(cba['bonus_count'], 2)
        
        # CSL.AX: 1 penalty, 1 bonus
        csl = result['stocks'][2]
        self.assertEqual(csl['penalty_count'], 1)
        self.assertEqual(csl['bonus_count'], 1)
    
    def test_missing_data_handling(self):
        """Test that missing data is handled gracefully"""
        incomplete_stock = {
            'symbol': 'TEST.AX',
            'name': 'Test Stock',
            'sector': 'Technology',
            'opportunity_score': 75.0,
            'prediction': 'HOLD'
            # Missing score_breakdown, adjustments, macro_betas
        }
        
        # Should not raise exception
        result = self.builder.build_factor_view([incomplete_stock])
        self.assertEqual(len(result['stocks']), 1)
        
        stock = result['stocks'][0]
        # Should have default/empty values
        self.assertEqual(stock['prediction_confidence'], 0)
        self.assertEqual(stock['beta_xjo'], 0)
        self.assertEqual(stock['penalty_count'], 0)
    
    def test_save_factor_view(self):
        """Test that factor view files are saved correctly"""
        factor_view = self.builder.build_factor_view(self.sample_stocks)
        result = self.builder.save_factor_view(factor_view)
        
        # Check that all expected files are created
        self.assertIn('stocks_csv', result)
        self.assertIn('sector_csv', result)
        self.assertIn('summary_json', result)
        
        # Verify files exist
        for file_type, file_path in result.items():
            self.assertTrue(Path(file_path).exists(), f"File not created: {file_path}")
    
    def test_csv_output_format(self):
        """Test that CSV output has correct format"""
        factor_view = self.builder.build_factor_view(self.sample_stocks)
        files = self.builder.save_factor_view(factor_view)
        
        # Read stocks CSV
        import csv
        with open(files['stocks_csv'], 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            # Check row count
            self.assertEqual(len(rows), 3)
            
            # Check first row has all columns
            expected_columns = [
                'symbol', 'name', 'sector', 'opportunity_score',
                'beta_xjo', 'beta_lithium'
            ]
            for col in expected_columns:
                self.assertIn(col, rows[0], f"Missing column: {col}")
    
    def test_json_output_format(self):
        """Test that JSON output has valid structure"""
        factor_view = self.builder.build_factor_view(self.sample_stocks)
        files = self.builder.save_factor_view(factor_view)
        
        # Read and parse JSON
        with open(files['summary_json'], 'r') as f:
            data = json.load(f)
            
            # Check structure
            self.assertIn('timestamp', data)
            self.assertIn('total_stocks', data)
            self.assertIn('sectors', data)
            self.assertIn('overall', data)
            
            # Verify data types
            self.assertIsInstance(data['total_stocks'], int)
            self.assertIsInstance(data['sectors'], dict)
            self.assertEqual(data['total_stocks'], 3)
    
    def test_date_override(self):
        """Test that date override works in filenames"""
        factor_view = self.builder.build_factor_view(self.sample_stocks)
        custom_date = "2025-12-25"
        files = self.builder.save_factor_view(factor_view, date_override=custom_date)
        
        # Check that all filenames contain custom date
        for file_path in files.values():
            filename = Path(file_path).name
            self.assertIn(custom_date, filename, f"Date not in filename: {filename}")
    
    def test_empty_stocks_list(self):
        """Test handling of empty stocks list"""
        result = self.builder.build_factor_view([])
        
        self.assertEqual(len(result['stocks']), 0)
        self.assertEqual(result['summary']['total_stocks'], 0)
        self.assertEqual(len(result['summary']['sectors']), 0)


if __name__ == '__main__':
    unittest.main()
