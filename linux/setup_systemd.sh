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

cat > "$SERVICE_FILE" << 'EOF'
[Unit]
Description=BytePulse WiFi Data Tracker
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=mosesamwoma
WorkingDirectory=/home/mosesamwoma/projects/BytePulse
Environment="PYTHONPATH=/home/mosesamwoma/projects/BytePulse"
ExecStart=/bin/bash /home/mosesamwoma/projects/BytePulse/linux/run_tracker.sh
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