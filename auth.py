"""
Authentication module for Contractor Leads SaaS
"""

from functools import wraps
from flask import session, redirect, url_for, request
import database

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def subscription_required(state_key, county_key):
    """Decorator to require active subscription for specific county"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login', next=request.url))
            
            user_id = session['user_id']
            if not database.has_access_to_county(user_id, state_key, county_key):
                return redirect(url_for('signup'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_current_user():
    """Get current logged-in user"""
    if 'user_id' in session:
        return database.get_user_by_id(session['user_id'])
    return None
