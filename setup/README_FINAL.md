# BytePulse Setup

**One-click setup. Auto-elevates. Auto-registers. Just restart.**

No manual steps. No terminal commands. No README hunting after setup.

---

## 🚀 Quick Start

### For Users (Clone & Run)

```powershell
git clone https://github.com/mosesamwoma/BytePulse.git
cd BytePulse
python setup/setup_bytepulse.py
```

Or just **double-click**: `setup\setup_bytepulse.bat`

**Then:**
1. Click "Yes" on UAC prompt (if appears)
2. Wait for setup to finish
3. **Restart your PC**
4. BytePulse starts automatically ✅

---

## 📋 What Gets Installed

During setup, these happen automatically:

| Step | What | Status |
|------|------|--------|
| 1 | Check Python 3.7+ | ✅ Auto-checked |
| 2 | Install dependencies | ✅ Auto-installed |
| 3 | Create data/ logs/ folders | ✅ Auto-created |
| 4 | Initialize SQLite database | ✅ Auto-initialized |
| 5 | Check admin rights | ✅ Auto-elevated if needed |
| 6 | Register Task Scheduler tasks | ✅ Auto-registered |
| 7 | Create launcher shortcut | ✅ Auto-created |
| 8 | Verify all files | ✅ Auto-verified |

**No manual setup needed. Everything is automatic.**

---

## 🔧 Setup Methods

### Method 1: Python (Recommended)

**Run from PowerShell:**
```powershell
cd C:\path\to\BytePulse
python setup/setup_bytepulse.py
```

**What happens:**
- Auto-elevates to Administrator (if needed)
- Runs all 8 steps with colored output
- Asks to launch BytePulse at the end
- Registers auto-startup tasks

### Method 2: Batch (Windows Native)

**Double-click:**
```
setup\setup_bytepulse.bat
```

**What happens:**
- Same as Python method
- Auto-elevates to Administrator
- No PowerShell needed
- Colored output and progress bars

---

## 📖 After Setup

### Auto-Startup (Already Registered)

BytePulse will start automatically on next login.

**To verify:**
1. Restart your PC
2. Look for BytePulse icon in system tray (bottom-right)
3. Right-click it to see menu

### Manual Launch

If you want to start BytePulse without restarting:

```powershell
launch_bytepulse.bat
```

Or from PowerShell:
```powershell
pythonw.exe src\tray.py
pythonw.exe src\tracker.py
```

### Using BytePulse

1. **System tray icon** appears in bottom-right corner
2. **Right-click** the icon for menu:
   - **Status** — Shows if tracker is running
   - **Open Dashboard** — View usage stats (http://localhost:8501)
   - **Stop Tracker** — Stop background monitoring
   - **Quit** — Close everything

3. **Dashboard** shows:
   - Daily/Weekly/Monthly usage
   - Hourly heatmap
   - 7-day forecast
   - Anomaly alerts
   - Data cap progress

---

## 📁 File Locations

All data saved automatically in `data/` folder:

```
BytePulse/
├── data/
│   ├── usage_log.csv        ← Session data (CSV)
│   ├── usage_log.json       ← Session data (JSON)
│   ├── bytepulse.db         ← SQLite database
│   └── tracker.log          ← Activity log
├── logs/
│   └── (application logs)
├── setup/
│   ├── README.md            ← This file
│   ├── setup_bytepulse.py   ← Python setup
│   └── setup_bytepulse.bat  ← Batch setup
├── launch_bytepulse.bat     ← Quick launcher
├── src/
│   ├── tray.py              ← System tray icon
│   ├── tracker.py           ← WiFi monitoring
│   ├── alerts.py            ← Data cap alerts
│   └── ... (other files)
└── ... (other files)
```

---

## ⚙️ Task Scheduler

Two tasks are registered automatically:

| Task | Runs | Purpose |
|------|------|---------|
| `BytePulse-Tray` | At login | System tray icon |
| `BytePulse-Tracker` | At login (10s delay) | WiFi tracking |

**Both:**
- Auto-start on every login
- Run with admin privileges
- Run in background (no window)
- Continue if on battery
- Allow multiple instances

**To verify tasks are registered:**
```powershell
Get-ScheduledTask -TaskName "BytePulse-Tray"
Get-ScheduledTask -TaskName "BytePulse-Tracker"
```

Both should show `State: Ready`

---

## 🆘 Troubleshooting

### Setup shows "Administrator Privileges Required"
**This is normal!** 
- Click Yes on the UAC prompt
- Setup continues automatically
- Only happens once

### "Python not found"
**Solution:**
1. Download Python 3.11 from [python.org](https://www.python.org/downloads/)
2. Run installer
3. **Check "Add Python to PATH"** ← Important!
4. Finish installation
5. Run setup again

### Setup fails with "Access Denied"
**Solution:**
1. Close the setup window
2. Right-click setup script
3. Select "Run as Administrator"
4. Click Yes on UAC prompt
5. Try again

### Tray icon doesn't appear after restart
**Check:**
1. Is PC actually restarted? (Not just logged out)
2. Check system tray — click `^` arrow to see hidden icons
3. Check `data/tracker.log` for errors
4. Make sure connected to WiFi (tracker only monitors WiFi)

**If still not working:**
- Open Task Scheduler (Win + S → Task Scheduler)
- Look for "BytePulse-Tray" and "BytePulse-Tracker"
- Right-click each → "Run" to test manually

### No data appearing in dashboard
**Check:**
1. Are you connected to WiFi? (Tracker only monitors WiFi)
2. Wait 30+ minutes (first data arrives after 30 minutes)
3. Check `data/usage_log.csv` exists
4. Look at `data/tracker.log` for errors

### Want to disable auto-startup
**Remove Task Scheduler tasks:**
```powershell
# Run as Administrator
Unregister-ScheduledTask -TaskName "BytePulse-Tray" -Confirm:$false
Unregister-ScheduledTask -TaskName "BytePulse-Tracker" -Confirm:$false
```

### Want to re-register tasks (if corrupted)
```powershell
# Run as Administrator
python setup/setup_bytepulse.py
```

Or just run setup again — it will update existing tasks.

---

## 🎯 User Experience Flow

### First-Time User

```
1. Clone repo
   ↓
2. Run: python setup/setup_bytepulse.py
   ↓
3. Click Yes on UAC (auto-elevation)
   ↓
4. Wait ~1-2 minutes (dependencies install)
   ↓
5. Setup asks: "Launch BytePulse now? (y/n)"
   ↓
6. Choose y or n
   ↓
7. Restart PC (or launch manually)
   ↓
8. BytePulse starts automatically
   ↓
9. System tray icon appears
   ↓
10. Right-click icon for menu
```

### Existing User

```
1. Open launch_bytepulse.bat
   ↓
2. Tray icon appears
   ↓
3. Tracker starts in background
   ↓
4. Right-click tray for options
```

---

## 📊 Dashboard Features

After 30 minutes of tracking, view stats at `http://localhost:8501`

**Daily View:**
- Hourly usage heatmap
- 7-day forecast (with confidence bands)
- Anomaly detection
- Data cap progress

**Weekly View:**
- Weekly usage trends
- Peak days

**Monthly View:**
- Monthly usage summary
- Monthly cap progress

---

## 🔐 Privacy & Security

✅ **100% Local**
- No cloud upload
- No data collection
- No tracking
- No subscriptions
- Your data stays on your computer

✅ **Admin-Only Tasks**
- Task Scheduler jobs run with admin rights
- Secure startup registration
- Only your user account can see tasks

✅ **Silent Operation**
- No visible window
- No notifications (except data cap alerts)
- Minimal resource usage

---

## 📝 Configuration

To customize BytePulse, edit these files:

**Change WiFi monitoring interval:**
```python
# src/tracker.py, line ~15
POLL_INTERVAL = 5  # seconds between checks
AUTO_SAVE_INTERVAL = 1800  # 30 minutes
```

**Change data cap alerts:**
```python
# src/alerts.py, line ~10
CAP_MB = 10240  # 10 GB daily cap
WARN_THRESHOLD = 0.8  # Alert at 80%
```

Then restart BytePulse.

---

## 🐛 Getting Help

**Check logs:**
```powershell
cat data/tracker.log
```

**Verify database:**
```powershell
sqlite3 data/bytepulse.db "SELECT COUNT(*) FROM sessions;"
```

**Report issues:**
- GitHub: [github.com/mosesamwoma/BytePulse/issues](https://github.com/mosesamwoma/BytePulse/issues)

---

## 🎓 For Developers

Want to customize BytePulse?

**Project structure:**
```
src/
├── tray.py           — System tray icon + menu
├── tracker.py        — WiFi session monitoring
├── alerts.py         — Data cap notifications
├── analyzer.py       — Data analysis
├── anomaly.py        — Anomaly detection
└── forecaster.py     — 7-day forecasting

database/
└── database.py       — SQLite operations

app.py                — Streamlit dashboard
```

**Key entry points:**
- `src/tray.py:run_tray()` — Starts tray icon
- `src/tracker.py:track_usage()` — Starts tracking
- `app.py` — Dashboard (run with `streamlit run app.py`)

---

## 📄 License

MIT License — See LICENSE file

---

<div align="center">
<strong>Built for Windows • No cloud • Your data stays yours</strong>

<sub>
Questions? Check the GitHub repo or open an issue.
</sub>
</div>
