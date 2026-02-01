#!/bin/bash

# Quick start script for Places Manager Web App

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║          Nouakchott Places Manager - Quick Start            ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if Flask is installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "⚠️  Flask is not installed."
    echo ""
    echo "Installing Flask..."
    pip install flask
    
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install Flask."
        echo ""
        echo "Please install manually:"
        echo "  pip install flask"
        exit 1
    fi
    echo "✅ Flask installed successfully"
    echo ""
fi

# Check if JSON file exists
if [ ! -f "nouakchott_places.json" ]; then
    echo "❌ Error: nouakchott_places.json not found!"
    echo ""
    echo "Make sure you're in the correct directory."
    exit 1
fi

# Count places
PLACE_COUNT=$(python3 -c "import json; print(len(json.load(open('nouakchott_places.json'))))")

echo "✅ Flask is installed"
echo "✅ Found $PLACE_COUNT places in nouakchott_places.json"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Starting web server..."
echo ""
echo "🌐 Open your browser and go to:"
echo ""
echo "   👉 http://localhost:3000"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the app
python3 app.py
