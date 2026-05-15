# BytePulse — Linux

Track WiFi data usage locally on Linux with zero cloud involvement.

## Features

- Silent background tracking via systemd
- Triple-format logging (CSV, JSON, SQLite)
- Data cap alerts
- 7-day usage forecasting
- Anomaly detection
- Streamlit dashboard

## Requirements

- Python 3.11
- Linux with systemd
- Root access for installation

## Installation

```bash
cd linux
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
sudo bash setup_systemd.sh
```

## Usage

Start tracking:
```bash
sudo systemctl start bytepulse
sudo systemctl enable bytepulse
```

View dashboard:
```bash
streamlit run app.py
```

Check logs:
```bash
journalctl -u bytepulse -f
```

Stop tracking:
```bash
sudo systemctl stop bytepulse
```

## Data Locations

- **Database**: `data/bytepulse.db`
- **CSV**: `data/usage_log.csv`
- **JSON**: `data/usage_log.json`
- **Logs**: `data/tracker.log`

## Configuration

Edit `src/config.py` to customize:
- Data caps
- Alert thresholds
- Polling interval