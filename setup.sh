#!/bin/bash

# Setup script for Contractor Leads SaaS

echo "🏗️  Setting up Contractor Leads SaaS..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your credentials"
else
    echo "✓ .env file already exists"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your Firebase, Stripe, and email credentials"
echo "2. Place firebase-credentials.json in project root"
echo "3. Run: python app.py (Flask app)"
echo "4. Run: python scheduler.py (Nightly jobs)"
echo ""
echo "Visit: http://localhost:5000"
