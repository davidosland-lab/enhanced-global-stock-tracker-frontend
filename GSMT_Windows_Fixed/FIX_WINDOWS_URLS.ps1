# GSMT Windows URL Fix Script
# Fixes dynamic URL construction to use hardcoded localhost

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  GSMT Windows URL Fix Script" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get current directory
$currentDir = Get-Location
Write-Host "Current directory: $currentDir" -ForegroundColor Gray

# Check if we're in the right directory
if (-not (Test-Path "simple_working_dashboard.html")) {
    Write-Host "ERROR: simple_working_dashboard.html not found!" -ForegroundColor Red
    Write-Host "Looking for GSMT installation..." -ForegroundColor Yellow
    
    # Check common locations
    $possiblePaths = @(
        "C:\GSMT\GSMT_Windows_Package",
        "C:\GSMT",
        "$env:USERPROFILE\Desktop\GSMT",
        "$env:USERPROFILE\Downloads\GSMT_Windows_Package"
    )
    
    foreach ($path in $possiblePaths) {
        if (Test-Path "$path\simple_working_dashboard.html") {
            Write-Host "Found GSMT at: $path" -ForegroundColor Green
            Set-Location $path
            break
        }
    }
    
    # Check again
    if (-not (Test-Path "simple_working_dashboard.html")) {
        Write-Host "ERROR: Cannot find GSMT files!" -ForegroundColor Red
        Write-Host "Please navigate to the GSMT directory and run this script again." -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host "Found GSMT files. Starting fix..." -ForegroundColor Green
Write-Host ""

# Function to fix URLs in a file
function Fix-FileURLs {
    param($FilePath)
    
    if (Test-Path $FilePath) {
        $content = Get-Content $FilePath -Raw
        $originalContent = $content
        
        # Fix various URL patterns
        $patterns = @(
            @{
                Pattern = 'window\.location\.protocol\s*\+\s*[''\"]/[''\"]\s*\+\s*window\.location\.hostname\.replace\([^)]+\)'
                Replace = '''http://localhost:8002'''
            },
            @{
                Pattern = 'const\s+API_URL\s*=\s*window\.location[^;]+'
                Replace = 'const API_URL = ''http://localhost:8002'''
            }
        )
        
        foreach ($p in $patterns) {
            $content = $content -replace $p.Pattern, $p.Replace
        }
        
        if ($content -ne $originalContent) {
            Set-Content -Path $FilePath -Value $content -Encoding UTF8
            Write-Host "  ✓ Fixed: $FilePath" -ForegroundColor Green
            return $true
        } else {
            Write-Host "  - No changes needed: $FilePath" -ForegroundColor Gray
            return $false
        }
    } else {
        Write-Host "  × File not found: $FilePath" -ForegroundColor Red
        return $false
    }
}

# Fix main dashboard
Write-Host "Fixing main dashboard..." -ForegroundColor Yellow
Fix-FileURLs "simple_working_dashboard.html"

# Fix all module files
Write-Host ""
Write-Host "Fixing module files..." -ForegroundColor Yellow
if (Test-Path "modules") {
    Get-ChildItem "modules\*.html" | ForEach-Object {
        Fix-FileURLs $_.FullName
    }
} else {
    Write-Host "  × Modules directory not found!" -ForegroundColor Red
}

# Verify the fix
Write-Host ""
Write-Host "Verifying fixes..." -ForegroundColor Yellow

$dashboard = Get-Content "simple_working_dashboard.html" -Raw
if ($dashboard -match 'http://localhost:8002') {
    Write-Host "  ✓ Dashboard is correctly configured" -ForegroundColor Green
} else {
    Write-Host "  × Dashboard still has dynamic URLs!" -ForegroundColor Red
}

# Count fixed files
$fixedCount = 0
Get-ChildItem "*.html", "modules\*.html" -ErrorAction SilentlyContinue | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    if ($content -match 'http://localhost:8002') {
        $fixedCount++
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Fix Complete!" -ForegroundColor Green
Write-Host "  $fixedCount files are using localhost:8002" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Run START_GSMT_WINDOWS.bat to start the application" -ForegroundColor White
Write-Host "2. Open http://localhost:8002 in your browser to verify backend" -ForegroundColor White
Write-Host "3. The dashboard will open automatically" -ForegroundColor White
Write-Host ""

Read-Host "Press Enter to exit"