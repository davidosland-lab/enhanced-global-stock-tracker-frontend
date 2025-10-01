#!/usr/bin/env python3
"""
Setup script for Stock Predictor Pro
Creates installable package for Windows 11
"""

from setuptools import setup, find_packages
import os
import sys
from pathlib import Path

# Read long description from README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text() if readme_path.exists() else ""

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
with open(requirements_path) as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

# Package metadata
setup(
    name="stock-predictor-pro",
    version="1.0.0",
    author="Stock Predictor Team",
    author_email="support@stockpredictorpro.com",
    description="Professional AI-powered stock prediction and trading system for Windows",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/stock-predictor-pro",
    license="Proprietary",
    
    # Packages
    packages=find_packages(exclude=["tests", "tests.*", "docs", "docs.*"]),
    python_requires=">=3.9",
    
    # Dependencies
    install_requires=requirements,
    
    # Extra dependencies
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
        "cuda": [
            "torch @ https://download.pytorch.org/whl/cu118/torch-2.0.0%2Bcu118-cp39-cp39-win_amd64.whl",
            "torchvision @ https://download.pytorch.org/whl/cu118/torchvision-0.15.0%2Bcu118-cp39-cp39-win_amd64.whl",
        ],
    },
    
    # Entry points
    entry_points={
        "console_scripts": [
            "stock-predictor=stock_predictor_pro:main",
            "sp-pro=stock_predictor_pro:main",
        ],
        "gui_scripts": [
            "stock-predictor-gui=stock_predictor_pro:main",
        ],
    },
    
    # Package data
    package_data={
        "": ["*.json", "*.yaml", "*.yml", "*.txt", "*.md"],
        "assets": ["*.ico", "*.png", "*.jpg"],
        "models": ["*.pkl", "*.h5", "*.pt", "*.onnx"],
        "data": ["*.csv", "*.db"],
    },
    
    # Data files
    data_files=[
        ("", ["README.md", "LICENSE", "requirements.txt"]),
        ("assets", ["assets/icon.ico"] if os.path.exists("assets/icon.ico") else []),
    ],
    
    # Classification
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: Other/Proprietary License",
        "Operating System :: Microsoft :: Windows :: Windows 11",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Environment :: Win32 (MS Windows)",
        "Environment :: GPU :: NVIDIA CUDA",
    ],
    
    # Keywords
    keywords="stock trading prediction ai machine-learning finance investment",
    
    # Project URLs
    project_urls={
        "Documentation": "https://docs.stockpredictorpro.com",
        "Bug Reports": "https://github.com/yourusername/stock-predictor-pro/issues",
        "Source": "https://github.com/yourusername/stock-predictor-pro",
        "Support": "https://support.stockpredictorpro.com",
    },
    
    # Platform
    platforms=["Windows"],
    
    # Zip safe
    zip_safe=False,
)