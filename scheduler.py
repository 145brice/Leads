"""
Nightly scheduler for scraping and sending leads
"""
import schedule
import time
from datetime import datetime
from scrapers import ScraperOrchestrator
from ai_scorer import LeadScorer
from firebase_backend import FirebaseBackend
from email_service import EmailService


class LeadScheduler:
    """Manages nightly scraping and email distribution"""
    
    def __init__(self):
        self.scraper = ScraperOrchestrator()
        self.scorer = LeadScorer()
        self.firebase = FirebaseBackend()
        self.email_service = EmailService()
    
    def run_nightly_job(self):
        """Main nightly job: scrape, score, save, and email"""
        print(f"\n{'='*50}")
        print(f"Starting nightly job at {datetime.now()}")
        print(f"{'='*50}\n")
        
        try:
            # Check if we already ran today
            today_str = datetime.now().strftime('%Y-%m-%d')
            last_run = self.firebase.get_last_scrape_date()
            
            if last_run == today_str:
                print(f"Already scraped today ({today_str}). Skipping.")
                return
            
            # Step 1: Scrape permits from all counties
            print("Step 1: Scraping permits...")
            permits = self.scraper.scrape_all()
            
            if not permits:
                print("No permits found. Exiting.")
                return
            
            # Step 2: Score permits with AI
            print(f"\nStep 2: Scoring {len(permits)} permits with AI...")
            scored_permits = self.scorer.score_batch(permits)
            
            # Step 3: Get top 10 leads
            top_leads = scored_permits[:10]
            print(f"\nStep 3: Top 10 leads identified")
            for i, lead in enumerate(top_leads, 1):
                print(f"  {i}. {lead['county']} - Score: {lead['score']}")
            
            # Step 4: Save to Firebase
            print("\nStep 4: Saving permits to database...")
            batch_id = datetime.now().strftime('%Y%m%d_%H%M%S')
            self.firebase.save_permits(scored_permits, batch_id)
            
            # Save daily leads
            date_str = datetime.now().strftime('%Y-%m-%d')
            self.firebase.save_daily_leads(date_str, top_leads)
            
            # Update last scrape date
            self.firebase.update_last_scrape_date(date_str)
            
            # Step 5: Send emails to active subscribers
            print("\nStep 5: Sending emails to subscribers...")
            subscribers = self.firebase.get_active_subscribers()
            print(f"Found {len(subscribers)} active subscribers")
            
            success_count = 0
            for subscriber in subscribers:
                email = subscriber.get('email')
                if email:
                    if self.email_service.send_daily_leads(email, top_leads, date_str):
                        success_count += 1
            
            print(f"\nJob completed successfully!")
            print(f"Emails sent: {success_count}/{len(subscribers)}")
            print(f"{'='*50}\n")
        
        except Exception as e:
            print(f"Error in nightly job: {e}")
            import traceback
            traceback.print_exc()
    
    def start_scheduler(self, run_time: str = "07:00"):
        """Start the scheduler - only runs at scheduled time, no startup execution"""
        print(f"Scheduler started. Job will run daily at {run_time}")
        print("No startup scraping - waits for scheduled time.")
        
        # Schedule the job - NO immediate execution on startup
        schedule.every().day.at(run_time).do(self.run_nightly_job)
        
        # Keep running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute


def main():
    """Entry point for scheduler"""
    import config
    
    scheduler = LeadScheduler()
    scheduler.start_scheduler(config.SCRAPE_TIME)


if __name__ == '__main__':
    main()
