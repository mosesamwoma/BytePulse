CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    start_time TEXT NOT NULL UNIQUE,
    end_time TEXT NOT NULL,
    duration_minutes REAL,
    bytes_sent INTEGER,
    bytes_received INTEGER,
    total_bytes INTEGER,
    usage_MB REAL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_start_time ON sessions(start_time);