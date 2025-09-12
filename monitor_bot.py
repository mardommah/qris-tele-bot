#!/usr/bin/env python3
# monitor_bot.py
"""
Resource monitoring script for QRIS Telegram Bot
"""
import psutil
import time
import argparse
from datetime import datetime

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

def monitor_resources(interval=5):
    """Monitor resource usage of bot processes"""
    print("Monitoring QRIS Telegram Bot resource usage...")
    print("Press Ctrl+C to stop\n")
    
    # Print header
    print(f"{'Time':<10} {'PID':<8} {'Process':<20} {'CPU%':<8} {'Memory%':<10} {'Memory RSS':<12} {'Command'}")
    print("-" * 100)
    
    try:
        while True:
            # Get processes related to the bot
            main_bot_processes = get_process_info('main.py')
            webhook_processes = get_process_info('webhook_server.py')
            all_processes = main_bot_processes + webhook_processes
            
            # Clear screen (optional)
            # print("\033[2J\033[H")  # Uncomment to clear screen each update
            
            current_time = datetime.now().strftime("%H:%M:%S")
            
            if not all_processes:
                print(f"{current_time:<10} No bot processes found")
            else:
                for proc in all_processes:
                    if proc['cmdline']:  # Check if cmdline exists
                        pid = proc['pid']
                        cmd = ' '.join(proc['cmdline'])
                        cpu_percent = proc['cpu_percent'] or 0
                        memory_info = proc['memory_info']
                        memory_percent = psutil.Process(pid).memory_percent()
                        memory_rss = memory_info.rss / 1024 / 1024  # Convert to MB
                        
                        # Truncate command for display
                        display_cmd = cmd[:30] + "..." if len(cmd) > 30 else cmd
                        
                        print(f"{current_time:<10} {pid:<8} {'main.py' if 'main.py' in cmd else 'webhook.py':<20} "
                              f"{cpu_percent:<8.2f} {memory_percent:<10.2f} {memory_rss:<12.2f} {display_cmd}")
            
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")

def get_system_overview():
    """Get overall system resource usage"""
    print("=== System Resource Overview ===")
    print(f"CPU Usage: {psutil.cpu_percent(interval=1)}%")
    memory = psutil.virtual_memory()
    print(f"Memory Usage: {memory.percent}% ({memory.used / 1024 / 1024:.1f} MB / {memory.total / 1024 / 1024:.1f} MB)")
    print(f"Available Memory: {memory.available / 1024 / 1024:.1f} MB")
    
    # Get disk usage
    disk = psutil.disk_usage('/')
    print(f"Disk Usage: {(disk.total - disk.free) / disk.total * 100:.1f}% "
          f"({(disk.total - disk.free) / 1024 / 1024 / 1024:.1f} GB / {disk.total / 1024 / 1024 / 1024:.1f} GB)")
    
    print()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor QRIS Telegram Bot resource usage")
    parser.add_argument("-i", "--interval", type=int, default=5, 
                        help="Monitoring interval in seconds (default: 5)")
    parser.add_argument("-o", "--overview", action="store_true",
                        help="Show system overview only")
    
    args = parser.parse_args()
    
    # Show system overview
    get_system_overview()
    
    if not args.overview:
        monitor_resources(args.interval)
