# BytePulse

**See exactly how your internet data is used — locally, silently, and privately.**

Track every WiFi session, detect heavy usage, and visualize patterns with zero cloud involvement.

---

## Overview

BytePulse runs silently in the background. Every time you connect to WiFi, it tracks your data usage and saves sessions to a local SQLite database, CSV, and JSON simultaneously.

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

- **Silent background tracking** — Runs at login, no visible windows
- **Triple-format logging** — CSV, JSON, and SQLite simultaneously
- **Atomic writes** — Temp-file-swap prevents data corruption
- **Fault tolerance** — Falls back to `.pending` files if primary write fails
- **System tray icon** — Right-click to open dashboard or stop tracker
- **Streamlit dashboard** — Daily, weekly, and monthly views with hourly heatmap
- **Anomaly detection** — Z-score flagging for unusual sessions
- **Data cap alerts** — Toast notifications at 80% and 100%
- **7-day forecast** — Prophet-powered usage prediction

---

## Requirements

- Python 3.11 (exactly) — [Download](https://www.python.org/downloads/release/python-3110/)
- Windows 10/11 or Linux

> ⚠️ **Python 3.11 only.** psutil has compatibility issues with Python 3.12+.

---

## Gallery

### Dashboard Overview
![Dashboard overview](/assets/1.png)

### Peak Hours & Detailed Data
![Peak hours and detailed data](/assets/3.png)

### 7-Day Usage Forecast
![7-Day Usage Forecast](/assets/6.png)

---

## Getting Started

```bash
git clone https://github.com/mosesamwoma/BytePulse.git
cd BytePulse
```

- **Windows:** See [windows/README.md](windows/README.md)
- **Linux:** See [linux/README.md](linux/README.md)

---

## Output Files

All data stored locally in `data/` folder:

- **`bytepulse.db`** — SQLite database with all sessions
- **`usage_log.csv`** — CSV export for Excel compatibility
- **`usage_log.json`** — JSON export for programmatic access
- **`tracker.log`** — Application logs

---

## Dashboard

Open at `http://localhost:8501` or right-click system tray icon → **Open Dashboard**.

**Views:**
- **Daily** — Hourly heatmap, peak hours, anomalies, 7-day forecast
- **Weekly** — Day-of-week patterns
- **Monthly** — Monthly trends

---

## Roadmap

- [ ] Per-SSID usage breakdown
- [ ] ISP billing cycle alignment
- [ ] Cross-platform portability (macOS)
- [ ] Mobile app (iOS/Android) for remote monitoring
- [ ] Web dashboard for multi-device sync
- [ ] Export to cloud (optional, privacy-first)

---

## Contributing

1. Fork the repo
2. Create a branch: `git checkout -b feature/your-feature`
3. Commit: `git commit -m "describe change"`
4. Push: `git push origin feature/your-feature`
5. Open a Pull Request

---

<div align="center">
<sub>No cloud · Your data stays yours</sub>
</div>