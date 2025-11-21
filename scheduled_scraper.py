#!/usr/bin/env python3
"""
Scheduled Scraper - Runs 4 times daily (6am, 12pm, 6pm, 12am)
Uses incremental scraper to avoid duplicates
"""

import schedule
import time
from datetime import datetime
import subprocess
import sys
from pathlib import Path

# Path to incremental scraper
SCRAPER_PATH = Path(__file__).parent / 'incremental_scraper.py'

def run_scraper():
    """Run the incremental scraper"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n{'='*70}")
    print(f"⏰ SCHEDULED SCRAPE STARTED: {timestamp}")
    print(f"{'='*70}\n")
    
    try:
        # Run incremental scraper
        result = subprocess.run(
            [sys.executable, str(SCRAPER_PATH)],
            capture_output=True,
            text=True,
            check=True
        )
        
        print(result.stdout)
        
        if result.stderr:
            print("Warnings/Errors:")
            print(result.stderr)
        
        print(f"\n{'='*70}")
        print(f"✅ SCRAPE COMPLETED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}\n")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Scraper failed with exit code {e.returncode}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def main():
    """Set up schedule and run continuously"""
    print("\n" + "="*70)
    print("🤖 AUTOMATED SCRAPER SCHEDULER")
    print("="*70)
    print("📅 Schedule: 4 times daily")
    print("   • 06:00 AM")
    print("   • 12:00 PM")
    print("   • 06:00 PM")
    print("   • 12:00 AM (midnight)")
    print("="*70)
    print("✅ Scheduler started - press Ctrl+C to stop")
    print("="*70 + "\n")
    
    # Schedule jobs
    schedule.every().day.at("06:00").do(run_scraper)
    schedule.every().day.at("12:00").do(run_scraper)
    schedule.every().day.at("18:00").do(run_scraper)
    schedule.every().day.at("00:00").do(run_scraper)
    
    # Optional: Run immediately on startup
    print("🚀 Running initial scrape...")
    run_scraper()
    
    # Keep running
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\n\n⚠️  Scheduler stopped by user")
        print("="*70 + "\n")

if __name__ == '__main__':
    main()
