# BytePulse

> A lightweight WiFi usage tracker that silently monitors, logs, and helps you understand your real-time data consumption — session by session.

---

## What It Does

BytePulse runs silently in the background on Windows. Every time you connect to WiFi, it starts tracking your data usage and saves sessions to a CSV file at regular intervals — no cloud, no subscriptions, just clean local data.

---

## Features

- Automatic WiFi detection and session tracking
- Logs bytes sent, received, total usage, and duration per session
- Configurable save interval (default: 30 minutes)
- Runs invisibly on Windows startup via Startup folder
- Raw CSV output — ready for analysis, visualization, or aggregation
- Handles interface changes, counter rollovers, and disconnects gracefully

---

## Requirements

Before you start, make sure you have the following installed:

- Windows 10 or 11
- [Python 3.8+](https://www.python.org/downloads/) — during installation, check **"Add Python to PATH"**
- Git — [download here](https://git-scm.com/downloads)

---

## Getting Started

### 1. Clone the repo

Open PowerShell or Command Prompt and run:
```bash
git clone https://github.com/mosesamwoma/BytePulse.git
cd BytePulse
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up your launcher files

BytePulse uses two files to run — you need to create them from the provided examples.

**Step 1 — Create `start_tracker.bat`:**

- Copy `start_tracker.example.bat` and rename it to `start_tracker.bat`
- Open it in Notepad and replace `C:\path\to\BytePulse` with your actual folder path

Example:
```bat
cd /d "C:\Users\YourName\Documents\BytePulse"
```

**Step 2 — Create `run_hidden.vbs`:**

- Copy `run_hidden.example.vbs` and rename it to `run_hidden.vbs`
- Open it in Notepad and replace `C:\path\to\BytePulse` with your actual folder path

Example:
```vbs
WshShell.Run chr(34) & "C:\Users\YourName\Documents\BytePulse\start_tracker.bat" & chr(34), 0
```

### 4. Run manually (to test)

Double-click `start_tracker.bat` or run in PowerShell:
```powershell
.\start_tracker.bat
```

You should see:
```
Starting WiFi tracker...
[16:34:51] Tracker started (30-minute auto-save)
[16:34:51] Connected: Wi-Fi
```

After 30 minutes, check `data/usage_log.csv` — a row should appear.

### 5. Run silently on startup (recommended)

To make BytePulse start automatically every time you log into Windows with no visible window:

1. Press `Win + R`, type `shell:startup`, hit Enter
2. Copy `run_hidden.vbs` into the folder that opens
3. Restart your PC

That's it — BytePulse will now run silently in the background every time you log in.

To confirm it's running after restart:
```powershell
Get-Process python
```

If Python appears in the list, the tracker is active.

---

## CSV Output

All data is saved to `data/usage_log.csv`:

| start_time | end_time | duration_minutes | bytes_sent | bytes_received | total_bytes | usage_MB |
|---|---|---|---|---|---|---|
| 2026-03-17 16:34:51 | 2026-03-17 16:35:56 | 1.0873 | 886606 | 1629334 | 2515940 | 2.3993 |

A new row is added every 30 minutes while connected, and immediately on disconnect or shutdown.

---

## Logs

Activity is logged to `data/tracker.log`:
```
2026-03-17 16:34:51 - Tracker started (30-minute auto-save)
2026-03-17 16:34:51 - Connected: Wi-Fi
2026-03-17 16:35:08 - Auto-saving (30 min)
2026-03-17 16:35:08 - Saved: 34.299827 MB in 30.0000 mins
```

---

## Configuration

Open `src/tracker.py` and adjust these two values at the top:
```python
POLL_INTERVAL = 5          # How often to check WiFi status in seconds
AUTO_SAVE_INTERVAL = 1800  # How often to save a session — 1800 = 30 minutes
```

To test with a shorter interval, set `AUTO_SAVE_INTERVAL = 60` for 1-minute saves.

---

## Stopping the Tracker

To stop the tracker, open Task Manager → find the `python` process → End Task.

Or in PowerShell:
```powershell
Stop-Process -Name python -Force
```

---

## Roadmap

- [ ] Daily / weekly / monthly usage summaries
- [ ] Usage visualization dashboard
- [ ] Data cap alerts
- [ ] Export to Excel

---

## Author

**Moses Amwoma** — [@AmwomaMoses](https://twitter.com/AmwomaMoses) · [GitHub](https://github.com/mosesamwoma)

---