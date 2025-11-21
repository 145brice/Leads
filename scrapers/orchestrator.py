
"""
Scraper orchestrator - runs all county scrapers
"""
from typing import List, Dict
from .nashville_scraper import NashvilleDavidsonScraper
from .rutherford_scraper import RutherfordScraper
from .wilson_scraper import WilsonScraper
from .sumner_scraper import SumnerScraper
from .harris_scraper import HarrisScraper


class ScraperOrchestrator:
    """Manages all county scrapers"""
    
    def __init__(self):
        self.scrapers = [
            NashvilleDavidsonScraper(),
            RutherfordScraper(),
            WilsonScraper(),
            SumnerScraper(),
            HarrisScraper()
        ]
    
    def scrape_all(self) -> List[Dict]:
        """Run all scrapers and collect permits"""
        all_permits = []
        
        for scraper in self.scrapers:
            print(f"Scraping {scraper.county_name}...")
            try:
                permits = scraper.scrape()
                all_permits.extend(permits)
                print(f"  Found {len(permits)} permits")
            except Exception as e:
                print(f"  Error: {e}")
        
        print(f"
Total permits collected: {len(all_permits)}")
        return all_permits
