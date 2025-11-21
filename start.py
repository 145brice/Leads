#!/usr/bin/env python3
"""
Startup script for Contractor Leads - ensures correct port
"""
import os
import sys

# Change to the correct directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Set the port explicitly
os.environ['PORT'] = '5002'

# Now import and run the app
import app as contractor_app

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🏗️  CONTRACTOR LEADS - Starting on PORT 5002")
    print("="*60)
    print(f"📂 Working Directory: {os.getcwd()}")
    print(f"🌐 URL: http://localhost:5002")
    print("="*60 + "\n")
    
    contractor_app.app.run(host='0.0.0.0', port=5002, debug=True)
