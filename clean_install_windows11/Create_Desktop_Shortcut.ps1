# PowerShell script to create a desktop shortcut
# Run this once to create the shortcut on your desktop

$DesktopPath = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = "$DesktopPath\Stock Tracker.lnk"

# Create shortcut object
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)

# Set shortcut properties
$Shortcut.TargetPath = "C:\StockTrack\Complete_Stock_Tracker_Windows11\START_STOCK_TRACKER.bat"
$Shortcut.WorkingDirectory = "C:\StockTrack\Complete_Stock_Tracker_Windows11"
$Shortcut.IconLocation = "C:\Windows\System32\shell32.dll,13"  # Money icon
$Shortcut.Description = "Launch Complete Stock Tracker"
$Shortcut.WindowStyle = 1

# Save the shortcut
$Shortcut.Save()

Write-Host "Desktop shortcut created successfully!" -ForegroundColor Green
Write-Host "Look for 'Stock Tracker' on your Desktop" -ForegroundColor Yellow