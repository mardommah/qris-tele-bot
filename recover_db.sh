#!/bin/bash

# Database Recovery Script for QRIS Telegram Bot

echo "🔄 QRIS Telegram Bot Database Recovery"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 is not installed"
    exit 1
fi

# Check if recovery script exists
if [ ! -f "recovery_script.py" ]; then
    echo "❌ Error: recovery_script.py not found"
    exit 1
fi

# Run the recovery script with any passed arguments
python3 recovery_script.py "$@"