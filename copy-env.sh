#!/bin/bash

# Script to copy environment variables
# This script is called during deployment to set up the .env file

echo "Copying environment variables..."
cp /root/.env /root/qris-tele-bot/.env

echo "Environment variables copied successfully!"