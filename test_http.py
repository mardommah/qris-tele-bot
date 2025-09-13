#!/usr/bin/env python3
# test_http.py
"""Test HTTP connectivity to Telegram API"""

import asyncio
import httpx

async def test_http():
    """Test HTTP connectivity"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("https://api.telegram.org")
            print(f"HTTP request successful: {response.status_code}")
            print(f"Response: {response.text[:100]}...")
            return True
    except Exception as e:
        print(f"HTTP request failed: {e}")
        return False

if __name__ == "__main__":
    try:
        asyncio.run(test_http())
    except Exception as e:
        print(f"Failed to run: {e}")