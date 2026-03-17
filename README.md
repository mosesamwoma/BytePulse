# BytePulse 📡

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

## Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/mosesamwoma/BytePulse.git
cd BytePulse
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run manually
```bash
.\start_tracker.bat
```

### 4. Run silently on startup

Copy `run_hidden.vbs` to your Windows Startup folder:
```
C:\Users\<YourName>\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\
```

The tracker will start automatically and silently every time you log in.

---

## CSV Output

Data is saved to `data/usage_log.csv`:

| start_time | end_time | duration_minutes | bytes_sent | bytes_received | total_bytes | usage_MB |
|---|---|---|---|---|---|---|
| 2026-03-17 16:34:51 | 2026-03-17 16:35:56 | 1.0873 | 886606 | 1629334 | 2515940 | 2.3993 |

---

## Configuration

In `src/tracker.py`:
```python
POLL_INTERVAL = 5 
AUTO_SAVE_INTERVAL = 1800 
```

---

## Requirements

- Windows 10/11
- Python 3.8+
- psutil
- pandas

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

## License

MIT