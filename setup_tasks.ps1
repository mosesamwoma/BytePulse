# ── UPDATE THESE TWO LINES ───────────────────────────────────────────────────
$base    = "C:\Users\YourName\BytePulse"                               # ← your BytePulse folder
$pythonw = "C:\Users\YourName\BytePulse\venv\Scripts\pythonw.exe"     # ← from step 7a
# ─────────────────────────────────────────────────────────────────────────────

if (-not (Test-Path $pythonw)) { Write-Error "pythonw.exe not found: $pythonw"; exit 1 }
if (-not (Test-Path $base))    { Write-Error "BytePulse folder not found: $base"; exit 1 }

$settingsTray    = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Seconds 0) -MultipleInstances IgnoreNew
$settingsTracker = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Seconds 0) -MultipleInstances IgnoreNew

$trigger = New-ScheduledTaskTrigger -AtLogOn
Register-ScheduledTask -TaskName "BytePulse-Tray" `
    -Action (New-ScheduledTaskAction -Execute $pythonw -Argument "`"$base\src\tray.py`"" -WorkingDirectory $base) `
    -Trigger $trigger -Settings $settingsTray -RunLevel Highest -Force
Write-Host "✅ BytePulse-Tray registered"

$triggerTracker       = New-ScheduledTaskTrigger -AtLogOn
$triggerTracker.Delay = "PT10S"
Register-ScheduledTask -TaskName "BytePulse-Tracker" `
    -Action (New-ScheduledTaskAction -Execute $pythonw -Argument "`"$base\src\tracker.py`"" -WorkingDirectory $base) `
    -Trigger $triggerTracker -Settings $settingsTracker -RunLevel Highest -Force
Write-Host "✅ BytePulse-Tracker registered (10s delay)"