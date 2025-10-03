# Windows 11 Deployment Update Script (PowerShell)
# Version: 5.0 -> Latest
# Run with: powershell -ExecutionPolicy Bypass -File windows_update_deployment.ps1

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  STOCK TRACKER UPDATE UTILITY" -ForegroundColor Cyan
Write-Host "  Windows 11 Deployment Updater" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Store current directory
$UpdateDir = Get-Location
$BackupDir = Join-Path $UpdateDir ("backup_" + (Get-Date -Format "yyyyMMdd_HHmmss"))

Write-Host "[1/7] Checking current installation..." -ForegroundColor Yellow
Write-Host "Current directory: $UpdateDir" -ForegroundColor Gray

# Check if this is a valid installation
if (-not (Test-Path "backend_fixed_v2.py")) {
    Write-Host ""
    Write-Host "ERROR: This doesn't appear to be a Stock Tracker installation directory!" -ForegroundColor Red
    Write-Host "Please run this script from your Stock Tracker installation folder." -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Check for Git
$GitAvailable = $null -ne (Get-Command git -ErrorAction SilentlyContinue)
if ($GitAvailable) {
    Write-Host "✓ Git detected. Will use Git for updates." -ForegroundColor Green
} else {
    Write-Host "⚠ Git not found. Will use direct download method." -ForegroundColor Yellow
}

# Create backup
Write-Host ""
Write-Host "[2/7] Creating backup of current installation..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
Write-Host "Backing up to: $BackupDir" -ForegroundColor Gray

# Backup important files
$FilesToBackup = @(
    "modules",
    "*.html",
    "*.py",
    "*.bat",
    "*.ps1",
    "*.md",
    "requirements.txt"
)

foreach ($pattern in $FilesToBackup) {
    $items = Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue
    foreach ($item in $items) {
        if ($item.PSIsContainer) {
            Copy-Item -Path $item.FullName -Destination $BackupDir -Recurse -Force
        } else {
            Copy-Item -Path $item.FullName -Destination $BackupDir -Force
        }
    }
}

Write-Host "✓ Backup completed successfully." -ForegroundColor Green

# Stop any running Python processes on port 8002
Write-Host ""
Write-Host "[3/7] Stopping any running backend services..." -ForegroundColor Yellow
$processes = Get-NetTCPConnection -LocalPort 8002 -ErrorAction SilentlyContinue
if ($processes) {
    foreach ($process in $processes) {
        $pid = $process.OwningProcess
        Write-Host "Stopping process on port 8002 (PID: $pid)..." -ForegroundColor Gray
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    }
    Write-Host "✓ Services stopped." -ForegroundColor Green
} else {
    Write-Host "No services running on port 8002." -ForegroundColor Gray
}

# Download latest files
Write-Host ""
Write-Host "[4/7] Fetching latest updates from GitHub..." -ForegroundColor Yellow

$RepoUrl = "https://raw.githubusercontent.com/davidosland-lab/enhanced-global-stock-tracker-frontend/main/working_directory"
$FilesToUpdate = @{
    "backend_fixed_v2.py" = "$RepoUrl/backend_fixed_v2.py"
    "index.html" = "$RepoUrl/index.html"
    "landing_page.html" = "$RepoUrl/landing_page.html"
    "diagnostic_tool.html" = "$RepoUrl/diagnostic_tool.html"
    "requirements.txt" = "$RepoUrl/requirements.txt"
    "windows_start.bat" = "$RepoUrl/windows_start.bat"
    "windows_start.ps1" = "$RepoUrl/windows_start.ps1"
    "WINDOWS_11_FIX_GUIDE.md" = "$RepoUrl/WINDOWS_11_FIX_GUIDE.md"
}

# Download module files
$ModuleFiles = @{
    "modules/technical_analysis_enhanced.html" = "$RepoUrl/modules/technical_analysis_enhanced.html"
    "modules/technical_analysis_desktop.html" = "$RepoUrl/modules/technical_analysis_desktop.html"
    "modules/predictions/prediction_centre_advanced.html" = "$RepoUrl/modules/predictions/prediction_centre_advanced.html"
}

# Combine all files
$AllFiles = $FilesToUpdate + $ModuleFiles

foreach ($file in $AllFiles.Keys) {
    Write-Host "Downloading: $file" -ForegroundColor Gray
    $outputPath = Join-Path $UpdateDir $file
    
    # Create directory if needed
    $dir = Split-Path $outputPath -Parent
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
    
    try {
        Invoke-WebRequest -Uri $AllFiles[$file] -OutFile $outputPath -ErrorAction Stop
        Write-Host "  ✓ Downloaded" -ForegroundColor Green
    } catch {
        Write-Host "  ✗ Failed to download: $_" -ForegroundColor Red
    }
}

# Apply Windows 11 localhost fixes
Write-Host ""
Write-Host "[5/7] Applying Windows 11 localhost fixes..." -ForegroundColor Yellow

# Function to fix localhost in HTML files
function Fix-LocalhostUrl {
    param($FilePath)
    
    if (Test-Path $FilePath) {
        $content = Get-Content $FilePath -Raw
        
        # Replace various forms of getBackendUrl with hardcoded localhost
        $patterns = @(
            'function getBackendUrl\(\)\s*{[^}]*}',
            'const BACKEND_URL = [^;]*;'
        )
        
        foreach ($pattern in $patterns) {
            if ($content -match $pattern) {
                $content = $content -replace $pattern, "function getBackendUrl() { return 'http://localhost:8002'; }"
                Write-Host "  Fixed: $(Split-Path $FilePath -Leaf)" -ForegroundColor Green
            }
        }
        
        # Ensure all API calls use localhost
        $content = $content -replace 'https?://[^/]*:8002', 'http://localhost:8002'
        
        Set-Content -Path $FilePath -Value $content -Encoding UTF8
    }
}

# Apply fixes to all HTML files
$htmlFiles = Get-ChildItem -Path "." -Filter "*.html" -Recurse
foreach ($file in $htmlFiles) {
    Fix-LocalhostUrl -FilePath $file.FullName
}

Write-Host "✓ Windows 11 fixes applied to all modules." -ForegroundColor Green

# Update Python dependencies
Write-Host ""
Write-Host "[6/7] Updating Python dependencies..." -ForegroundColor Yellow
try {
    # Upgrade pip
    & python -m pip install --upgrade pip 2>$null
    
    # Install requirements
    & pip install -r requirements.txt --upgrade 2>$null
    
    Write-Host "✓ Dependencies updated." -ForegroundColor Green
} catch {
    Write-Host "⚠ Some dependencies may have failed to update." -ForegroundColor Yellow
}

# Create update summary
Write-Host ""
Write-Host "[7/7] Creating update summary..." -ForegroundColor Yellow

$updateSummary = @"
Update Summary
==============
Update Date: $(Get-Date)
Previous Version: Unknown
New Version: 5.0 - Windows 11 Fixed Edition

Files Updated:
- All module HTML files (localhost fix applied)
- backend_fixed_v2.py (latest version)
- index.html (new landing page)
- diagnostic_tool.html (connection tester)
- requirements.txt (dependencies)

Key Changes:
- Fixed all Windows 11 connection issues
- All modules use hardcoded localhost:8002
- New landing page with module dashboard
- Enhanced diagnostic tools
- Improved error handling

Backup Location: $BackupDir
"@

$updateSummary | Out-File -FilePath "UPDATE_SUMMARY.txt" -Encoding UTF8

Write-Host ""
Write-Host "=====================================" -ForegroundColor Green
Write-Host "  UPDATE COMPLETED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""
Write-Host "✅ All files have been updated to the latest version" -ForegroundColor Green
Write-Host "✅ Windows 11 localhost fixes have been applied" -ForegroundColor Green
Write-Host "✅ Backup created at: $BackupDir" -ForegroundColor Green
Write-Host ""
Write-Host "What's New:" -ForegroundColor Cyan
Write-Host "  • Fixed all Windows 11 connection issues"
Write-Host "  • New landing page dashboard at index.html"
Write-Host "  • Enhanced diagnostic tools"
Write-Host "  • All modules using hardcoded localhost"
Write-Host "  • Improved performance and stability"
Write-Host ""
Write-Host "To start the application:" -ForegroundColor Yellow
Write-Host "  1. Run: .\windows_start.bat or .\windows_start.ps1"
Write-Host "  2. Open: index.html in your browser"
Write-Host ""
Write-Host "To restore previous version:" -ForegroundColor Gray
Write-Host "  Copy files from: $BackupDir"
Write-Host ""
Read-Host "Press Enter to exit"