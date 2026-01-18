#!/bin/bash
# Quick start script for Phishing Detection Backend

echo "=========================================="
echo "Phishing Detection Backend - Quick Start"
echo "=========================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Create virtual environment (optional but recommended)
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Set up data directory
echo "Setting up data directory..."
python setup_data.py

# Train models
echo "Training models..."
python train_models.py

# Start server
echo "Starting API server..."
echo "Server will be available at http://localhost:8000"
python app.py
