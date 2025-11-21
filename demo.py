#!/usr/bin/env python3
"""
Simple demo server - Landing page only (no Firebase/Stripe needed)
"""
from flask import Flask, render_template
import os

app = Flask(__name__)
app.secret_key = 'demo-key-for-testing'

@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')

if __name__ == '__main__':
    port = 5002
    print("\n" + "="*60)
    print("🏗️  CONTRACTOR LEADS - DEMO MODE (Landing Page Only)")
    print("="*60)
    print(f"🌐 Open in browser: http://localhost:{port}")
    print("="*60)
    print("\n✅ This is a demo showing the landing page")
    print("⚠️  Full app requires Firebase/Stripe credentials")
    print("📖 See QUICKSTART.md for setup instructions\n")
    
    app.run(host='0.0.0.0', port=port, debug=True)
