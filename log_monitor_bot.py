#!/usr/bin/env python3
# log_monitor_bot.py
"""
Resource monitoring script with logging for QRIS Telegram Bot
"""
import psutil
import time
import argparse
import logging
from datetime import datetime
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot_resource_usage.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def get_process_info(process_name):
    """Get process information by name"""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'memory_info', 'cpu_percent']):
        try:
            if process_name in ' '.join(proc.info['cmdline'] or []):
                processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, TypeError):
            pass
    return processes

def log_resource_usage(interval=60, duration=None):
    """Log resource usage of bot processes"""
    logger.info("Starting resource monitoring for QRIS Telegram Bot")
    
    start_time = time.time()
    
    try:
        while True:
            # Check if duration limit reached
            if duration and (time.time() - start_time) > duration:
                logger.info("Monitoring duration reached. Stopping.")
                break
            
            # Get processes related to the bot
            main_bot_processes = get_process_info('main.py')
            webhook_processes = get_process_info('webhook_server.py')
            all_processes = main_bot_processes + webhook_processes
            
            if not all_processes:
                logger.info("No bot processes found")
            else:
                for proc in all_processes:
                    if proc['cmdline']:  # Check if cmdline exists
                        pid = proc['pid']
                        cmd = ' '.join(proc['cmdline'])
                        cpu_percent = proc['cpu_percent'] or 0
                        memory_info = proc['memory_info']
                        memory_percent = psutil.Process(pid).memory_percent()
                        memory_rss = memory_info.rss / 1024 / 1024  # Convert to MB
                        
                        logger.info(f"PID:{pid} | CPU:{cpu_percent:.2f}% | "
                                  f"Memory:{memory_percent:.2f}% ({memory_rss:.2f}MB) | "
                                  f"Command:{cmd[:50]}{'...' if len(cmd) > 50 else ''}")
            
            time.sleep(interval)
    except KeyboardInterrupt:
        logger.info("Monitoring stopped by user.")
    except Exception as e:
        logger.error(f"Error during monitoring: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Log QRIS Telegram Bot resource usage")
    parser.add_argument("-i", "--interval", type=int, default=60, 
                        help="Logging interval in seconds (default: 60)")
    parser.add_argument("-d", "--duration", type=int, 
                        help="Monitoring duration in seconds (default: infinite)")
    
    args = parser.parse_args()
    
    log_resource_usage(args.interval, args.duration)