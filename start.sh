#!/bin/bash

# OSS Community Agent - Full System Starter
# This script runs both frontend and backend

echo "🚀 Starting OSS Community Agent"
echo "================================"

# Check if we're in the right directory
if [[ ! -f "run_full_system.py" ]]; then
    echo "❌ Error: Please run this script from the project root directory"
    echo "📁 Current directory: $(pwd)"
    echo "📌 Expected files: run_full_system.py"
    exit 1
fi

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 is not installed or not in PATH"
    exit 1
fi

# Check if virtual environment exists
if [[ -d ".venv" ]]; then
    echo "🐍 Activating virtual environment..."
    source .venv/bin/activate
fi

# Install dependencies if needed
if ! python3 -c "import streamlit" &> /dev/null; then
    echo "📦 Installing dependencies..."
    pip3 install -r infra/requirements.txt
fi

# Set up environment file if it doesn't exist
if [[ ! -f ".env" ]] && [[ -f ".env.example" ]]; then
    echo "🔧 Setting up environment file..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your API keys before the first run!"
fi

# Start the full system
echo "🌟 Launching OSS Community Agent..."
python3 run_full_system.py
