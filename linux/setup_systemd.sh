#!/bin/bash

if [ "$EUID" -ne 0 ]; then
    echo "This script must be run as root (use sudo)"
    exit 1
fi

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
USERNAME="${SUDO_USER:-$(whoami)}"

echo "[*] Setting up systemd service..."

mkdir -p "$PROJECT_DIR/data"
mkdir -p "$PROJECT_DIR/logs"
chown -R "$USERNAME:$USERNAME" "$PROJECT_DIR"

SERVICE_FILE="/etc/systemd/system/bytepulse.service"
TIMER_FILE="/etc/systemd/system/bytepulse.timer"

sed "s|__PROJECT_DIR__|$PROJECT_DIR|g; s|__USERNAME__|$USERNAME|g" "$PROJECT_DIR/systemd/bytepulse.service.template" > "$SERVICE_FILE"
sed "s|__PROJECT_DIR__|$PROJECT_DIR|g; s|__USERNAME__|$USERNAME|g" "$PROJECT_DIR/systemd/bytepulse.timer.template" > "$TIMER_FILE"

systemctl daemon-reload

echo "[✓] Service installed at $SERVICE_FILE"
echo "[✓] Timer installed at $TIMER_FILE"
echo ""
echo "To start tracking:"
echo "  sudo systemctl start bytepulse"
echo "  sudo systemctl enable bytepulse"
echo ""
echo "To check status:"
echo "  systemctl status bytepulse"
echo "  journalctl -u bytepulse -f"