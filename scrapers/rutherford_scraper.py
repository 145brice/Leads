
"""
Rutherford County permit scraper
"""
from typing import List, Dict
from .base_scraper import PermitScraper


class RutherfordScraper(PermitScraper):
    """Scraper for Rutherford County building permits"""
    
    def __init__(self):
        super().__init__(
            'Rutherford',
            'https://rutherfordcountytn.gov'  # Main homepage
        )
    
    def scrape(self) -> List[Dict]:
        """
        Scrape Rutherford County permits
        Note: Rutherford does not appear to publish issued permit data publicly online.
        """
        permits = []
        print(f"{self.county_name}: No public issued permit data available")
        return permits
