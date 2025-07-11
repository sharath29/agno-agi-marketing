#!/bin/bash

# Agno-AGI Marketing Automation - Quick Start Script
echo "🚀 Activating Agno-AGI Marketing Automation Environment..."

# Check if we're in the right directory
if [ ! -f "src/simple_demo.py" ]; then
    echo "❌ Error: Please run this script from the agentic-marketing directory"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Error: Virtual environment not found. Please run setup first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

echo "✅ Virtual environment activated!"
echo "✅ Ready to run marketing automation demos"
echo ""
echo "Quick commands:"
echo "  python src/simple_demo.py    # Run the interactive demo"
echo "  python main.py               # Run full system (requires more deps)"
echo "  deactivate                   # Exit virtual environment"
echo ""
echo "Current Python: $(which python)"
echo "Installed packages: $(pip list --format=freeze | wc -l) packages"
echo ""
echo "🎯 To get started: python src/simple_demo.py"