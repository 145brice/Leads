#!/bin/bash
# Production Deployment Script for Contractor Leads SaaS

set -e  # Exit on error

echo "🚀 Deploying Contractor Leads to Production"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${RED}❌ .env file not found!${NC}"
    echo "Copy .env.template to .env and fill in your values:"
    echo "  cp .env.template .env"
    echo "  nano .env"
    exit 1
fi

# Load environment variables
source .env

# Check required variables
if [ -z "$SECRET_KEY" ] || [ "$SECRET_KEY" == "your-secret-key-here" ]; then
    echo -e "${RED}❌ SECRET_KEY not set in .env${NC}"
    echo "Generate one with: python3 -c \"import secrets; print(secrets.token_hex(32))\""
    exit 1
fi

if [ -z "$SENDGRID_API_KEY" ] || [ "$SENDGRID_API_KEY" == "SG.your_sendgrid_api_key_here" ]; then
    echo -e "${YELLOW}⚠️  SENDGRID_API_KEY not set - emails will not work${NC}"
fi

if [ -z "$STRIPE_WEBHOOK_SECRET" ] || [ "$STRIPE_WEBHOOK_SECRET" == "whsec_your_webhook_secret_here" ]; then
    echo -e "${YELLOW}⚠️  STRIPE_WEBHOOK_SECRET not set - webhooks will not work${NC}"
fi

echo "✅ Environment variables loaded"
echo ""

# Install dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt --quiet 2>/dev/null || {
    echo "Creating requirements.txt..."
    cat > requirements.txt << EOF
Flask==3.0.0
sendgrid==6.11.0
gunicorn==21.2.0
EOF
    pip3 install -r requirements.txt --quiet
}
echo "✅ Dependencies installed"
echo ""

# Initialize database
echo "💾 Initializing database..."
python3 database.py > /dev/null 2>&1
echo "✅ Database ready"
echo ""

# Test the application
echo "🧪 Testing application..."
python3 -c "
import app_backend
import database

# Test database connection
try:
    user = database.get_user_by_email('test@example.com')
    print('✅ Database connection works')
except Exception as e:
    print(f'❌ Database error: {e}')
    exit(1)

# Test leads loading
try:
    leads = app_backend.load_leads()
    total = sum(len(county) for state in leads.values() for county in state.values())
    print(f'✅ Leads loaded: {total:,} total')
except Exception as e:
    print(f'❌ Leads loading error: {e}')
    exit(1)
"
echo ""

# Check if gunicorn is available
if command -v gunicorn &> /dev/null; then
    echo "✅ Gunicorn is installed"
    
    # Test gunicorn
    echo "🧪 Testing Gunicorn..."
    timeout 3 gunicorn -w 1 -b 127.0.0.1:5004 --timeout 2 app_backend:app &> /dev/null &
    GUNICORN_PID=$!
    sleep 2
    if kill -0 $GUNICORN_PID 2>/dev/null; then
        echo "✅ Gunicorn test passed"
        kill $GUNICORN_PID 2>/dev/null
    else
        echo "⚠️  Gunicorn test failed"
    fi
else
    echo "⚠️  Gunicorn not found, installing..."
    pip3 install gunicorn
fi
echo ""

# Create systemd service file (Linux only)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "🔧 Creating systemd service..."
    cat > contractor-leads.service << EOF
[Unit]
Description=Contractor Leads SaaS
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment="PATH=$(which python3):$PATH"
EnvironmentFile=$(pwd)/.env
ExecStart=$(which gunicorn) -w 4 -b 0.0.0.0:5003 --timeout 120 app_backend:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF
    echo "✅ Service file created: contractor-leads.service"
    echo "   Install with: sudo cp contractor-leads.service /etc/systemd/system/"
    echo "   Enable with: sudo systemctl enable contractor-leads"
    echo "   Start with: sudo systemctl start contractor-leads"
fi
echo ""

# Create cron jobs
echo "⏰ Setting up cron jobs..."
cat > cron_jobs.txt << EOF
# Contractor Leads - Daily Scraping (1 AM)
0 1 * * * cd $(pwd) && /usr/bin/python3 incremental_scraper.py >> $(pwd)/logs/scraper.log 2>&1

# Contractor Leads - Daily Emails (6 AM)
0 6 * * * cd $(pwd) && /usr/bin/python3 email_sender.py >> $(pwd)/logs/email.log 2>&1
EOF

echo "✅ Cron jobs configuration created: cron_jobs.txt"
echo "   Install with: crontab -e"
echo "   Then paste the contents of cron_jobs.txt"
echo ""

# Create logs directory
mkdir -p logs
echo "✅ Logs directory created"
echo ""

# Print deployment summary
echo "=========================================="
echo -e "${GREEN}✅ Deployment preparation complete!${NC}"
echo "=========================================="
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Configure Stripe metadata (see stripe_metadata_config.md)"
echo ""
echo "2. Start the application:"
echo "   Production: gunicorn -w 4 -b 0.0.0.0:5003 --timeout 120 app_backend:app"
echo "   Development: python3 app_backend.py"
echo ""
echo "3. Set up cron jobs:"
echo "   crontab -e"
echo "   # Paste contents from cron_jobs.txt"
echo ""
echo "4. Test Stripe webhooks with CLI:"
echo "   stripe listen --forward-to localhost:5003/stripe/webhook"
echo ""
echo "5. Access the application:"
echo "   http://localhost:5003"
echo ""
echo "📧 SendGrid: ${SENDGRID_API_KEY:0:10}..."
echo "🔐 Stripe: ${STRIPE_WEBHOOK_SECRET:0:10}..."
echo "🔑 Secret Key: Set ✓"
echo ""
