# 🚀 AUTO-SUBSCRIPTION SYSTEM - Complete Setup Guide

**Date:** November 19, 2025  
**System:** Contractor Leads Auto-Feed Platform

---

## 📋 **What We Built**

### Core Features:
1. **Stripe Checkout** - $20/month per city, 7-day free trial
2. **Auto-Scraper Cron** - Runs 4x daily (5:30 AM, 9:30 AM, 1:30 PM, 5:30 PM)
3. **Duplicate Detection** - SHA-256 hash-based deduplication (30-day rolling window)
4. **Email Delivery** - Daily CSV dumps + RSS feeds for CRM integration
5. **Archive Vault** - 70k San Antonio original dump preserved forever

---

## 🗂️ **File Structure**

```
contractor-leads-saas/
├── subscription_manager.py      ← Stripe payments, subscriber database
├── subscription_app.py          ← Flask web app with checkout UI
├── auto_scraper_cron.py         ← 4x daily scraping daemon
├── email_service.py             ← Email with CSV attachments
├── multi_region_scraper.py      ← Core scraping engine
├── templates/
│   └── subscription_index.html  ← Beautiful city selection UI
├── archive_vault/               ← 70k original dumps (NEVER DELETE)
│   └── San Antonio-Bexar_archive.csv
├── fresh_feeds/                 ← Daily new permits only
│   └── user_12345_Nashville_20251119.csv
├── rss_feeds/                   ← RSS XML for CRM integration
│   └── Nashville-Davidson.xml
└── subscriptions.db             ← SQLite database
```

---

## 🎯 **System Flow**

### 1. User Subscribes ($20/month, 7-day trial)
```
User visits → http://localhost:5002
↓
Clicks "Buy" on Nashville
↓
Stripe Checkout → Payment processed
↓
Database: subscriptions table updated
↓
Auto-scraper: Adds Nashville to daily rotation
```

### 2. Auto-Scraper Runs (4x Daily)
```
Cron triggers at 5:30 AM
↓
Scrapes all subscribed cities (Nashville, Austin, San Antonio, etc.)
↓
Filters NEW permits (SHA-256 hash check)
↓
Saves to fresh_feeds/user_id_city_timestamp.csv
↓
Emails subscriber with CSV attached
↓
Updates RSS feed for CRM integration
```

### 3. Duplicate Prevention
```
Permit scraped → Generate SHA-256 hash (address + type + date)
↓
Check seen_permits table
↓
IF duplicate → Skip
IF new → Mark as seen + deliver to subscriber
↓
Cleanup: Delete hashes older than 30 days
```

---

## 🛠️ **Setup Instructions**

### Step 1: Install Dependencies
```bash
cd /Users/briceleasure/Desktop/contractor-leads-saas

# Install Python packages
pip3 install stripe sendgrid schedule

# Or add to requirements.txt:
echo "stripe" >> requirements.txt
echo "sendgrid" >> requirements.txt
echo "schedule" >> requirements.txt
pip3 install -r requirements.txt
```

### Step 2: Configure Environment Variables
```bash
# Create .env file
cat >> .env << 'EOF'
# Stripe Configuration
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# SendGrid Email
SENDGRID_API_KEY=SG....
SENDGRID_FROM_EMAIL=leads@contractorleads.com

# Flask
FLASK_SECRET_KEY=your-secret-key-here
EOF
```

### Step 3: Initialize Database
```bash
python3 subscription_manager.py
```

**Output:**
```
======================================================================
🏗️  SUBSCRIPTION MANAGER SETUP
======================================================================
✅ Database initialized

📋 Configured Cities:
   • Nashville-Davidson          → $20.00/month (7-day trial)
   • Austin-Travis               → $20.00/month (7-day trial)
   • Chattanooga-Hamilton        → $20.00/month (7-day trial)
   • San Antonio-Bexar           → $20.00/month (7-day trial)

📂 Directories:
   • Archive Vault: /Users/briceleasure/Desktop/contractor-leads-saas/archive_vault
   • Fresh Feeds:   /Users/briceleasure/Desktop/contractor-leads-saas/fresh_feeds
   • RSS Feeds:     /Users/briceleasure/Desktop/contractor-leads-saas/rss_feeds
   • Database:      /Users/briceleasure/Desktop/contractor-leads-saas/subscriptions.db

✅ Setup complete!
```

### Step 4: Start Subscription Web App
```bash
python3 subscription_app.py
```

**Visit:** http://localhost:5002

You'll see:
- Beautiful UI with all cities
- $20/month pricing with 7-day trial
- "Buy" buttons for each city
- Real-time status (LIVE vs Coming Soon)

### Step 5: Test Auto-Scraper (Once)
```bash
python3 auto_scraper_cron.py --once
```

**Output:**
```
======================================================================
🤖 AUTO-SCRAPER RUNNING - 2025-11-19 13:50:00
======================================================================

📍 Cities to scrape: 3
   • Nashville-Davidson: 2 subscribers
   • Austin-Travis: 1 subscriber
   • San Antonio-Bexar: 1 subscriber

🕷️  Scraping Nashville-Davidson...
   ✅ Scraped 80 total permits
   🆕 Found 15 NEW permits!
   📧 Sent to user1@email.com
   📧 Sent to user2@email.com

🕷️  Scraping Austin-Travis...
   ✅ Scraped 100 total permits
   🆕 Found 22 NEW permits!
   📧 Sent to user3@email.com

🕷️  Scraping San Antonio-Bexar...
   ✅ Scraped 120 total permits
   🆕 Found 35 NEW permits!
   📧 Sent to user4@email.com

🧹 Cleaned up 147 old permit records

======================================================================
✅ Scraping complete!
======================================================================
```

### Step 6: Run Auto-Scraper as Daemon (4x Daily)
```bash
# Run in background
nohup python3 auto_scraper_cron.py --daemon > scraper.log 2>&1 &

# Or use systemd service (production):
sudo systemctl start contractor-scraper
```

---

## 📊 **Database Schema**

### `subscriptions` table:
```sql
CREATE TABLE subscriptions (
    id INTEGER PRIMARY KEY,
    user_id TEXT NOT NULL,
    email TEXT NOT NULL,
    city TEXT NOT NULL,
    stripe_customer_id TEXT,
    stripe_subscription_id TEXT,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP,
    trial_end TIMESTAMP,
    UNIQUE(user_id, city)
);
```

### `seen_permits` table:
```sql
CREATE TABLE seen_permits (
    id INTEGER PRIMARY KEY,
    city TEXT NOT NULL,
    permit_hash TEXT NOT NULL,
    permit_number TEXT,
    address TEXT,
    scraped_at TIMESTAMP,
    UNIQUE(city, permit_hash)
);
```

---

## 🎨 **UI Features**

### Subscription Page (http://localhost:5002)
- **Gradient background** - Purple/blue professional look
- **City cards** - Nashville, Austin, San Antonio, Chattanooga
- **Status badges** - "✓ LIVE" vs "Coming Soon"
- **Stats** - Avg permits/day, update frequency
- **Buy buttons** - "$20/month · 7-Day Free Trial · Cancel Anytime"
- **Feature list** - Real-time data, CSV dumps, RSS feeds, no duplicates
- **Info banner** - How it works (5 steps)

### After Purchase:
```
🎉 Subscription Activated!
Your auto-feed is now running. Expect your first permits at 5:30 AM tomorrow.
```

---

## 📧 **Email Template**

Subscribers receive:

```
Subject: 🏗️ 15 New Building Permits in Nashville-Davidson

Body:
┌──────────────────────────────────────┐
│     🏗️ Fresh Building Permits       │
│          Nashville-Davidson          │
└──────────────────────────────────────┘

You have 15 new leads!

Scraped: November 19, 2025 at 5:31 AM
City: Nashville-Davidson
New Permits: 15

Your fresh permits are attached as a CSV file. 
These are brand new leads - no duplicates, just 
opportunities scraped in the last few hours.

💡 Pro Tip: The earliest contractors usually win 
the bid. Call these leads within the hour for 
best results.

[CSV Attachment: user_12345_Nashville_20251119_053100.csv]

Next scrape: Every 4 hours (5:30 AM, 9:30 AM, 1:30 PM, 5:30 PM)
```

---

## 🔄 **Cron Schedule**

Auto-scraper runs 4x daily:
- **5:30 AM** - Morning scrape (largest batch)
- **9:30 AM** - Mid-morning scrape
- **1:30 PM** - Afternoon scrape
- **5:30 PM** - Evening scrape

Email sent immediately after each scrape (only if new permits found).

---

## 💾 **Archive Management**

### Original 70k San Antonio Dump:
```
archive_vault/San Antonio-Bexar_archive.csv
```

**Rules:**
- ✅ **NEVER DELETE** - This is the master archive
- ✅ **Preserved forever** - Historical record
- ✅ **Separate from daily feeds** - Not sent to subscribers
- ✅ **Optional download** - Available on request

### Daily Fresh Feeds:
```
fresh_feeds/user_12345_Nashville_20251119_053100.csv
```

**Rules:**
- ✅ **Only NEW permits** - Filtered against seen_permits table
- ✅ **No duplicates** - SHA-256 hash deduplication
- ✅ **Auto-emailed** - Sent immediately after scrape
- ✅ **30-day retention** - Old files auto-deleted

---

## 🚨 **Important Notes**

### 1. **No Duplicates Strategy**
- **Hash-based:** SHA-256(address + permit_type + issue_date)
- **Rolling window:** 30-day seen_permits table
- **Auto-cleanup:** Old hashes deleted daily
- **Result:** Subscribers NEVER see same permit twice

### 2. **Archive Preservation**
- **San Antonio archive:** 72,986 total permits preserved
- **Never touched by scraper** - Separate directory
- **Building permits only:** 22,519 filtered (no garage sales)
- **Available for:** Historical analysis, bulk downloads, research

### 3. **Payment Flow**
1. User clicks "Buy" → Stripe Checkout
2. Stripe processes payment → Webhook fires
3. Database updated → Subscription activated
4. Cron adds city to rotation → Auto-scraping begins
5. First email sent at 5:30 AM next day

### 4. **Cancellation**
- User cancels in Stripe dashboard
- Webhook fires → Database updated (status='cancelled')
- Cron stops scraping for that user
- No more emails sent
- Archive preserved (never deleted)

---

## 🧪 **Testing Commands**

### Test Single City Scrape:
```bash
python3 -c "
from subscription_manager import filter_new_permits, save_fresh_dump
from multi_region_scraper import scrape_all_regions

permits = scrape_all_regions(['Nashville'])
new_permits = filter_new_permits('Nashville-Davidson', permits)
csv_file = save_fresh_dump('Nashville-Davidson', 'test_user', new_permits)
print(f'Saved {len(new_permits)} new permits to {csv_file}')
"
```

### Test Email Delivery:
```bash
python3 -c "
from email_service import send_permit_email
send_permit_email(
    to_email='your@email.com',
    city='Nashville-Davidson',
    permit_count=15,
    csv_file='fresh_feeds/test.csv'
)
"
```

### Check Database:
```bash
sqlite3 subscriptions.db "SELECT * FROM subscriptions;"
sqlite3 subscriptions.db "SELECT COUNT(*) FROM seen_permits;"
```

---

## 🚀 **Production Deployment**

### 1. Set up Stripe Products:
```bash
# Create products in Stripe dashboard:
- Nashville Building Permits Feed ($20/month, 7-day trial)
- Austin Building Permits Feed ($20/month, 7-day trial)
- San Antonio Building Permits Feed ($20/month, 7-day trial)
- Chattanooga Building Permits Feed ($20/month, 7-day trial)
```

### 2. Configure Webhook:
```
Stripe Dashboard → Webhooks → Add endpoint
URL: https://yoursite.com/webhook
Events: checkout.session.completed, customer.subscription.deleted
```

### 3. Deploy Flask App:
```bash
gunicorn -w 4 -b 0.0.0.0:5002 subscription_app:app
```

### 4. Deploy Auto-Scraper:
```bash
# Systemd service
sudo cp contractor-scraper.service /etc/systemd/system/
sudo systemctl enable contractor-scraper
sudo systemctl start contractor-scraper
```

---

## 📈 **Metrics to Track**

- **Active subscribers:** SELECT COUNT(*) FROM subscriptions WHERE status='active'
- **Total revenue:** $20 × active_subscribers
- **Permits scraped:** SELECT COUNT(*) FROM seen_permits
- **Email success rate:** Check SendGrid dashboard
- **Churn rate:** Cancelled subscriptions / total subscriptions

---

## ✅ **Success Checklist**

- [ ] Stripe keys configured
- [ ] SendGrid API key set
- [ ] Database initialized
- [ ] Archive vault created (San Antonio 70k dump)
- [ ] Subscription app running (port 5002)
- [ ] Auto-scraper daemon running (4x daily)
- [ ] Test subscription completed successfully
- [ ] Test email received with CSV attachment
- [ ] Duplicate detection working (no repeat permits)
- [ ] Webhooks configured in Stripe
- [ ] Production deployment ready

---

**🎉 System Complete! Contractors get fresh leads. You get recurring revenue. Magic. 🚀**
