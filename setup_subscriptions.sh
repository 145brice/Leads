#!/bin/bash
# Quick Start - Auto-Subscription System

echo "========================================================================"
echo "🚀 CONTRACTOR LEADS - AUTO-SUBSCRIPTION SYSTEM"
echo "========================================================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  Creating .env file..."
    cat > .env << 'EOF'
# Stripe Configuration (ADD YOUR KEYS)
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# SendGrid Email (ADD YOUR KEY)
SENDGRID_API_KEY=SG....
SENDGRID_FROM_EMAIL=leads@contractorleads.com

# Flask
FLASK_SECRET_KEY=dev-secret-key-change-in-production
EOF
    echo "✅ Created .env file - PLEASE ADD YOUR API KEYS!"
    echo ""
fi

# Check dependencies
echo "📦 Checking dependencies..."
python3 -c "import stripe" 2>/dev/null || echo "⚠️  Missing: stripe (pip3 install stripe)"
python3 -c "import sendgrid" 2>/dev/null || echo "⚠️  Missing: sendgrid (pip3 install sendgrid)"
python3 -c "import schedule" 2>/dev/null || echo "⚠️  Missing: schedule (pip3 install schedule)"
echo ""

# Initialize database
echo "🗄️  Initializing database..."
python3 subscription_manager.py
echo ""

# Create directories
mkdir -p archive_vault fresh_feeds rss_feeds
echo "📂 Created directories:"
echo "   • archive_vault/  (70k original dumps - NEVER DELETE)"
echo "   • fresh_feeds/    (Daily new permits only)"
echo "   • rss_feeds/      (RSS XML for CRM integration)"
echo ""

# Archive San Antonio dump
if [ -f "scraped_permits/sanantonio_20251119_134001.csv" ]; then
    echo "📦 Archiving San Antonio 70k dump..."
    cp scraped_permits/sanantonio_20251119_134001.csv archive_vault/San_Antonio-Bexar_archive.csv
    echo "✅ Archive saved: archive_vault/San_Antonio-Bexar_archive.csv"
else
    echo "ℹ️  San Antonio archive not found (will be created on first scrape)"
fi
echo ""

echo "========================================================================"
echo "✅ SETUP COMPLETE!"
echo "========================================================================"
echo ""
echo "🌐 Start subscription web app:"
echo "   python3 subscription_app.py"
echo "   Then visit: http://localhost:5002"
echo ""
echo "🤖 Test auto-scraper (once):"
echo "   python3 auto_scraper_cron.py --once"
echo ""
echo "🔄 Run auto-scraper daemon (4x daily):"
echo "   nohup python3 auto_scraper_cron.py --daemon > scraper.log 2>&1 &"
echo ""
echo "📖 Full guide:"
echo "   cat AUTO_SUBSCRIPTION_GUIDE.md"
echo ""
echo "========================================================================"
