#!/bin/bash

# NucDeck CAD Automation Setup Script
# This script sets up the development environment for OpenSCAD automation

echo "🎮 Setting up NucDeck CAD Automation Environment..."

# Check if OpenSCAD is installed
if ! command -v openscad &> /dev/null; then
    echo "📦 OpenSCAD not found. Installing..."
    
    # Detect OS and install OpenSCAD
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        sudo apt update
        sudo apt install -y openscad
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install openscad
        else
            echo "❌ Please install Homebrew first: https://brew.sh/"
            exit 1
        fi
    else
        echo "❌ Unsupported OS. Please install OpenSCAD manually."
        exit 1
    fi
else
    echo "✅ OpenSCAD is already installed"
    openscad --version
fi

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip install -r requirements.txt

# Create output directory
mkdir -p output
echo "📁 Created output directory"

# Make scripts executable
chmod +x cad_automator.py
chmod +x web_viewer/server.py

# Test OpenSCAD installation
echo "🧪 Testing OpenSCAD installation..."
cd OpenSCAD
if openscad --version; then
    echo "✅ OpenSCAD test passed"
else
    echo "❌ OpenSCAD test failed"
    exit 1
fi

cd ..

echo ""
echo "🎉 Setup complete! You can now:"
echo "   1. Run the CAD automator: python cad_automator.py --help"
echo "   2. Start the web viewer: python web_viewer/server.py"
echo "   3. Edit OpenSCAD files in: OpenSCAD/"
echo "   4. View outputs in: output/"
echo ""
echo "🚀 Quick start:"
echo "   python cad_automator.py --render-preview --batch"
echo "   python web_viewer/server.py"
