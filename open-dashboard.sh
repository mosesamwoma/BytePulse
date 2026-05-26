#!/bin/bash
cd ~/projects/BytePulse/linux
source venv/bin/activate
python3 -m streamlit run app.py --server.port=8501 &
sleep 3
xdg-open http://localhost:8501
