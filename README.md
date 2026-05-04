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

### Step 5 — Run manual tests

Before setting up automatic startup, make sure everything works by running BytePulse manually.

In PowerShell (with `(venv)` active):

```powershell
python src\tray.py
python src\tracker.py
```

A BytePulse icon should appear in your system tray (the small icons in the bottom-right corner of your taskbar). If you don't see it, click the `^` arrow in the taskbar to reveal hidden tray icons.

**Verify the tracker is actually running**:

```powershell
Get-Process python
```

You should see Python processes running. After 30 minutes, a row of data should appear in `data/usage_log.csv`.

---

### Step 6 — Enable silent startup (optional)

This step makes BytePulse start automatically every time you log into Windows, with no visible window. This is optional but recommended for continuous tracking.

See [Setup Guide](./setup/SETUP.md) for detailed Task Scheduler registration instructions.

---

### Step 7 — Migrate existing data (if applicable)

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

**Tracker doesn't start after running setup**
- Check `data/tracker.log` for error messages
- Make sure Python 3.11 is installed: `python --version`
- Verify Task Scheduler tasks are registered: `Get-ScheduledTask -TaskName "BytePulse-*"`

**`psutil` install fails or crashes at runtime**
- Confirm you're on Python 3.11: `python --version`
- If you see 3.12 or higher, install 3.11 from [python.org](https://www.python.org/downloads/release/python-3110/)

**No data after 30 minutes**
- Confirm you're connected to WiFi (BytePulse only tracks WiFi, not Ethernet)
- Check `data/tracker.log` for errors
- Manually run the tracker to see real-time output: `python src/tracker.py`

**Dashboard shows "Not enough data to forecast"**
- The forecast requires at least 10 days of data. Keep the tracker running and check back later.

**Tray icon doesn't appear**
- Check Task Manager for Python processes — if they exist, the icon may be hidden in the system tray overflow area (click the `^` arrow in the taskbar)

---

## Limitations

- Windows 10/11 only
- WiFi only — Ethernet and mobile hotspot sessions are not tracked
- Total usage only — no per-app or per-SSID breakdown
- Requires Python 3.11 specifically

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