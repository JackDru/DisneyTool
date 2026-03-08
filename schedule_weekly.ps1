# Schedule Elias scraper + scorer to run every Monday at 4:00 AM
# Run this script once (as Administrator optional; current user is fine):
#   PowerShell -ExecutionPolicy Bypass -File schedule_weekly.ps1

$TaskName = "EliasWeeklyScrape"
$ScriptDir = $PSScriptRoot
$BatPath = Join-Path $ScriptDir "run_weekly.bat"

if (-not (Test-Path $BatPath)) {
    Write-Error "run_weekly.bat not found at $BatPath"
    exit 1
}

# Remove existing task if present
$existing = schtasks /query /tn $TaskName 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "Removing existing task '$TaskName'..."
    schtasks /delete /tn $TaskName /f
}

# Create task: every Monday at 4:00 AM (current user, run when logged on)
schtasks /create /tn $TaskName /tr "`"$BatPath`"" /sc weekly /d MON /st 04:00 /f
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to create scheduled task."
    exit 1
}

Write-Host "Scheduled task created: $TaskName"
Write-Host "  Runs: Every Monday at 4:00 AM"
Write-Host "  Action: $BatPath"
Write-Host ""
Write-Host "To run manually: schtasks /run /tn $TaskName"
Write-Host "To remove:       schtasks /delete /tn $TaskName /f"
