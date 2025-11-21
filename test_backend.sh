#!/bin/bash
# Quick Test Script - Test the full backend flow

echo "🧪 Testing Contractor Leads Backend"
echo "===================================="
echo ""

cd /Users/briceleasure/Desktop/contractor-leads-saas

# 1. Check database
echo "1️⃣  Checking database..."
if [ -f "contractor_leads.db" ]; then
    echo "   ✅ Database exists"
else
    echo "   ❌ Database not found"
    exit 1
fi

# 2. Check test user
echo ""
echo "2️⃣  Checking test user..."
python3 -c "
import database
user = database.get_user_by_email('test@example.com')
if user:
    print('   ✅ Test user found:', user['email'])
else:
    print('   ❌ Test user not found')
" || echo "   ❌ Failed to check user"

# 3. Check subscriptions
echo ""
echo "3️⃣  Checking subscriptions..."
python3 -c "
import database
stats = database.get_subscription_stats()
print(f'   ✅ Total subscriptions: {stats[\"total_subscriptions\"]}')
print(f'   ✅ Active subscriptions: {stats[\"active_subscriptions\"]}')
" || echo "   ❌ Failed to check subscriptions"

# 4. Check leads
echo ""
echo "4️⃣  Checking leads..."
python3 -c "
import json
with open('leads_db/current_leads.json') as f:
    data = json.load(f)
    leads = data.get('leads', {})
    total = sum(len(county) for state in leads.values() for county in state.values())
    print(f'   ✅ Total leads: {total:,}')
" || echo "   ❌ Failed to check leads"

# 5. Test email simulation
echo ""
echo "5️⃣  Testing email delivery (simulation)..."
python3 email_sender.py 2>&1 | grep -E "(Sent:|Failed:|Total:)" || echo "   ❌ Email test failed"

echo ""
echo "===================================="
echo "✅ Backend Test Complete!"
echo ""
echo "🌐 Start the app with:"
echo "   python3 app_backend.py"
echo ""
echo "📧 Test account:"
echo "   Email: test@example.com"
echo "   Password: password123"
echo ""
echo "🔧 Admin panel:"
echo "   python3 admin_panel.py"
echo ""
