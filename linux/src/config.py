import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, "data")
LOG_DIR = os.path.join(BASE_DIR, "logs")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

CSV_PATH = os.path.join(DATA_DIR, "usage_log.csv")
JSON_PATH = os.path.join(DATA_DIR, "usage_log.json")
DB_PATH = os.path.join(DATA_DIR, "bytepulse.db")
LOG_PATH = os.path.join(DATA_DIR, "tracker.log")

POLL_INTERVAL = 5
AUTO_SAVE_INTERVAL = 1800

CAP_MB = 10240
MONTHLY_CAP_MB = 307200