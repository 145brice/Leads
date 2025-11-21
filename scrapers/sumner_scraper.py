
"""
Sumner County permit scraper
"""
from typing import List, Dict
from .base_scraper import PermitScraper


class SumnerScraper(PermitScraper):
    """Scraper for Sumner County building permits"""
    
    def __init__(self):
        super().__init__(
            'Sumner',
            'https://sumnercountytn.gov'  # Main homepage
        )
    
    def scrape(self) -> List[Dict]:
        """
        Scrape Sumner County permits
        Note: Sumner does not appear to publish issued permit data publicly online.
        """
        permits = []
        print(f"{self.county_name}: No public issued permit data available")
        return permits
