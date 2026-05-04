# BytePulse Setup

One-click setup. Auto-elevates. Auto-registers. Just restart.

---

## Quick Start

```powershell
git clone https://github.com/mosesamwoma/BytePulse.git
cd BytePulse
python setup/setup_bytepulse.py
```

Or double-click: `setup\setup_bytepulse.bat`

Then restart your PC. BytePulse starts automatically.

---

## What Gets Installed

- Check Python 3.7+
- Install dependencies
- Create data/ logs/ folders
- Initialize SQLite database
- Register Task Scheduler tasks
- Create launcher shortcut

Everything is automatic.

---

## After Setup

### Manual Launch

```powershell
launch_bytepulse.bat
```

### Using BytePulse

1. System tray icon appears (bottom-right)
2. Right-click for menu:
   - Status — Check if running
   - Open Dashboard — View stats (http://localhost:8501)
   - Stop Tracker — Stop monitoring
   - Quit — Close everything

---

## Troubleshooting

**Python not found?**
- Download Python 3.11 from [python.org](https://www.python.org/downloads/)
- Check "Add Python to PATH"
- Run setup again

**Setup fails with "Access Denied"?**
- Right-click setup script
- Select "Run as Administrator"
- Try again

**Tray icon doesn't appear?**
- Restart PC (not logout)
- Check system tray arrow
- Check `data/tracker.log` for errors

**No data in dashboard?**
- Wait 30+ minutes for first data
- Make sure WiFi is connected
- Check `data/tracker.log`

**Disable auto-startup?**
```powershell
Unregister-ScheduledTask -TaskName "BytePulse-Tray" -Confirm:$false
Unregister-ScheduledTask -TaskName "BytePulse-Tracker" -Confirm:$false
```

**Check logs:**
```powershell
cat data/tracker.log
```