
"""
Nashville-Davidson County permit scraper
"""
import re
from typing import List, Dict
from .base_scraper import PermitScraper


class NashvilleDavidsonScraper(PermitScraper):
    """Scraper for Nashville-Davidson County building permits"""
    
    def __init__(self):
        super().__init__(
            'Nashville-Davidson',
            'https://www.nashville.gov'  # Main homepage for dynamic link finding
        )
    
    def scrape(self) -> List[Dict]:
        """
        Scrape Nashville-Davidson permits
        Note: Nashville does not appear to publish issued permit data publicly online.
        This scraper currently returns empty results.
        """
        permits = []
        
        # Nashville-Davidson County does not publish issued permit data publicly
        # The services page only shows permit application links, not issued permits
        print(f"{self.county_name}: No public issued permit data available")
        
        return permits
    
    def extract_from_table_row(self, cols) -> Dict:
        """Extract permit data from table row"""
        # Not used since no tables with permit data exist
        return None
    
    def extract_from_html(self, soup) -> Dict:
        """Extract permit data from HTML page"""
        # Not used since no permit data pages exist
        return None
    
    def extract_from_pdf(self, text: str) -> Dict:
        """Extract permit data from PDF text"""
        # Not used since no permit PDFs are available
        return None
    
    def parse_value(self, value_str: str) -> float:
        """Parse monetary value from string"""
        try:
            # Remove $ and commas, convert to float
            cleaned = re.sub(r'[,$]', '', value_str)
            return float(cleaned)
        except:
            return 0.0
