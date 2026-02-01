#!/bin/bash

# Setup script for Google Places Extractor

echo "=========================================="
echo "Google Places Extractor - Setup"
echo "=========================================="
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7+."
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Found Python $PYTHON_VERSION"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""

# Check for API key
if [ -z "$GOOGLE_PLACES_API_KEY" ]; then
    echo "⚠️  GOOGLE_PLACES_API_KEY environment variable not set"
    echo ""
    echo "Please set your API key:"
    echo "  export GOOGLE_PLACES_API_KEY='your-api-key-here'"
    echo ""
    echo "Or create a .env file (see .env.example)"
else
    echo "✅ GOOGLE_PLACES_API_KEY is set"
fi

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Set your Google Places API key (if not already set)"
echo "  2. Run: python3 extract_places.py"
echo "  3. Monitor progress in extraction.log"
echo ""
echo "For help, see README.md"
