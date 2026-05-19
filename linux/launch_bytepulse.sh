#!/bin/bash

set -e

LINUX_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$LINUX_DIR")"
VENV_DIR="$LINUX_DIR/venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "[*] Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

echo "[*] Installing dependencies..."
pip install -q -r "$LINUX_DIR/requirements.txt"

echo "[*] Starting BytePulse..."
python3 "$LINUX_DIR/main.py"