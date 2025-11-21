
"""
Wilson County permit scraper
"""
from typing import List, Dict
from .base_scraper import PermitScraper


class WilsonScraper(PermitScraper):
    """Scraper for Wilson County building permits"""
    
    def __init__(self):
        super().__init__(
            'Wilson',
            'https://www.wilsoncountytn.gov'  # Main homepage
        )
    
    def scrape(self) -> List[Dict]:
        """
        Scrape Wilson County permits
        Note: Wilson does not appear to publish issued permit data publicly online.
        """
        permits = []
        print(f"{self.county_name}: No public issued permit data available")
        return permits
