#!/usr/bin/env python3
"""
Phase 3 Market Regime Intelligence System - Setup Script
Version: v1.3.13 - Complete Backend Package
Author: David Osland Lab
Date: January 6, 2026

This setup script provides easy installation and configuration
of the complete backend system.
"""

from setuptools import setup, find_packages
import os
import sys

# Check Python version
if sys.version_info < (3, 8):
    sys.exit("ERROR: Python 3.8 or higher is required")

# Read the long description from README
def read_long_description():
    readme_path = os.path.join(os.path.dirname(__file__), 'COMPLETE_INSTALLATION_GUIDE.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Phase 3 Market Regime Intelligence System - Complete Backend Package"

# Core dependencies (required)
CORE_REQUIREMENTS = [
    'yfinance>=0.2.28',
    'yahooquery>=2.3.0',
    'pandas>=1.5.0',
    'numpy>=1.23.0',
    'flask>=2.3.0',
    'werkzeug>=2.3.0',
    'requests>=2.31.0',
    'python-dotenv>=1.0.0',
    'bcrypt>=4.0.0',
]

# Optional dependencies for extra features
EXTRAS_REQUIRE = {
    # Production deployment
    'production': [
        'gunicorn>=21.2.0',
        'prometheus-client>=0.17.0',
        'sentry-sdk>=1.25.0',
    ],
    
    # Machine learning & analysis
    'ml': [
        'scikit-learn>=1.3.0',
        'scipy>=1.10.0',
    ],
    
    # Visualization & reporting
    'visualization': [
        'matplotlib>=3.7.0',
        'seaborn>=0.12.0',
        'plotly>=5.14.0',
    ],
    
    # Testing & development
    'dev': [
        'pytest>=7.3.0',
        'pytest-cov>=4.1.0',
        'pytest-mock>=3.11.0',
        'black>=23.3.0',
        'flake8>=6.0.0',
        'pylint>=2.17.0',
        'mypy>=1.3.0',
    ],
    
    # Database support
    'database': [
        'sqlalchemy>=2.0.0',
        'psycopg2-binary>=2.9.0',
    ],
    
    # Performance optimization
    'performance': [
        'numba>=0.57.0',
        'joblib>=1.2.0',
        'cachetools>=5.3.0',
    ],
}

# All optional dependencies combined
EXTRAS_REQUIRE['all'] = list(set(
    dep for extra in EXTRAS_REQUIRE.values() for dep in extra
))

# Package configuration
setup(
    name='regime-intelligence-backend',
    version='1.3.13',
    description='Phase 3 Market Regime Intelligence System - Complete Backend',
    long_description=read_long_description(),
    long_description_content_type='text/markdown',
    author='David Osland Lab',
    author_email='support@davidosland-lab.com',
    url='https://github.com/davidosland-lab/enhanced-global-stock-tracker-frontend',
    
    # Package discovery
    packages=find_packages(exclude=['tests', 'tests.*', 'docs']),
    include_package_data=True,
    
    # Python version requirement
    python_requires='>=3.8',
    
    # Dependencies
    install_requires=CORE_REQUIREMENTS,
    extras_require=EXTRAS_REQUIRE,
    
    # Package data
    package_data={
        '': [
            'config/*.json',
            'docs/*.md',
            'scripts/*.bat',
            'scripts/*.sh',
            'data/.gitkeep',
        ],
    },
    
    # Entry points for CLI scripts
    entry_points={
        'console_scripts': [
            'regime-au-pipeline=run_au_pipeline_v1.3.13:main',
            'regime-us-pipeline=run_us_pipeline_v1.3.13:main',
            'regime-uk-pipeline=run_uk_pipeline_v1.3.13:main',
            'regime-dashboard=regime_dashboard:main',
            'regime-dashboard-prod=regime_dashboard_production:main',
            'regime-test=test_integration:main',
        ],
    },
    
    # Classifiers for PyPI
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Financial and Insurance Industry',
        'Intended Audience :: Developers',
        'Topic :: Office/Business :: Financial :: Investment',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
        'Environment :: Console',
        'Environment :: Web Environment',
    ],
    
    # Keywords for discoverability
    keywords=[
        'trading',
        'stock-market',
        'regime-detection',
        'market-intelligence',
        'algorithmic-trading',
        'quantitative-finance',
        'machine-learning',
        'financial-analysis',
    ],
    
    # Project URLs
    project_urls={
        'Bug Reports': 'https://github.com/davidosland-lab/enhanced-global-stock-tracker-frontend/issues',
        'Source': 'https://github.com/davidosland-lab/enhanced-global-stock-tracker-frontend',
        'Documentation': 'https://github.com/davidosland-lab/enhanced-global-stock-tracker-frontend/tree/main/docs',
        'Pull Request': 'https://github.com/davidosland-lab/enhanced-global-stock-tracker-frontend/pull/11',
    },
)

# Post-installation message
def print_post_install_message():
    """Print helpful message after installation"""
    message = """
╔════════════════════════════════════════════════════════════════════╗
║  REGIME INTELLIGENCE SYSTEM v1.3.13 - INSTALLATION COMPLETE! [OK]   ║
╚════════════════════════════════════════════════════════════════════╝

🎉 Successfully installed Phase 3 Market Regime Intelligence System!

📚 NEXT STEPS:

1️⃣  Verify Installation:
   python test_integration.py

2️⃣  Run Your First Pipeline:
   python run_au_pipeline_v1.3.13.py    # Australian market
   python run_us_pipeline_v1.3.13.py    # US market
   python run_uk_pipeline_v1.3.13.py    # UK market

3️⃣  Launch Dashboard:
   python regime_dashboard.py           # Development mode
   python regime_dashboard_production.py # Production mode (with auth)

4️⃣  Read Documentation:
   See COMPLETE_INSTALLATION_GUIDE.md for detailed instructions

[#] COVERAGE: 720 stocks across AU/US/UK markets (240 per market)

🔧 OPTIONAL FEATURES:
   pip install .[ml]            # Machine learning features
   pip install .[production]    # Production deployment tools
   pip install .[visualization] # Charts & graphs
   pip install .[dev]           # Development & testing tools
   pip install .[all]           # Everything

📞 SUPPORT:
   GitHub: https://github.com/davidosland-lab/enhanced-global-stock-tracker-frontend
   Issues: https://github.com/davidosland-lab/enhanced-global-stock-tracker-frontend/issues
   PR: https://github.com/davidosland-lab/enhanced-global-stock-tracker-frontend/pull/11

[=>] TRADE SMARTER WITH REGIME INTELLIGENCE!

"""
    print(message)

if __name__ == '__main__':
    # If running directly (not via pip), show installation instructions
    print("""
╔════════════════════════════════════════════════════════════════════╗
║  REGIME INTELLIGENCE SYSTEM v1.3.13 - SETUP SCRIPT               ║
╚════════════════════════════════════════════════════════════════════╝

To install this package, run:

  📦 BASIC INSTALLATION (Core features):
     pip install .

  📦 FULL INSTALLATION (All features):
     pip install .[all]

  📦 DEVELOPMENT INSTALLATION (Editable mode):
     pip install -e .[dev]

  📦 PRODUCTION INSTALLATION:
     pip install .[production]

After installation, run 'python test_integration.py' to verify setup.

For detailed installation instructions, see:
  COMPLETE_INSTALLATION_GUIDE.md
""")
