#!/bin/bash

if [ ! -d "sentiment_env" ]; then
    echo "Creating virtual environment..."
    python3 -m venv sentiment_env
    source sentiment_env/bin/activate
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    source sentiment_env/bin/activate
fi

echo "Starting the Flask app..."
python app.py