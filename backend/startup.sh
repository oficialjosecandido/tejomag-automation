#!/bin/bash
# Azure App Service startup script

echo "Starting TejoMag Backend..."

# Create logs directory
mkdir -p logs

# Install dependencies if needed
if [ ! -d "antenv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv antenv
    source antenv/bin/activate
    pip install -r requirements.txt
else
    echo "Activating existing virtual environment..."
    source antenv/bin/activate
fi

# Start Gunicorn with proper configuration
echo "Starting Gunicorn server..."
gunicorn --bind=0.0.0.0:8000 \
         --workers=2 \
         --threads=4 \
         --timeout=300 \
         --access-logfile=- \
         --error-logfile=- \
         --log-level info \
         --preload \
         app:app

