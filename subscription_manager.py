#!/usr/bin/env python3
"""
Subscription Manager - Stripe + Auto-Scraper System
Handles: Payments, User Subscriptions, Duplicate Detection, Auto-Feeding
"""
import os
import sqlite3
import hashlib
import stripe
from datetime import datetime, timedelta
from pathlib import Path
import json

# Stripe configuration
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

# Directory structure
BASE_DIR = Path(__file__).parent
ARCHIVE_DIR = BASE_DIR / "archive_vault"  # 70k original dumps - NEVER DELETE
FRESH_DIR = BASE_DIR / "fresh_feeds"      # Daily new permits only
RSS_DIR = BASE_DIR / "rss_feeds"          # RSS XML files per city
DB_PATH = BASE_DIR / "subscriptions.db"

# Create directories
ARCHIVE_DIR.mkdir(exist_ok=True)
FRESH_DIR.mkdir(exist_ok=True)
RSS_DIR.mkdir(exist_ok=True)


# ==================== STRIPE PRODUCTS ====================

CITY_PRODUCTS = {
    'Nashville-Davidson': {
        'name': 'Nashville Building Permits Feed',
        'price': 2000,  # $20.00 in cents
        'trial_days': 7,
        'description': 'Live building permits from Nashville-Davidson County - 4x daily updates'
    },
    'Austin-Travis': {
        'name': 'Austin Building Permits Feed',
        'price': 2000,
        'trial_days': 7,
        'description': 'Live building permits from Austin-Travis County - 4x daily updates'
    },
    'Chattanooga-Hamilton': {
        'name': 'Chattanooga Building Permits Feed',
        'price': 2000,
        'trial_days': 7,
        'description': 'Live building permits from Chattanooga-Hamilton County - 4x daily updates'
    },
    'San Antonio-Bexar': {
        'name': 'San Antonio Building Permits Feed',
        'price': 2000,
        'trial_days': 7,
        'description': 'Live building permits from San Antonio-Bexar County - 4x daily updates'
    },
    'Dallas-Dallas': {
        'name': 'Dallas Building Permits Feed',
        'price': 2000,
        'trial_days': 7,
        'description': 'Live building permits from Dallas County - 4x daily updates'
    },
    'Houston-Harris': {
        'name': 'Houston Building Permits Feed',
        'price': 2000,
        'trial_days': 7,
        'description': 'Live building permits from Houston-Harris County - 4x daily updates'
    },
    'Memphis-Shelby': {
        'name': 'Memphis Building Permits Feed',
        'price': 2000,
        'trial_days': 7,
        'description': 'Live building permits from Memphis-Shelby County - 4x daily updates'
    },
    'Knoxville-Knox': {
        'name': 'Knoxville Building Permits Feed',
        'price': 2000,
        'trial_days': 7,
        'description': 'Live building permits from Knoxville-Knox County - 4x daily updates'
    }
}


# ==================== DATABASE SETUP ====================

def init_database():
    """Initialize SQLite database for subscriptions and seen permits"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Subscriptions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            email TEXT NOT NULL,
            city TEXT NOT NULL,
            stripe_customer_id TEXT,
            stripe_subscription_id TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            trial_end TIMESTAMP,
            UNIQUE(user_id, city)
        )
    ''')
    
    # Seen permits table (30-day rolling window)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS seen_permits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT NOT NULL,
            permit_hash TEXT NOT NULL,
            permit_number TEXT,
            address TEXT,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(city, permit_hash)
        )
    ''')
    
    # Index for fast lookups
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_permit_hash ON seen_permits(city, permit_hash)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_scraped_at ON seen_permits(scraped_at)')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized")


# ==================== DUPLICATE DETECTION ====================

def generate_permit_hash(permit):
    """Generate SHA-256 hash for duplicate detection"""
    # Hash based on: address + permit_type + issue_date
    key_fields = f"{permit.get('address', '')}|{permit.get('permit_type', '')}|{permit.get('issue_date', '')}"
    return hashlib.sha256(key_fields.encode()).hexdigest()


def is_duplicate(city, permit_hash):
    """Check if permit hash exists in seen table"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT id FROM seen_permits WHERE city = ? AND permit_hash = ?', (city, permit_hash))
    result = cursor.fetchone()
    conn.close()
    
    return result is not None


def mark_as_seen(city, permit):
    """Add permit to seen table"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    permit_hash = generate_permit_hash(permit)
    
    try:
        cursor.execute('''
            INSERT INTO seen_permits (city, permit_hash, permit_number, address)
            VALUES (?, ?, ?, ?)
        ''', (city, permit_hash, permit.get('permit_number', ''), permit.get('address', '')))
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # Already exists
    
    conn.close()


def cleanup_old_seen_permits(days=30):
    """Remove seen permits older than X days (rolling window)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cutoff = datetime.now() - timedelta(days=days)
    cursor.execute('DELETE FROM seen_permits WHERE scraped_at < ?', (cutoff,))
    deleted = cursor.rowcount
    
    conn.commit()
    conn.close()
    
    return deleted


def filter_new_permits(city, permits):
    """Filter out duplicates, return only new permits"""
    new_permits = []
    
    for permit in permits:
        permit_hash = generate_permit_hash(permit)
        
        if not is_duplicate(city, permit_hash):
            new_permits.append(permit)
            mark_as_seen(city, permit)
    
    return new_permits


# ==================== STRIPE CHECKOUT ====================

def create_checkout_session(city, user_email, success_url, cancel_url):
    """Create Stripe checkout session for city subscription"""
    
    if city not in CITY_PRODUCTS:
        raise ValueError(f"Unknown city: {city}")
    
    product = CITY_PRODUCTS[city]
    
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': product['name'],
                        'description': product['description'],
                    },
                    'unit_amount': product['price'],
                    'recurring': {
                        'interval': 'month',
                    },
                },
                'quantity': 1,
            }],
            mode='subscription',
            customer_email=user_email,
            subscription_data={
                'trial_period_days': product['trial_days'],
                'metadata': {
                    'city': city
                }
            },
            success_url=success_url + f'?session_id={{CHECKOUT_SESSION_ID}}&city={city}',
            cancel_url=cancel_url,
        )
        
        return session
        
    except Exception as e:
        print(f"❌ Stripe error: {e}")
        raise


def handle_successful_payment(session_id):
    """Handle successful Stripe payment - activate subscription"""
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        
        city = session['subscription_data']['metadata']['city']
        customer_id = session['customer']
        subscription_id = session['subscription']
        customer_email = session['customer_email']
        
        # Get trial end date
        subscription = stripe.Subscription.retrieve(subscription_id)
        trial_end = datetime.fromtimestamp(subscription['trial_end']) if subscription.get('trial_end') else None
        
        # Save to database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        user_id = f"user_{customer_id[:8]}"
        
        cursor.execute('''
            INSERT OR REPLACE INTO subscriptions 
            (user_id, email, city, stripe_customer_id, stripe_subscription_id, status, trial_end)
            VALUES (?, ?, ?, ?, ?, 'active', ?)
        ''', (user_id, customer_email, city, customer_id, subscription_id, trial_end))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Subscription activated: {customer_email} → {city}")
        
        return {
            'user_id': user_id,
            'city': city,
            'email': customer_email,
            'trial_end': trial_end
        }
        
    except Exception as e:
        print(f"❌ Payment handling error: {e}")
        raise


# ==================== SUBSCRIPTION MANAGEMENT ====================

def get_active_subscribers(city=None):
    """Get all active subscribers (optionally filtered by city)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if city:
        cursor.execute('SELECT * FROM subscriptions WHERE city = ? AND status = "active"', (city,))
    else:
        cursor.execute('SELECT * FROM subscriptions WHERE status = "active"')
    
    subscribers = cursor.fetchall()
    conn.close()
    
    return subscribers


def get_user_cities(user_id):
    """Get all cities a user is subscribed to"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT city FROM subscriptions WHERE user_id = ? AND status = "active"', (user_id,))
    cities = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    return cities


def cancel_subscription(user_id, city):
    """Cancel a user's subscription to a city"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT stripe_subscription_id FROM subscriptions 
        WHERE user_id = ? AND city = ?
    ''', (user_id, city))
    
    result = cursor.fetchone()
    if result:
        subscription_id = result[0]
        
        # Cancel in Stripe
        try:
            stripe.Subscription.delete(subscription_id)
        except Exception as e:
            print(f"⚠️  Stripe cancellation error: {e}")
        
        # Update database
        cursor.execute('''
            UPDATE subscriptions 
            SET status = 'cancelled' 
            WHERE user_id = ? AND city = ?
        ''', (user_id, city))
        
        conn.commit()
    
    conn.close()


# ==================== ARCHIVE MANAGEMENT ====================

def save_to_archive(city, permits):
    """Save original 70k dump to archive vault - NEVER DELETE"""
    archive_file = ARCHIVE_DIR / f"{city}_archive.csv"
    
    if archive_file.exists():
        print(f"   ℹ️  Archive already exists: {archive_file}")
        return archive_file
    
    import csv
    
    if not permits:
        return None
    
    with open(archive_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=permits[0].keys())
        writer.writeheader()
        writer.writerows(permits)
    
    print(f"   ✅ Archive saved: {archive_file} ({len(permits)} permits)")
    return archive_file


def get_archive_path(city):
    """Get path to city's archive vault"""
    return ARCHIVE_DIR / f"{city}_archive.csv"


# ==================== FRESH FEED MANAGEMENT ====================

def save_fresh_dump(city, user_id, new_permits):
    """Save new permits to user's fresh feed CSV"""
    if not new_permits:
        return None
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    fresh_file = FRESH_DIR / f"{user_id}_{city}_{timestamp}.csv"
    
    import csv
    
    with open(fresh_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=new_permits[0].keys())
        writer.writeheader()
        writer.writerows(new_permits)
    
    print(f"   ✅ Fresh dump: {fresh_file} ({len(new_permits)} new permits)")
    return fresh_file


# ==================== MAIN ====================

if __name__ == "__main__":
    print("="*70)
    print("🏗️  SUBSCRIPTION MANAGER SETUP")
    print("="*70)
    
    # Initialize database
    init_database()
    
    print("\n📋 Configured Cities:")
    for city, product in CITY_PRODUCTS.items():
        print(f"   • {city:30} → ${product['price']/100:.2f}/month (7-day trial)")
    
    print(f"\n📂 Directories:")
    print(f"   • Archive Vault: {ARCHIVE_DIR}")
    print(f"   • Fresh Feeds:   {FRESH_DIR}")
    print(f"   • RSS Feeds:     {RSS_DIR}")
    print(f"   • Database:      {DB_PATH}")
    
    print("\n✅ Setup complete!")
