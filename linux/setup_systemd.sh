#!/bin/bash

if [ "$EUID" -ne 0 ]; then
    echo "This script must be run as root (use sudo)"
    exit 1
fi

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$PROJECT_DIR")"
USERNAME="${SUDO_USER:-$(whoami)}"

echo "[*] Setting up systemd service..."

mkdir -p "$PROJECT_DIR/data"
mkdir -p "$PROJECT_DIR/logs"
chown -R "$USERNAME:$USERNAME" "$PROJECT_DIR"

SERVICE_FILE="/etc/systemd/system/bytepulse.service"

cat > "$SERVICE_FILE" << EOF
[Unit]
Description=BytePulse WiFi Data Tracker
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$USERNAME
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/linux/venv/bin/python3 $PROJECT_DIR/linux/src/tracker.py
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload

echo "[✓] Service installed at $SERVICE_FILE"
echo ""
echo "To start tracking:"
echo "  sudo systemctl start bytepulse"
echo "  sudo systemctl enable bytepulse"
echo ""
echo "To check status:"
echo "  systemctl status bytepulse"
echo "  journalctl -u bytepulse -f"