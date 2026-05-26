#!/bin/bash
cd /home/mosesamwoma/projects/BytePulse
source /home/mosesamwoma/projects/BytePulse/linux/venv/bin/activate
export PYTHONPATH=/home/mosesamwoma/projects/BytePulse
exec python3 /home/mosesamwoma/projects/BytePulse/linux/src/tracker.py
