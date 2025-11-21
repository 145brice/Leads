"""
Quick test script to verify all components
"""
import sys


def test_imports():
    """Test all imports"""
    print("Testing imports...")
    
    try:
        import requests
        print("✓ requests")
    except ImportError:
        print("✗ requests - Run: pip install requests")
        return False
    
    try:
        from bs4 import BeautifulSoup
        print("✓ beautifulsoup4")
    except ImportError:
        print("✗ beautifulsoup4 - Run: pip install beautifulsoup4")
        return False
    
    try:
        import transformers
        print("✓ transformers")
    except ImportError:
        print("✗ transformers - Run: pip install transformers")
        return False
    
    try:
        import firebase_admin
        print("✓ firebase-admin")
    except ImportError:
        print("✗ firebase-admin - Run: pip install firebase-admin")
        return False
    
    try:
        import stripe
        print("✓ stripe")
    except ImportError:
        print("✗ stripe - Run: pip install stripe")
        return False
    
    try:
        import flask
        print("✓ flask")
    except ImportError:
        print("✗ flask - Run: pip install flask")
        return False
    
    try:
        from reportlab.lib.pagesizes import letter
        print("✓ reportlab")
    except ImportError:
        print("✗ reportlab - Run: pip install reportlab")
        return False
    
    try:
        import schedule
        print("✓ schedule")
    except ImportError:
        print("✗ schedule - Run: pip install schedule")
        return False
    
    return True


def test_config():
    """Test configuration"""
    print("\nTesting configuration...")
    
    import os
    if not os.path.exists('.env'):
        print("⚠️  .env file not found. Copy .env.example to .env and configure it.")
        return False
    
    print("✓ .env file exists")
    return True


def test_scrapers():
    """Test scraper structure"""
    print("\nTesting scrapers...")
    
    try:
        from scrapers import ScraperOrchestrator
        orchestrator = ScraperOrchestrator()
        print(f"✓ Loaded {len(orchestrator.scrapers)} county scrapers")
        return True
    except Exception as e:
        print(f"✗ Error loading scrapers: {e}")
        return False


def test_ai_scorer():
    """Test AI scorer"""
    print("\nTesting AI scorer...")
    
    try:
        from ai_scorer import LeadScorer
        print("Loading AI model (this may take a minute)...")
        scorer = LeadScorer()
        print("✓ AI model loaded successfully")
        
        # Test scoring
        test_permit = {
            'county': 'Test',
            'permit_number': '12345',
            'address': '123 Main St, Nashville',
            'permit_type': 'New Construction',
            'estimated_value': 150000,
            'work_description': 'New commercial building construction'
        }
        
        scored = scorer.score_permit(test_permit)
        print(f"✓ Test permit scored: {scored['score']}/100")
        return True
    except Exception as e:
        print(f"✗ Error with AI scorer: {e}")
        return False


def main():
    """Run all tests"""
    print("="*50)
    print("Contractor Leads SaaS - Component Test")
    print("="*50)
    print()
    
    all_passed = True
    
    if not test_imports():
        all_passed = False
        print("\n⚠️  Install missing packages: pip install -r requirements.txt")
    
    if not test_config():
        all_passed = False
    
    if not test_scrapers():
        all_passed = False
    
    if not test_ai_scorer():
        all_passed = False
    
    print("\n" + "="*50)
    if all_passed:
        print("✅ All tests passed!")
        print("Your system is ready to run.")
        print("\nNext: Configure .env and run:")
        print("  python app.py")
        print("  python scheduler.py")
    else:
        print("❌ Some tests failed. Fix issues above.")
    print("="*50)


if __name__ == '__main__':
    main()
