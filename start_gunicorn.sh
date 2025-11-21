#!/bin/bash
cd /Users/briceleasure/Desktop/contractor-leads-saas
PYTHONPATH=/Users/briceleasure/Desktop/contractor-leads-saas python3 -m gunicorn --bind 127.0.0.1:5008 app:app
