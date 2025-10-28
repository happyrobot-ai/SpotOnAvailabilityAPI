#!/bin/bash

# Port Pairs SpotOn API - Run Script
# This script activates the virtual environment and runs the API server

echo "🚀 Starting Port Pairs SpotOn API..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "   Please run ./setup.sh first to set up the project"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

if [ $? -ne 0 ]; then
    echo "❌ Failed to activate virtual environment"
    exit 1
fi

# Check if CSV file exists
if [ ! -f "Qlik Sense Port Pairs SpotOn.csv" ]; then
    echo "❌ Error: 'Qlik Sense Port Pairs SpotOn.csv' not found!"
    echo "   Make sure the CSV file is in the same directory as main.py"
    exit 1
fi

# Run the application
echo "✓ Starting server on http://localhost:8000"
echo "✓ Interactive docs available at http://localhost:8000/docs"
echo ""
echo "Press CTRL+C to stop the server"
echo ""

python main.py

