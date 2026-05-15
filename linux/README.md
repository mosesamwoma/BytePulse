# BytePulse — Linux

Track WiFi data usage locally on Linux with zero cloud involvement.

## Features

- Silent background tracking via systemd
- System tray icon (GNOME, KDE, XFCE compatible)
- Triple-format logging (CSV, JSON, SQLite)
- Data cap alerts
- 7-day usage forecasting
- Anomaly detection
- Streamlit dashboard

## Requirements

- Python 3.11
- Linux with systemd
- Display server (X11 or Wayland) for tray icon

## Quick Start

```bash
cd linux
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

## Usage

**Start tracker:**
```bash
python3 src/tracker.py
```

**Start with tray icon and dashboard:**
```bash
python3 main.py
```

**View dashboard:**
```bash
streamlit run app.py
```

**Check logs:**
```bash
tail -f data/tracker.log
```

## Data Locations

- **Database**: `data/bytepulse.db`
- **CSV**: `data/usage_log.csv`
- **JSON**: `data/usage_log.json`
- **Logs**: `data/tracker.log`

## Installation with systemd

```bash
sudo bash setup_systemd.sh
sudo systemctl start bytepulse
sudo systemctl enable bytepulse
journalctl -u bytepulse -f
```