#!/bin/bash

# Port Pairs SpotOn API - Setup Script
# This script sets up the virtual environment and installs dependencies

echo "🚀 Setting up Port Pairs SpotOn API..."
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "❌ Failed to create virtual environment"
    exit 1
fi

echo "✓ Virtual environment created"
echo ""

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

if [ $? -ne 0 ]; then
    echo "❌ Failed to activate virtual environment"
    exit 1
fi

echo "✓ Virtual environment activated"
echo ""

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip -q

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✓ Dependencies installed successfully"
echo ""

# Check if CSV file exists
if [ ! -f "Qlik Sense Port Pairs SpotOn.csv" ]; then
    echo "⚠️  Warning: 'Qlik Sense Port Pairs SpotOn.csv' not found in current directory"
    echo "   Make sure to add the CSV file before running the application"
    echo ""
fi

echo "✅ Setup complete!"
echo ""
echo "To start the API server:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Run the server: python main.py"
echo "  3. Open http://localhost:8000 in your browser"
echo "  4. View interactive docs at http://localhost:8000/docs"
echo ""
echo "To deactivate the virtual environment later: deactivate"
echo ""

