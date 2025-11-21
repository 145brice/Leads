#!/bin/bash
cd /Users/briceleasure/Desktop/contractor-leads-saas
export FIREBASE_CREDENTIALS_PATH=firebase-credentials.json
exec /Users/briceleasure/Library/Python/3.9/bin/gunicorn -b 127.0.0.1:5008 app:app
