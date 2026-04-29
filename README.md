# BytePulse

**See exactly how your internet data is used — locally, silently, and privately.**

Track every WiFi session, detect heavy usage, and visualize patterns with zero cloud involvement.

---

## Overview

BytePulse runs silently in the background. Every time you connect to WiFi, it starts tracking your data usage and saves sessions to a local CSV, JSON, and SQLite database at regular intervals.

No cloud. No subscriptions. No tracking. Just clean local data that belongs to you.

**What it tracks:**

| Field | Description |
|---|---|
| `start_time` / `end_time` | Session timestamps |
| `duration_minutes` | How long you were connected |
| `bytes_sent` / `bytes_received` | Raw transfer counts |
| `usage_MB` | Total data used per session |

---

## Features

- **Silent background tracking** — runs at login via Windows Task Scheduler, no terminal window
- **Triple-format logging** — every session saved to CSV, JSON, and SQLite simultaneously
- **Atomic writes** — temp-file-swap pattern prevents data corruption on crash
- **Fault tolerance** — if CSV is locked (e.g. open in Excel), data falls back to a `.pending` file and merges on next run
- **System tray icon** — right-click to open dashboard, stop tracker, or quit
- **Streamlit dashboard** — daily, weekly, and monthly views with hourly heatmap
- **Anomaly detection** — flags sessions with unusually high usage via Z-score
- **Data cap alerts** — Windows toast notifications at 80% and 100% of your daily cap
- **7-day usage forecast** — Prophet-powered time series forecasting

---

## Requirements

- Windows 10 or 11
- [Python 3.11](https://www.python.org/downloads/release/python-3110/) — check **"Add Python to PATH"** during install

> ⚠️ **Use Python 3.11 specifically.** `psutil` has known compatibility issues with Python 3.12+. Using any other version may cause install or runtime errors.

---

## Getting Started

> 💡 **New to this?** Follow every step in order. Don't skip anything — each step builds on the last.

---

### Step 1 — Check your Python version

Before doing anything else, confirm you have the right Python version installed.

Open PowerShell (`Win + S` → type `powershell` → press Enter) and run:

```powershell
python --version
```

You should see:

```
Python 3.11.x
```

If you see `3.12`, `3.13`, or anything other than `3.11`, you need to install Python 3.11 first. Download it from [python.org](https://www.python.org/downloads/release/python-3110/). During installation, **check the box that says "Add Python to PATH"** — this is important.

After installing, close PowerShell and reopen it, then run `python --version` again to confirm.

---

### Step 2 — Clone the repository

This downloads the BytePulse code to your computer.

In PowerShell, run:

```bash
git clone https://github.com/mosesamwoma/BytePulse.git
cd BytePulse
```

After running `cd BytePulse`, your terminal is now inside the BytePulse folder. All future commands assume you are in this folder.

> 💡 **Don't have Git?** Download it from [git-scm.com](https://git-scm.com/download/win), install it with default settings, then reopen PowerShell and try again.

---

### Step 3 — Create a virtual environment

A virtual environment is an isolated Python workspace for BytePulse. It keeps BytePulse's dependencies separate from other Python projects on your system so nothing conflicts.

Run:

```powershell
python -m venv venv
venv\Scripts\activate
```

After the second command, your terminal prompt will change to start with `(venv)`, like this:

```
(venv) PS C:\Users\YourName\BytePulse>
```

That `(venv)` prefix means the virtual environment is active. **You must see this before running any further commands.**

> ⚠️ **Every time you open a new terminal window**, you need to navigate to the BytePulse folder and run `venv\Scripts\activate` again before working on BytePulse. The `(venv)` prefix does not persist between sessions.

---

### Step 4 — Install dependencies

With the virtual environment active (you see `(venv)` in your prompt), install all required packages.

**Recommended:**

```bash
pip install -e .
```

**Alternative (if the above fails):**

```bash
pip install -r requirements.txt
```

This will download and install several packages — it may take a minute or two. You'll see a lot of output scrolling past; that's normal. Wait until you get your prompt back.

> 💡 The `-e` flag in the first option installs BytePulse in "editable" mode, meaning any code changes you make take effect immediately without reinstalling.

---

### Step 5 — Configure the launcher

BytePulse uses a `.bat` file to start the tracker. You need to tell it where your files are.

**5a.** In File Explorer, navigate to your BytePulse folder. Click the address bar at the top — it will show your full path, something like:

```
C:\Users\YourName\BytePulse
```

Copy that path. You'll need it in a moment.

**5b.** In the BytePulse folder, find the file called `start_tracker.example.bat`. Make a copy of it and rename the copy to `start_tracker.bat`.

> 💡 **Can't see the `.bat` extension?** Open any folder → click the **View** tab at the top → check **File name extensions**. This prevents accidentally saving the file as `start_tracker.bat.bat`.

**5c.** Right-click `start_tracker.bat` → **Open with** → **Notepad**.

Find these two lines near the top:

```bat
cd /d "C:\Users\YourName\BytePulse"
set PYTHONW=C:\Users\YourName\BytePulse\venv\Scripts\pythonw.exe
```

Replace `C:\Users\YourName\BytePulse` with the actual path you copied in step 5a. For example, if your path is `C:\Users\Moses\Documents\BytePulse`, the lines should become:

```bat
cd /d "C:\Users\Moses\Documents\BytePulse"
set PYTHONW=C:\Users\Moses\Documents\BytePulse\venv\Scripts\pythonw.exe
```

Save the file and close Notepad.

---

### Step 6 — Run manually to test

Before setting up automatic startup, make sure everything works by running BytePulse manually.

In PowerShell (with `(venv)` active):

```powershell
.\start_tracker.bat
```

A BytePulse icon should appear in your system tray (the small icons in the bottom-right corner of your taskbar). If you don't see it, click the `^` arrow in the taskbar to reveal hidden tray icons.

**Verify the tracker is actually running** — don't wait 30 minutes to find out it crashed:

```powershell
Get-Process pythonw
```

You should see exactly **two** `pythonw` processes listed (one for the tracker, one for the tray icon). If you see zero, check the [Troubleshooting](#troubleshooting) section.

After 30 minutes, a row of data should appear in `data/usage_log.csv`. You can also check the database directly:

```powershell
python -c "import sqlite3; conn = sqlite3.connect('data/bytepulse.db'); print(conn.execute('SELECT COUNT(*) FROM sessions').fetchone()); conn.close()"
```

If it prints `(1,)` or higher, your data is being saved correctly. If it prints `(0,)` after 30 minutes, check [Troubleshooting](#troubleshooting).

---

### Step 7 — Enable silent startup (optional)

This step makes BytePulse start automatically every time you log into Windows, with no visible window. This is optional but recommended for continuous tracking.

> ⚠️ This step requires running PowerShell as Administrator. The commands register tasks with Windows Task Scheduler.

**7a.** First, get the exact path to `pythonw.exe` inside your virtual environment. In PowerShell, run:

```powershell
(Get-Item "venv\Scripts\pythonw.exe").FullName
```

Copy the output. It will look something like:

```
C:\Users\Moses\Documents\BytePulse\venv\Scripts\pythonw.exe
```

**7b.** Open a new PowerShell window **as Administrator**: press `Win + S`, type `powershell`, right-click the result, and select **Run as administrator**. Click Yes on the prompt.

**7c.** In the Administrator PowerShell window, paste the block below. Before pasting, update the two lines at the top (`$base` and `$pythonw`) with your actual paths from steps 5a and 7a:

```powershell
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
```

You should see two green checkmarks confirming the tasks were registered.

**7d.** Confirm both tasks are ready:

```powershell
Get-ScheduledTask -TaskName "BytePulse-Tracker"
Get-ScheduledTask -TaskName "BytePulse-Tray"
```

Both should show `State: Ready`. If they do, restart your PC — BytePulse will now start automatically at every login.

---

### Step 8 — Migrate existing data (if applicable)

If you have existing CSV data from a previous run and want to sync it to the SQLite database, run this once:

```bash
python -m scripts.migrate_csv_to_db
```

You can skip this step if you're setting up BytePulse for the first time.

---

## Dashboard

```bash
streamlit run app.py
```

Or right-click the system tray icon → **Open Dashboard**. Opens at `http://localhost:8501`.

Switch between **Daily**, **Weekly**, and **Monthly** views from the sidebar. The **hourly heatmap**, **7-day forecast**, **anomaly detection**, and **data cap** sections are only visible in the Daily view.

![Dashboard overview](assets/1.png)

![Peak hours and detailed data](assets/3.png)

---

## ML — 7-Day Usage Forecast

BytePulse uses **Prophet** (Meta's time series forecasting library) to predict your WiFi usage for the next 7 days.

**How it works:**
- Aggregates your session data into daily totals
- Fits a Prophet model with weekly seasonality
- Predicts `usage_MB` for the next 7 days with upper and lower confidence bounds

**What you need:** at least 10 days of recorded data before the forecast section appears.

**What you get:**
- A line chart showing predicted daily usage with a confidence band
- A table with `Day`, `Predicted (MB)`, `Lower (MB)`, and `Upper (MB)` per day

The model retrains automatically every time the dashboard loads — no manual steps needed.

![7-Day Usage Forecast](assets/6.png)

---

## Configuration

Edit these constants in `src/tracker.py`:

```python
POLL_INTERVAL      = 5     # seconds between WiFi checks
AUTO_SAVE_INTERVAL = 1800  # seconds between auto-saves (1800 = 30 min)
```

Edit these constants in `src/alerts.py`:

```python
CAP_MB         = 10240  # daily data cap in MB (10240 = 10 GB)
WARN_THRESHOLD = 0.8    # alert at 80% usage
```

> 💡 These are hardcoded by design — no config file needed. Just edit and save; changes take effect on next run.

---

## Output Files

All three files live in `data/` and stay in sync — if one write fails, the others preserve the data.

### `data/usage_log.csv`

| start_time | end_time | duration_minutes | bytes_sent | bytes_received | total_bytes | usage_MB |
|---|---|---|---|---|---|---|
| 2026-03-17 16:34:51 | 2026-03-17 16:35:56 | 1.0873 | 886606 | 1629334 | 2515940 | 2.3993 |

> ⚠️ **Do not open `usage_log.csv` in Excel while the tracker is running.** This locks the file and causes save failures. To view data safely, copy it first:
> ```powershell
> copy "data\usage_log.csv" "%USERPROFILE%\Desktop\usage_copy.csv"
> ```

### `data/usage_log.json`

```json
[
  {
    "start_time": "2026-03-17 16:34:51",
    "end_time": "2026-03-17 16:35:56",
    "duration_minutes": 1.0873,
    "bytes_sent": 886606,
    "bytes_received": 1629334,
    "total_bytes": 2515940,
    "usage_MB": 2.3993
  }
]
```

### `data/bytepulse.db`

This is a SQLite database with a `sessions` table.

### Querying the Database

BytePulse stores all session data in a local SQLite database at `data/bytepulse.db`. You can query it directly from the terminal:

```powershell
sqlite3 data\bytepulse.db
```

Useful queries:

```sql
SELECT * FROM sessions LIMIT 10;
SELECT COUNT(*) FROM sessions;
SELECT SUM(usage_MB) FROM sessions;
SELECT date(start_time), SUM(usage_MB) FROM sessions GROUP BY date(start_time);
SELECT * FROM sessions WHERE usage_MB > 100;
```

To exit:

```sql
.quit
```

> 💡 You can also open `data/bytepulse.db` in [DB Browser for SQLite](https://sqlitebrowser.org/) for a visual interface.

---

## Stopping the Tracker

Right-click the system tray icon → **Stop Tracker** or **Quit**.

Or force-stop from PowerShell:

```powershell
Stop-Process -Name pythonw -Force
```

To remove the Task Scheduler entries entirely:

```powershell
Unregister-ScheduledTask -TaskName "BytePulse-Tracker" -Confirm:$false
Unregister-ScheduledTask -TaskName "BytePulse-Tray"    -Confirm:$false
```

---

## Troubleshooting

**`Get-Process pythonw` shows nothing after running `start_tracker.bat`**
- Make sure your virtual environment is activated: `venv\Scripts\activate`
- Check that the paths in `start_tracker.bat` match your actual BytePulse folder
- Run `start_tracker.bat` directly by double-clicking it and look for any error message in the terminal

**`psutil` install fails or crashes at runtime**
- Confirm you're on Python 3.11: `python --version`
- If you see 3.12 or higher, install 3.11 from [python.org](https://www.python.org/downloads/release/python-3110/) and recreate the virtual environment

**Task Scheduler tasks registered but BytePulse doesn't start on login**
- Confirm both tasks show `State: Ready` in Task Scheduler (`Win + S` → Task Scheduler)
- Make sure the `pythonw.exe` path in the task points to `venv\Scripts\pythonw.exe` inside your BytePulse folder
- Check that you ran the registration script as Administrator

**No data after 30 minutes**
- Confirm you're connected to WiFi (BytePulse only tracks WiFi, not Ethernet)
- Check the `data/` folder exists — create it manually if not: `mkdir data`
- Look for a `data/usage_log.pending` file — this means the CSV was locked during a save

**Dashboard shows "Not enough data to forecast"**
- The forecast requires at least 10 days of data. Keep the tracker running and check back later.

**Tray icon doesn't appear**
- Check Task Manager for `pythonw` processes — if they exist, the icon may be hidden in the system tray overflow area (click the `^` arrow in the taskbar)

---

## Limitations

- Windows 10/11 only
- WiFi only — Ethernet and mobile hotspot sessions are not tracked
- Total usage only — no per-app or per-SSID breakdown
- Requires Python 3.11 specifically
- Opening `usage_log.csv` in Excel while the tracker runs may cause save failures

---

## Roadmap

- [ ] Per-SSID usage breakdown
- [ ] ISP billing cycle alignment
- [ ] Cross-platform portability (macOS / Linux)

---

## Contributing

1. Fork the repo and clone it
2. Create a branch: `git checkout -b feature/your-feature`
3. Make your changes and commit: `git commit -m "describe change"`
4. Push: `git push origin feature/your-feature`
5. Open a Pull Request targeting `main` on `mosesamwoma/BytePulse`

---

## Support This Project

If BytePulse saved you from blowing your data cap, consider:

- Starring the repository
- Forking it to contribute
- Opening issues or suggesting features

---

<div align="center">
<sub>Built for Windows · No cloud · Your data stays yours</sub>
</div>