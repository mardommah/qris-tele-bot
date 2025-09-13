#!/usr/bin/env python3
# run_bot.py
"""Wrapper script to run the bot with proper async environment"""

import asyncio
import sys
import os

# Set environment variables for compatibility
os.environ['PYTHONASYNCIODEBUG'] = '1'

def main():
    """Main function to run the bot"""
    # Import the main module here to ensure proper async context
    from main import main as bot_main
    
    # Run the bot in a proper asyncio event loop
    try:
        bot_main()
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Error running bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # For Python 3.7+, use asyncio.run()
    if sys.version_info >= (3, 7):
        asyncio.run(main())
    else:
        # For older versions, create event loop manually
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(main())
        except KeyboardInterrupt:
            print("\nBot stopped by user")
        finally:
            loop.close()