#!/bin/bash
# Script to run Contractor Leads SaaS with Gunicorn

cd /Users/briceleasure/Desktop/contractor-leads-saas
export PYTHONPATH=/Users/briceleasure/Desktop/contractor-leads-saas
exec /Users/briceleasure/Library/Python/3.9/bin/gunicorn --bind 127.0.0.1:5008 app:app
