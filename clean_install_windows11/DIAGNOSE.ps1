# Diagnostic script to understand the issue
Clear-Host
Write-Host "=== STOCK TRACKER DIAGNOSTIC ===" -ForegroundColor Cyan
Write-Host ""

# Show current directory
Write-Host "Current Directory:" -ForegroundColor Yellow
Get-Location
Write-Host ""

# List Python files
Write-Host "Python Files in Directory:" -ForegroundColor Yellow
Get-ChildItem -Filter "*.py" | Select-Object Name, Length | Format-Table
Write-Host ""

# List HTML files
Write-Host "HTML Files in Directory:" -ForegroundColor Yellow
Get-ChildItem -Filter "*.html" | Select-Object Name, Length | Format-Table
Write-Host ""

# Check for critical files
Write-Host "Critical File Check:" -ForegroundColor Yellow
$files = @(
    "backend.py",
    "backend_ml_enhanced.py", 
    "index.html",
    "index_complete.html",
    "FINAL_FIX_ALL.py",
    "FIX_ML_PORT.py"
)

foreach ($file in $files) {
    if (Test-Path $file) {
        $size = (Get-Item $file).Length
        Write-Host "[✓] $file (Size: $size bytes)" -ForegroundColor Green
    } else {
        Write-Host "[✗] $file - NOT FOUND" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Port Status:" -ForegroundColor Yellow
$ports = @(8000, 8002, 8003)
foreach ($port in $ports) {
    $conn = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($conn) {
        Write-Host "[✓] Port $port is IN USE" -ForegroundColor Green
    } else {
        Write-Host "[✗] Port $port is FREE" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "=== END DIAGNOSTIC ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "To fix issues, run: .\WINDOWS_ABSOLUTE_FIX.bat" -ForegroundColor Yellow