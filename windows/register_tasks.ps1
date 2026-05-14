# BytePulse Task Scheduler Registration
# Run as Administrator to register auto-startup tasks
# Usage: powershell -ExecutionPolicy Bypass -File register_tasks.ps1

# ── UPDATE THESE TWO LINES ───────────────────────────────────────────────────
$base    = "C:\Users\YourName\Documents\projects\BytePulse\windows"  # ← your windows/ folder
$pythonw = "C:\Users\YourName\Documents\projects\BytePulse\windows\venv\Scripts\pythonw.exe"  # ← pythonw in venv
# ─────────────────────────────────────────────────────────────────────────────

# Verify paths exist
if (-not (Test-Path $pythonw)) {
    Write-Error "pythonw.exe not found at: $pythonw"
    exit 1
}

if (-not (Test-Path $base)) {
    Write-Error "BytePulse folder not found at: $base"
    exit 1
}

Write-Host ""
Write-Host "=========================================================================="
Write-Host "BytePulse Task Scheduler Registration"
Write-Host "=========================================================================="
Write-Host ""

# Task settings (common to both)
$settingsTray    = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Seconds 0) -MultipleInstances IgnoreNew
$settingsTracker = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Seconds 0) -MultipleInstances IgnoreNew

# Register BytePulse-Tray
Write-Host "[1/2] Registering BytePulse-Tray..."
$trigger = New-ScheduledTaskTrigger -AtLogOn
$action = New-ScheduledTaskAction -Execute $pythonw -Argument "`"$base\src\tray.py`"" -WorkingDirectory $base
Register-ScheduledTask -TaskName "BytePulse-Tray" -Action $action -Trigger $trigger -Settings $settingsTray -RunLevel Highest -Force | Out-Null
Write-Host "[OK] BytePulse-Tray registered (starts at login)"
Write-Host ""

# Register BytePulse-Tracker
Write-Host "[2/2] Registering BytePulse-Tracker (10 second delay)..."
$trigger = New-ScheduledTaskTrigger -AtLogOn
$trigger.Delay = "PT10S"
$action = New-ScheduledTaskAction -Execute $pythonw -Argument "`"$base\src\tracker.py`"" -WorkingDirectory $base
Register-ScheduledTask -TaskName "BytePulse-Tracker" -Action $action -Trigger $trigger -Settings $settingsTracker -RunLevel Highest -Force | Out-Null
Write-Host "[OK] BytePulse-Tracker registered (starts 10s after login)"
Write-Host ""

# Verify
Write-Host "=========================================================================="
Write-Host "Verification"
Write-Host "=========================================================================="
Write-Host ""
$tray = Get-ScheduledTask -TaskName "BytePulse-Tray" -ErrorAction SilentlyContinue
$tracker = Get-ScheduledTask -TaskName "BytePulse-Tracker" -ErrorAction SilentlyContinue

if ($tray) {
    Write-Host "[OK] BytePulse-Tray: $($tray.State)"
} else {
    Write-Host "[ERROR] BytePulse-Tray not found"
}

if ($tracker) {
    Write-Host "[OK] BytePulse-Tracker: $($tracker.State)"
} else {
    Write-Host "[ERROR] BytePulse-Tracker not found"
}

Write-Host ""
Write-Host "Tasks will start automatically on next login."
Write-Host "To disable: Open Task Scheduler (Win + S -> Task Scheduler) and disable the tasks."
Write-Host ""
