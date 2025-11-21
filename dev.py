#!/usr/bin/env python3
"""
Development helper - Quick commands for testing
"""
import sys
import os

def print_menu():
    print("\n" + "="*50)
    print("🏗️  CONTRACTOR LEADS - DEV MENU")
    print("="*50)
    print("\n1. Test Scrapers")
    print("2. Test AI Scorer")
    print("3. Test Email Service")
    print("4. Run Manual Job (Full Pipeline)")
    print("5. Test Database Connection")
    print("6. Check Environment Setup")
    print("7. Start Flask App")
    print("8. Start Scheduler")
    print("9. Run All Tests")
    print("0. Exit")
    print("\n" + "="*50)

def test_scrapers():
    print("\n🕷️  Testing Scrapers...")
    try:
        from scrapers import ScraperOrchestrator
        orchestrator = ScraperOrchestrator()
        permits = orchestrator.scrape_all()
        print(f"\n✅ Found {len(permits)} permits")
        if permits:
            print("\nSample permit:")
            print(permits[0])
    except Exception as e:
        print(f"❌ Error: {e}")

def test_scorer():
    print("\n🤖 Testing AI Scorer...")
    try:
        from ai_scorer import LeadScorer
        scorer = LeadScorer()
        
        test_permit = {
            'county': 'Nashville-Davidson',
            'permit_number': 'TEST-001',
            'address': '123 Broadway, Nashville, TN',
            'permit_type': 'New Construction - Commercial',
            'estimated_value': 250000,
            'work_description': 'New office building construction project'
        }
        
        scored = scorer.score_permit(test_permit)
        print(f"\n✅ Scoring successful!")
        print(f"Score: {scored['score']}/100")
        print(f"Breakdown: {scored['score_breakdown']}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_email():
    print("\n📧 Testing Email Service...")
    email = input("Enter test email address: ")
    
    try:
        from email_service import EmailService
        from datetime import datetime
        
        service = EmailService()
        test_leads = [{
            'county': 'Test County',
            'permit_number': '12345',
            'address': '123 Test St',
            'permit_type': 'New Construction',
            'estimated_value': 150000,
            'score': 85,
            'score_breakdown': {
                'size_score': 80,
                'location_score': 85,
                'urgency_score': 90,
                'type_score': 85
            }
        }]
        
        date = datetime.now().strftime('%Y-%m-%d')
        success = service.send_daily_leads(email, test_leads, date)
        
        if success:
            print("\n✅ Test email sent!")
        else:
            print("\n❌ Failed to send email")
    except Exception as e:
        print(f"❌ Error: {e}")

def run_manual_job():
    print("\n🚀 Running Manual Job...")
    confirm = input("This will scrape, score, and email. Continue? (y/n): ")
    
    if confirm.lower() == 'y':
        try:
            from scheduler import LeadScheduler
            scheduler = LeadScheduler()
            scheduler.run_nightly_job()
            print("\n✅ Job completed!")
        except Exception as e:
            print(f"❌ Error: {e}")

def test_database():
    print("\n🔥 Testing Firebase Connection...")
    try:
        from firebase_backend import FirebaseBackend
        backend = FirebaseBackend()
        print("✅ Firebase connected!")
        
        # Test read
        permits = backend.get_recent_permits(days=1)
        print(f"✅ Found {len(permits)} recent permits in database")
    except Exception as e:
        print(f"❌ Error: {e}")

def check_environment():
    print("\n⚙️  Checking Environment Setup...")
    
    # Check .env
    if os.path.exists('.env'):
        print("✅ .env file exists")
    else:
        print("❌ .env file missing")
    
    # Check firebase credentials
    if os.path.exists('firebase-credentials.json'):
        print("✅ firebase-credentials.json exists")
    else:
        print("❌ firebase-credentials.json missing")
    
    # Check imports
    packages = [
        'requests', 'bs4', 'transformers', 'firebase_admin',
        'stripe', 'flask', 'reportlab', 'schedule'
    ]
    
    print("\nPackage check:")
    for package in packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - Run: pip install -r requirements.txt")

def start_flask():
    print("\n🌐 Starting Flask App...")
    os.system('python app.py')

def start_scheduler():
    print("\n⏰ Starting Scheduler...")
    os.system('python scheduler.py')

def run_all_tests():
    print("\n🧪 Running All Tests...")
    os.system('python test_setup.py')

def main():
    while True:
        print_menu()
        choice = input("\nEnter your choice (0-9): ").strip()
        
        if choice == '1':
            test_scrapers()
        elif choice == '2':
            test_scorer()
        elif choice == '3':
            test_email()
        elif choice == '4':
            run_manual_job()
        elif choice == '5':
            test_database()
        elif choice == '6':
            check_environment()
        elif choice == '7':
            start_flask()
        elif choice == '8':
            start_scheduler()
        elif choice == '9':
            run_all_tests()
        elif choice == '0':
            print("\n👋 Goodbye!")
            sys.exit(0)
        else:
            print("\n❌ Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")

if __name__ == '__main__':
    main()
