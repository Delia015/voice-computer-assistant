#!/bin/bash
echo "==============================================="
echo "Voice Computer Assistant (Unix 一键运行)"
echo "==============================================="

if [ ! -d ".venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv .venv
fi

echo "Activating venv..."
source .venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

echo "✅ Starting app..."
python3 app.py
