# Vercel serverless function handler
import sys
import os

# Add parent directory to Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from app import app
    handler = app
except Exception as e:
    # Create error handler to see what's wrong
    from flask import Flask, Response
    error_app = Flask(__name__)
    
    @error_app.route('/', defaults={'path': ''})
    @error_app.route('/<path:path>')
    def error_handler(path):
        error_msg = f"Error importing app: {str(e)}\nType: {type(e).__name__}\nPath: {parent_dir}"
        return Response(error_msg, status=500, mimetype='text/plain')
    
    handler = error_app
