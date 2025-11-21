"""
Database module for Contractor Leads SaaS
Handles user accounts, subscriptions, and payments
"""

import os
import sqlite3
import hashlib
import secrets
from datetime import datetime, timedelta
from contextlib import contextmanager

DATABASE_PATH = os.getenv('DATABASE_PATH', 'contractor_leads.db')

@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_database():
    """Initialize database with required tables"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT,
                stripe_customer_id TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                email_verified BOOLEAN DEFAULT 0
            )
        ''')
        
        # Subscriptions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                county_key TEXT NOT NULL,
                state_key TEXT NOT NULL,
                stripe_subscription_id TEXT UNIQUE,
                status TEXT DEFAULT 'active',
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                cancelled_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE(user_id, county_key, state_key)
            )
        ''')
        
        # Payments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                stripe_payment_intent_id TEXT UNIQUE,
                stripe_invoice_id TEXT,
                amount INTEGER NOT NULL,
                currency TEXT DEFAULT 'usd',
                status TEXT DEFAULT 'pending',
                county_key TEXT,
                state_key TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Sessions table for authentication
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_token TEXT UNIQUE NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Email queue table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                email_type TEXT NOT NULL,
                subject TEXT,
                body TEXT,
                status TEXT DEFAULT 'pending',
                scheduled_for TIMESTAMP,
                sent_at TIMESTAMP,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        print("✅ Database initialized successfully")

# User management functions
def create_user(email, password, full_name=None):
    """Create a new user account"""
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO users (email, password_hash, full_name) VALUES (?, ?, ?)',
                (email.lower(), password_hash, full_name)
            )
            user_id = cursor.lastrowid
            return user_id
        except sqlite3.IntegrityError:
            return None  # Email already exists

def get_user_by_email(email):
    """Get user by email address"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email.lower(),))
        return cursor.fetchone()

def get_user_by_id(user_id):
    """Get user by ID"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        return cursor.fetchone()

def verify_password(email, password):
    """Verify user password"""
    user = get_user_by_email(email)
    if not user:
        return None
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    if password_hash == user['password_hash']:
        return user
    return None

def update_stripe_customer_id(user_id, stripe_customer_id):
    """Update user's Stripe customer ID"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE users SET stripe_customer_id = ? WHERE id = ?',
            (stripe_customer_id, user_id)
        )

# Session management
def create_session(user_id, expires_in_days=30):
    """Create a new session for user"""
    session_token = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(days=expires_in_days)
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO sessions (user_id, session_token, expires_at) VALUES (?, ?, ?)',
            (user_id, session_token, expires_at)
        )
    
    return session_token

def get_session(session_token):
    """Get session and check if valid"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM sessions WHERE session_token = ? AND expires_at > ?',
            (session_token, datetime.now())
        )
        return cursor.fetchone()

def delete_session(session_token):
    """Delete a session (logout)"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM sessions WHERE session_token = ?', (session_token,))

# Subscription management
def create_subscription(user_id, state_key, county_key, stripe_subscription_id):
    """Create a new subscription"""
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                '''INSERT INTO subscriptions 
                   (user_id, state_key, county_key, stripe_subscription_id, status)
                   VALUES (?, ?, ?, ?, 'active')''',
                (user_id, state_key, county_key, stripe_subscription_id)
            )
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None  # Subscription already exists

def get_user_subscriptions(user_id):
    """Get all active subscriptions for a user"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''SELECT * FROM subscriptions 
               WHERE user_id = ? AND status = 'active' 
               ORDER BY started_at DESC''',
            (user_id,)
        )
        return cursor.fetchall()

def has_access_to_county(user_id, state_key, county_key):
    """Check if user has active subscription to a county"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''SELECT COUNT(*) as count FROM subscriptions 
               WHERE user_id = ? AND state_key = ? AND county_key = ? 
               AND status = 'active' ''',
            (user_id, state_key, county_key)
        )
        result = cursor.fetchone()
        return result['count'] > 0

def cancel_subscription(subscription_id):
    """Cancel a subscription"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''UPDATE subscriptions 
               SET status = 'cancelled', cancelled_at = ? 
               WHERE id = ?''',
            (datetime.now(), subscription_id)
        )

def update_subscription_status(stripe_subscription_id, status):
    """Update subscription status from Stripe webhook"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE subscriptions SET status = ? WHERE stripe_subscription_id = ?',
            (status, stripe_subscription_id)
        )

# Payment tracking
def record_payment(user_id, amount, stripe_payment_intent_id, state_key=None, county_key=None):
    """Record a payment"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO payments 
               (user_id, stripe_payment_intent_id, amount, status, state_key, county_key)
               VALUES (?, ?, ?, 'succeeded', ?, ?)''',
            (user_id, stripe_payment_intent_id, amount, state_key, county_key)
        )
        return cursor.lastrowid

def get_user_payments(user_id):
    """Get all payments for a user"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM payments WHERE user_id = ? ORDER BY created_at DESC',
            (user_id,)
        )
        return cursor.fetchall()

# Email queue management
def queue_email(user_id, email_type, subject, body, scheduled_for=None):
    """Add email to queue"""
    if scheduled_for is None:
        scheduled_for = datetime.now()
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO email_queue 
               (user_id, email_type, subject, body, scheduled_for)
               VALUES (?, ?, ?, ?, ?)''',
            (user_id, email_type, subject, body, scheduled_for)
        )
        return cursor.lastrowid

def get_pending_emails():
    """Get emails ready to send"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''SELECT * FROM email_queue 
               WHERE status = 'pending' AND scheduled_for <= ?
               ORDER BY scheduled_for ASC''',
            (datetime.now(),)
        )
        return cursor.fetchall()

def mark_email_sent(email_id):
    """Mark email as sent"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''UPDATE email_queue 
               SET status = 'sent', sent_at = ?
               WHERE id = ?''',
            (datetime.now(), email_id)
        )

def mark_email_failed(email_id, error_message):
    """Mark email as failed"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''UPDATE email_queue 
               SET status = 'failed', error_message = ?
               WHERE id = ?''',
            (error_message, email_id)
        )

# Admin functions
def get_all_users():
    """Get all users (admin only)"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users ORDER BY created_at DESC')
        return cursor.fetchall()

def get_subscription_stats():
    """Get subscription statistics"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Get total counts
        cursor.execute('SELECT COUNT(*) FROM subscriptions')
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM subscriptions WHERE status = 'active'")
        active = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM subscriptions WHERE status = 'cancelled'")
        cancelled = cursor.fetchone()[0]
        
        return {
            'total_subscriptions': total,
            'active_subscriptions': active,
            'cancelled_subscriptions': cancelled
        }

if __name__ == '__main__':
    # Initialize database
    print("🔧 Initializing database...")
    init_database()
    
    # Create a test user
    print("\n📝 Creating test user...")
    user_id = create_user('test@example.com', 'password123', 'Test User')
    if user_id:
        print(f"✅ Test user created with ID: {user_id}")
    else:
        print("⚠️  Test user already exists")
    
    print("\n✅ Database setup complete!")
    print(f"📍 Database location: {DATABASE_PATH}")
