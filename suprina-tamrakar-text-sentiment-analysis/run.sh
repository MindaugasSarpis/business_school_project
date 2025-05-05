#!/bin/bash

# === Settings ===
ENV_NAME="bert_env"
PYTHON_REQUIRED="3.13"
MODEL_DIR="./models/distilbert_dailydialog"

# === 1. Check Python version ===
PYTHON_VERSION=$(python3 -c "import platform; print(platform.python_version())")
PYTHON_MAJOR_MINOR=$(echo $PYTHON_VERSION | cut -d. -f1,2)

if [[ "$PYTHON_MAJOR_MINOR" != "$PYTHON_REQUIRED" ]]; then
    echo "❌ Python $PYTHON_REQUIRED is required! You have $PYTHON_VERSION"
    echo "Please create an environment with Python $PYTHON_REQUIRED first."
    exit 1
else
    echo "✅ Correct Python version detected: $PYTHON_VERSION"
fi

# === 2. Create or Activate Virtual Environment ===
if [ ! -d "$ENV_NAME" ]; then
    echo "🔵 Creating virtual environment: $ENV_NAME"
    python3 -m venv "$ENV_NAME"
    source "$ENV_NAME/bin/activate"
    echo "🔵 Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "🟢 Virtual environment found: $ENV_NAME"
    source "$ENV_NAME/bin/activate"
fi

# === 3. Check if model exists ===
if [ -d "$MODEL_DIR" ]; then
    echo "✅ Pre-trained model found at $MODEL_DIR. Skipping training."
else
    echo "⚡ No pre-trained model found. Starting model training (train_bert_sentiment.py)..."
    python train_bert_sentiment.py
fi

# === 4. Run Flask App ===
echo "🚀 Starting the Flask app (app.py)..."
python app.py
