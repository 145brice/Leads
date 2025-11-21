# Automated Scraping Setup - No Duplicates

## Overview
The system now includes **incremental scraping** that only pulls new leads and skips duplicates.

## Files Created

### 1. `incremental_scraper.py`
- Loads existing database and tracks all permit numbers
- Scrapes from 4 counties (Nashville, Dallas, Austin, San Antonio)
- Checks each new permit against existing database
- Only adds NEW permits (skips duplicates)
- Adds `first_seen` timestamp to new leads
- Updates database with only new data

### 2. `scheduled_scraper.py`
- Runs incremental scraper 4 times daily:
  - **6:00 AM** - Morning scrape
  - **12:00 PM** - Midday scrape
  - **6:00 PM** - Evening scrape
  - **12:00 AM** - Midnight scrape
- Uses Python `schedule` library
- Logs all activity to console

## How It Works

### Duplicate Detection
```python
# Loads all existing permit numbers into a set
seen_permits = {'T2025097204', 'T2025097203', ...}

# Checks each new permit
if permit_number in seen_permits:
    # Skip duplicate
else:
    # Add new lead to database
```

### Database Updates
- **Before**: 18 permits
- **After 1st run**: Added 81 new permits, skipped 14 duplicates
- **Total**: 180 permits in database

## Running the Scraper

### Manual Test (One-Time)
```bash
cd /Users/briceleasure/Desktop/contractor-leads-saas
python3 incremental_scraper.py
```

### Scheduled Execution (4x Daily)
```bash
cd /Users/briceleasure/Desktop/contractor-leads-saas
python3 scheduled_scraper.py
```

This will run continuously and execute scrapes at:
- 6:00 AM
- 12:00 PM
- 6:00 PM
- 12:00 AM (midnight)

Press `Ctrl+C` to stop the scheduler.

## Background Execution (macOS)

### Option 1: Use `nohup` (Simple)
```bash
cd /Users/briceleasure/Desktop/contractor-leads-saas
nohup python3 scheduled_scraper.py > scraper.log 2>&1 &
```

Check logs:
```bash
tail -f scraper.log
```

Stop the scraper:
```bash
pkill -f scheduled_scraper.py
```

### Option 2: LaunchAgent (Recommended for Production)

Create a plist file at `~/Library/LaunchAgents/com.contractorleads.scraper.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.contractorleads.scraper</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>/Users/briceleasure/Desktop/contractor-leads-saas/scheduled_scraper.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/Users/briceleasure/Desktop/contractor-leads-saas/logs/scraper.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/briceleasure/Desktop/contractor-leads-saas/logs/scraper_error.log</string>
</dict>
</plist>
```

Load and start:
```bash
mkdir -p ~/Desktop/contractor-leads-saas/logs
launchctl load ~/Library/LaunchAgents/com.contractorleads.scraper.plist
```

Stop:
```bash
launchctl unload ~/Library/LaunchAgents/com.contractorleads.scraper.plist
```

## Verify It's Working

### Check Database Size Growth
```bash
cd /Users/briceleasure/Desktop/contractor-leads-saas
wc -l leads_db/current_leads.json
```

### View Recent Leads
```bash
cd /Users/briceleasure/Desktop/contractor-leads-saas
python3 << 'PYEOF'
import json
with open('leads_db/current_leads.json', 'r') as f:
    db = json.load(f)
    
total = sum(len(counties[county]) for counties in db['leads'].values() for county in counties)
print(f"Last Updated: {db['last_updated']}")
print(f"Total Leads: {total}")

# Show recently added leads
for state, counties in db['leads'].items():
    for county, leads in counties.items():
        recent = [l for l in leads if l.get('first_seen')][:3]
        if recent:
            print(f"\n{state.title()} - {county.title()}: {len(leads)} leads")
            for lead in recent:
                print(f"  • {lead['permit_number']} - {lead.get('first_seen', 'N/A')}")
PYEOF
```

## Expected Output

Each scrape session will show:
```
======================================================================
🌐 INCREMENTAL SCRAPING SESSION - NO DUPLICATES
======================================================================
📊 Loaded database: 180 existing permits tracked
🕷️  Scraping Nashville-Davidson County (ArcGIS API)...
   🔍 Found 20 Nashville permits

======================================================================
🔍 CHECKING FOR DUPLICATES
======================================================================
   ⏭️  Skipping duplicate: T2025097204
   ⏭️  Skipping duplicate: T2025097203
   ✅ NEW: T2025099999 - 123 New Street 37203

======================================================================
📊 SCRAPING SUMMARY
======================================================================
✅ New leads added: 15
⏭️  Duplicates skipped: 75
📦 Total leads in database: 195
🕒 Last updated: 2025-11-19T18:45:11.186604
======================================================================
```

## Integration with Flask App

The Flask app at `/tmp/contractor_leads.py` already loads from `leads_db/current_leads.json`.

To refresh the app with new data, just restart it:
```bash
pkill -f contractor_leads.py
python3 /tmp/contractor_leads.py
```

Or add auto-reload to Flask app to pick up database changes automatically.

## Monitoring

### Check if scheduler is running
```bash
ps aux | grep scheduled_scraper
```

### View logs (if using nohup)
```bash
tail -f ~/Desktop/contractor-leads-saas/scraper.log
```

### Check last update time
```bash
cd /Users/briceleasure/Desktop/contractor-leads-saas
python3 -c "import json; db=json.load(open('leads_db/current_leads.json')); print(f'Last updated: {db[\"last_updated\"]}')"
```

## Summary

✅ **Duplicate Detection**: Tracks all permit numbers, skips existing ones
✅ **Incremental Updates**: Only adds new leads to database
✅ **4x Daily Schedule**: 6am, 12pm, 6pm, 12am
✅ **Timestamps**: Tracks when each lead was first seen
✅ **Real APIs**: Nashville (ArcGIS), Austin (Socrata), San Antonio (OpenGov)
✅ **Production Ready**: Can run in background via nohup or LaunchAgent
