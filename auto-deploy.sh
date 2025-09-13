#!/bin/bash

# Auto Deploy Script for QRIS Telegram Bot

echo "🚀 Starting QRIS Telegram Bot deployment..."

# Navigate to the root directory
cd /root

# Remove existing folder if it exists
echo "🗑️ Removing existing qris-tele-bot folder..."
rm -rf qris-tele-bot

# Clone the repository
echo "📥 Cloning repository..."
git clone https://github.com/mardommah/qris-tele-bot.git

# Navigate to the project directory
cd qris-tele-bot

# Create virtual environment
echo "🔧 Creating virtual environment..."
python3 -m venv env

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source env/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Copy environment variables
echo "📋 Copying environment variables..."
/root/copy-env.sh

# Restart the service
echo "🔄 Restarting service..."
sudo systemctl restart pythonapp.service

echo "✅ Deployment completed successfully!"