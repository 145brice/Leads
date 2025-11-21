#!/bin/bash
# Setup Cron Jobs for Contractor Leads

echo "⏰ Setting up cron jobs for Contractor Leads"
echo "==========================================="
echo ""

PROJECT_DIR="/Users/briceleasure/Desktop/contractor-leads-saas"
PYTHON_PATH="/usr/bin/python3"

# Create logs directory
mkdir -p "$PROJECT_DIR/logs"

# Create temporary cron file
TEMP_CRON=$(mktemp)

# Get existing crontab (if any)
crontab -l 2>/dev/null > "$TEMP_CRON" || true

# Remove old contractor leads cron jobs (if any)
sed -i '' '/Contractor Leads/d' "$TEMP_CRON" 2>/dev/null || sed -i '/Contractor Leads/d' "$TEMP_CRON"
sed -i '' '/incremental_scraper.py/d' "$TEMP_CRON" 2>/dev/null || sed -i '/incremental_scraper.py/d' "$TEMP_CRON"
sed -i '' '/email_sender.py/d' "$TEMP_CRON" 2>/dev/null || sed -i '/email_sender.py/d' "$TEMP_CRON"

# Add new cron jobs
cat >> "$TEMP_CRON" << EOF

# Contractor Leads - Daily Scraping at 1:00 AM
0 1 * * * cd $PROJECT_DIR && $PYTHON_PATH incremental_scraper.py >> $PROJECT_DIR/logs/scraper.log 2>&1

# Contractor Leads - Daily Emails at 6:00 AM
0 6 * * * cd $PROJECT_DIR && $PYTHON_PATH email_sender.py >> $PROJECT_DIR/logs/email.log 2>&1

EOF

# Install new crontab
crontab "$TEMP_CRON"

# Clean up
rm "$TEMP_CRON"

echo "✅ Cron jobs installed successfully!"
echo ""
echo "📋 Scheduled tasks:"
echo "   • Daily scraping: 1:00 AM"
echo "   • Daily emails: 6:00 AM"
echo ""
echo "📂 Logs location:"
echo "   $PROJECT_DIR/logs/"
echo ""
echo "🔍 View cron jobs:"
echo "   crontab -l"
echo ""
echo "📊 Monitor logs:"
echo "   tail -f $PROJECT_DIR/logs/scraper.log"
echo "   tail -f $PROJECT_DIR/logs/email.log"
echo ""
