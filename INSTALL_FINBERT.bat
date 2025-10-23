@echo off
echo ============================================
echo FINBERT INSTALLATION FOR DOCUMENT ANALYZER
echo ============================================
echo.
echo This will install the required packages for
echo financial sentiment analysis using FinBERT.
echo.
echo Required packages:
echo - transformers (Hugging Face)
echo - torch (PyTorch)
echo - sentencepiece
echo - protobuf
echo - PyPDF2 (for PDF processing)
echo - python-docx (for Word documents)
echo.
pause

echo.
echo [1/6] Installing transformers library...
pip install transformers

echo.
echo [2/6] Installing PyTorch (CPU version)...
pip install torch torchvision torchaudio

echo.
echo [3/6] Installing sentencepiece...
pip install sentencepiece

echo.
echo [4/6] Installing protobuf...
pip install protobuf

echo.
echo [5/6] Installing PyPDF2 for PDF processing...
pip install PyPDF2

echo.
echo [6/6] Installing python-docx for Word documents...
pip install python-docx

echo.
echo ============================================
echo TESTING FINBERT INSTALLATION
echo ============================================
python -c "from transformers import pipeline; print('FinBERT import successful!')"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✓ FinBERT installation successful!
    echo.
    echo The model will be downloaded on first use (~400MB)
    echo This happens only once and will be cached.
) else (
    echo.
    echo ✗ Installation may have issues.
    echo Please check error messages above.
)

echo.
echo ============================================
echo INSTALLATION COMPLETE
echo ============================================
echo.
echo To use the Document Analyzer with FinBERT:
echo 1. Run: python document_analyzer_with_finbert.py
echo 2. It will run on port 8004
echo 3. Update frontend to use port 8004 for document analysis
echo.
pause