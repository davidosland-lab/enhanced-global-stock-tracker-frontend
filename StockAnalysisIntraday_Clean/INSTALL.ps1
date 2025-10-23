# PowerShell Installation Script
# More robust than batch files

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "     STOCK ANALYSIS SYSTEM - INSTALLER" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not installed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Python from: https://python.org" -ForegroundColor Yellow
    Write-Host "IMPORTANT: Check 'Add Python to PATH' during installation" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit
}

Write-Host ""
Write-Host "Installing packages..." -ForegroundColor Yellow
Write-Host "This may take 3-5 minutes on first installation" -ForegroundColor Gray
Write-Host ""

# Package list
$packages = @(
    @{name="Flask"; pip="flask"},
    @{name="Flask-CORS"; pip="flask-cors"},
    @{name="yfinance"; pip="yfinance"},
    @{name="pandas"; pip="pandas"},
    @{name="numpy"; pip="numpy"},
    @{name="scikit-learn"; pip="scikit-learn"},
    @{name="requests"; pip="requests"},
    @{name="ta (optional)"; pip="ta"}
)

# Install each package
foreach ($package in $packages) {
    Write-Host "Installing $($package.name)..." -ForegroundColor White
    $output = pip install $($package.pip) 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ $($package.name) installed successfully" -ForegroundColor Green
    } else {
        if ($package.pip -eq "ta") {
            Write-Host "  ⚠ $($package.name) not installed (optional)" -ForegroundColor Yellow
        } else {
            Write-Host "  ✗ Failed to install $($package.name)" -ForegroundColor Red
            Write-Host "  Trying without version..." -ForegroundColor Yellow
            pip install $($package.pip) --no-deps 2>&1
        }
    }
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "     VERIFYING INSTALLATION" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Test imports
$modules = @("flask", "flask_cors", "yfinance", "pandas", "numpy", "sklearn", "requests")
$allGood = $true

foreach ($module in $modules) {
    try {
        python -c "import $module" 2>&1 | Out-Null
        Write-Host "✓ $module is working" -ForegroundColor Green
    } catch {
        Write-Host "✗ $module is not working" -ForegroundColor Red
        $allGood = $false
    }
}

Write-Host ""
if ($allGood) {
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "     INSTALLATION SUCCESSFUL!" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "You can now run: START.ps1 or START_FIXED.bat" -ForegroundColor Yellow
} else {
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "     SOME PACKAGES FAILED" -ForegroundColor Red
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Try running: pip install -r requirements.txt" -ForegroundColor Yellow
}

Write-Host ""
Read-Host "Press Enter to close"