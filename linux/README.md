# BytePulse

**See exactly how your internet data is used — locally, silently, and privately.**

Track every WiFi session, detect heavy usage, and visualize patterns with zero cloud involvement.

---

## Overview

BytePulse runs silently in the background via systemd. Every time you connect to WiFi, it starts tracking your data usage and saves sessions to a local CSV, JSON, and SQLite database at regular intervals.

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

- **Silent background tracking** — runs via systemd at startup, no terminal window
- **Triple-format logging** — every session saved to CSV, JSON, and SQLite simultaneously
- **Atomic writes** — temp-file-swap pattern prevents data corruption on crash
- **Fault tolerance** — if CSV write fails, data falls back to a `.pending` file and merges on next run
- **System tray icon** — right-click to open dashboard, stop tracker, or quit
- **Streamlit dashboard** — daily, weekly, and monthly views with hourly heatmap
- **Anomaly detection** — flags sessions with unusually high usage via Z-score
- **Data cap alerts** — console alerts at 80% and 100% of your daily cap
- **7-day usage forecast** — Prophet-powered time series forecasting

---

## Requirements

- Linux (Ubuntu 20.04 LTS or newer, Fedora, Debian, or any systemd-based distro)
- [Python 3.11](https://www.python.org/downloads/release/python-3110/)
- systemd (standard on all modern Linux distributions)

> ⚠️ **Use Python 3.11 specifically.** `psutil` has known compatibility issues with Python 3.12+. Using any other version may cause install or runtime errors.

---

## Quick Setup (Alternative)

For one-click automated setup, see [setup/SETUP.md](setup/README.md)

---

## Getting Started

> 💡 **New to this?** Follow every step in order. Don't skip anything — each step builds on the last.

---

### Step 1 — Check your Python version

Before doing anything else, confirm you have the right Python version installed.

Open a terminal and run:

```bash
python3 --version
```

You should see:

```
Python 3.11.x
```

If you see `3.10`, `3.12`, `3.13`, or anything other than `3.11`, you need to install Python 3.11 first. On Ubuntu/Debian:

```bash
sudo apt update
sudo apt install python3.11 python3.11-venv
```

On Fedora/RHEL:

```bash
sudo dnf install python3.11
```

After installing, close the terminal and reopen it, then run `python3.11 --version` again to confirm.

---

### Step 2 — Clone the repository

This downloads the BytePulse code to your computer.

In a terminal, run:

```bash
git clone https://github.com/mosesamwoma/BytePulse.git
cd BytePulse/linux
```

After running `cd BytePulse/linux`, your terminal is now inside the BytePulse Linux folder. All future commands assume you are in this folder.

> 💡 **Don't have Git?** Install it:
> - Ubuntu/Debian: `sudo apt install git`
> - Fedora/RHEL: `sudo dnf install git`

---

### Step 3 — Create a virtual environment

A virtual environment is an isolated Python workspace for BytePulse. It keeps BytePulse's dependencies separate from other Python projects on your system so nothing conflicts.

Run:

```bash
python3.11 -m venv venv
source venv/bin/activate
```

After the second command, your terminal prompt will change to start with `(venv)`, like this:

```
(venv) user@hostname:~/BytePulse/linux$
```

That `(venv)` prefix means the virtual environment is active. **You must see this before running any further commands.**

> ⚠️ **Every time you open a new terminal window**, you need to navigate to the BytePulse folder and run `source venv/bin/activate` again before working on BytePulse. The `(venv)` prefix does not persist between sessions.

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

### Step 5 — Run manually to test

Before setting up automatic startup, make sure everything works by running BytePulse manually.

In a terminal (with `(venv)` active):

```bash
python3 main.py
```

A BytePulse icon should appear in your system tray. If you don't see it, check for it in the tray overflow area or top panel depending on your desktop environment.

**Verify the tracker is actually running:**

```bash
ps aux | grep python3 | grep -v grep
```

You should see at least two `python3` processes (one for the tracker, one for the tray icon). If you see zero, check the [Troubleshooting](#troubleshooting) section.

After 30 minutes, a row of data should appear in `data/usage_log.csv`. You can also check the database directly:

```bash
sqlite3 data/bytepulse.db "SELECT COUNT(*) FROM sessions;"
```

If it prints `1` or higher, your data is being saved correctly. If it prints `0` after 30 minutes, check [Troubleshooting](#troubleshooting).

---

### Step 6 — Enable silent startup (optional)

This step makes BytePulse start automatically every time you boot, with no visible window. This is optional but recommended for continuous tracking.

> ⚠️ This step requires sudo access to register systemd services.

**6a.** Set up the systemd service:

```bash
sudo bash setup_systemd.sh
```

**6b.** Confirm the service is ready:

```bash
systemctl status bytepulse
```

Should show `State: inactive` or `State: active`.

**6c.** Enable auto-start at boot:

```bash
sudo systemctl enable bytepulse
sudo systemctl start bytepulse
```

**6d.** Verify both are working:

```bash
systemctl is-enabled bytepulse
systemctl is-active bytepulse
```

Both should print `enabled` and `active`. If they do, restart your PC — BytePulse will now start automatically at every boot.

---

### Step 7 — Migrate existing data (if applicable)

If you have existing CSV data from a previous run and want to sync it to the SQLite database, run this once:

```bash
python -m shared.scripts.migrate_csv_to_db
```

You can skip this step if you're setting up BytePulse for the first time.

---

## Dashboard

```bash
streamlit run app.py
```

Or right-click the system tray icon → **Open Dashboard**. Opens at `http://localhost:8501`.

Switch between **Daily**, **Weekly**, and **Monthly** views from the sidebar. The **hourly heatmap**, **7-day forecast**, **anomaly detection**, and **data cap** sections are only visible in the Daily view.

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

```bash
sqlite3 data/bytepulse.db
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

Or stop the service:

```bash
sudo systemctl stop bytepulse
```

To remove the systemd entries entirely:

```bash
sudo systemctl disable bytepulse
sudo rm /etc/systemd/system/bytepulse.service
sudo systemctl daemon-reload
```

---

## Troubleshooting

**Virtual environment won't activate**
- Make sure you're in the `BytePulse/linux` folder
- Try: `source venv/bin/activate`
- If that fails, recreate the venv: `rm -rf venv && python3.11 -m venv venv && source venv/bin/activate`

**`psutil` install fails or crashes at runtime**
- Confirm you're on Python 3.11: `python3.11 --version`
- If you see 3.10, 3.12 or higher, install 3.11 from your package manager
- Recreate the virtual environment: `python3.11 -m venv venv`

**Systemd service registered but BytePulse doesn't start on boot**
- Confirm the service is enabled: `systemctl is-enabled bytepulse` (should print `enabled`)
- Check service status: `systemctl status bytepulse`
- View logs: `journalctl -u bytepulse -n 20`

**No data after 30 minutes**
- Confirm you're connected to WiFi: `nmcli device wifi`
- Check that the `data/` folder exists: `ls -la data/`
- Look for a `data/usage_log.pending` file — this means a write failed
- Check logs: `tail data/tracker.log`

**Dashboard shows "Not enough data to forecast"**
- The forecast requires at least 10 days of data. Keep the tracker running and check back later.

**Tray icon doesn't appear**
- Check if the tray process is running: `ps aux | grep tray`
- Check systemd logs: `journalctl -u bytepulse | grep tray`
- Some minimal desktop environments don't support system trays — the tracker will still work; start the dashboard manually with `streamlit run app.py`

---

## Limitations

- Linux only (requires systemd)
- WiFi only — Ethernet and mobile hotspot sessions are not tracked
- Total usage only — no per-app or per-SSID breakdown
- Requires Python 3.11 specifically

---