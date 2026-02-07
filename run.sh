#!/bin/bash

echo "=================================================="
echo "🧠 AI Research Ideation Pipeline - Quick Start"
echo "=================================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt
echo ""

# Check for API key
if [ -z "$GROQ_API_KEY" ]; then
    echo "⚠️  GROQ_API_KEY not set in environment"
    echo ""
    echo "Please get your free API key from: https://console.groq.com/keys"
    echo ""
    echo "Then run ONE of these commands:"
    echo "  1. export GROQ_API_KEY='your-key-here'"
    echo "  2. Create a .env file with: GROQ_API_KEY=your-key-here"
    echo ""
    read -p "Do you want to enter your API key now? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter your Groq API key: " api_key
        export GROQ_API_KEY="$api_key"
        echo "export GROQ_API_KEY='$api_key'" > .env
        echo "✅ API key saved to .env"
    fi
fi

echo ""
echo "=================================================="
echo "🧪 Running setup tests..."
echo "=================================================="
python3 test_setup.py

echo ""
echo "=================================================="
echo "🚀 Starting Flask server..."
echo "=================================================="
echo ""
echo "Server will start at: http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo ""

python3 app.py
