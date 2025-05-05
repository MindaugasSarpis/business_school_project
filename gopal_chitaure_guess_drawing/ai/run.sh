#!/bin/bash

echo "🔁 Starting QuickDraw setup and training..."

# Step 1: Create virtual environment
echo "🐍 Creating virtual environment..."
python3.10 -m venv quickdraw_env
source quickdraw_env/bin/activate

# Step 2: Install dependencies from requirements.txt
echo "📦 Installing dependencies from requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

# Step 3: AI model
echo "⬇️ Downloading QuickDraw dataset..."
python3 pari.py

echo "✅ All steps completed successfully!"
