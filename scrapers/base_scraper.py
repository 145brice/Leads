"""
Base scraper class for county permit websites
"""
import requests
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
from typing import List, Dict
import pdfplumber
import io
from datetime import datetime
import re


class PermitScraper(ABC):
    """Base class for all county permit scrapers"""
    
    def __init__(self, county_name: str, base_url: str):
        self.county_name = county_name
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def find_todays_permits_link(self) -> str:
        """
        Dynamically find the 'today's permits' link on the homepage
        Returns the full URL to the permits page
        """
        try:
            soup = self.parse_html(self.base_url)
            if not soup:
                return None
            
            # Look for links containing keywords related to today's/daily permits
            keywords = ['today', 'daily', 'issued', 'new', 'permit', 'report']
            
            for link in soup.find_all('a', href=True):
                link_text = link.get_text().lower()
                href = link.get('href')
                
                # Check if link text contains any of our keywords
                if any(keyword in link_text for keyword in keywords):
                    # Convert relative URLs to absolute
                    if href.startswith('http'):
                        print(f"🔍 {self.county_name}: Found potential permits link: {href}")
                        return href
                    elif href.startswith('//'):
                        # Protocol-relative URL
                        full_url = f"https:{href}"
                        print(f"🔍 {self.county_name}: Found potential permits link: {full_url}")
                        return full_url
                    elif href.startswith('/'):
                        full_url = f"{self.base_url.rstrip('/')}{href}"
                        print(f"🔍 {self.county_name}: Found potential permits link: {full_url}")
                        return full_url
                    else:
                        # Relative URL without leading slash
                        full_url = f"{self.base_url.rstrip('/')}/{href}"
                        print(f"🔍 {self.county_name}: Found potential permits link: {full_url}")
                        return full_url
            
            # If no direct link found, try searching for text patterns in the page
            page_text = soup.get_text().lower()
            if any(keyword in page_text for keyword in keywords):
                # Look for any link that might be related
                for link in soup.find_all('a', href=True):
                    href = link.get('href')
                    if 'permit' in href.lower() or 'report' in href.lower():
                        if href.startswith('http'):
                            print(f"🔍 {self.county_name}: Found fallback permits link: {href}")
                            return href
                        elif href.startswith('//'):
                            # Protocol-relative URL
                            full_url = f"https:{href}"
                            print(f"🔍 {self.county_name}: Found fallback permits link: {full_url}")
                            return full_url
                        elif href.startswith('/'):
                            full_url = f"{self.base_url.rstrip('/')}{href}"
                            print(f"🔍 {self.county_name}: Found fallback permits link: {full_url}")
                            return full_url
                        else:
                            # Relative URL without leading slash
                            full_url = f"{self.base_url.rstrip('/')}/{href}"
                            print(f"🔍 {self.county_name}: Found fallback permits link: {full_url}")
                            return full_url
            
            print(f"🔍 {self.county_name}: No permits links found on homepage")
            return None
            
        except Exception as e:
            print(f"Error finding today's permits link for {self.county_name}: {e}")
            return None
    
    @abstractmethod
    def scrape(self) -> List[Dict]:
        """
        Scrape permits from county website
        Returns list of permit dictionaries
        """
        pass
    
    def parse_html(self, url: str) -> BeautifulSoup:
        """Fetch and parse HTML page"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def parse_pdf(self, pdf_url: str) -> str:
        """Download and extract text from PDF"""
        try:
            response = self.session.get(pdf_url, timeout=30)
            response.raise_for_status()
            
            with pdfplumber.open(io.BytesIO(response.content)) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            print(f"Error parsing PDF {pdf_url}: {e}")
            return ""
    
    def create_permit_dict(self, **kwargs) -> Dict:
        """Create standardized permit dictionary"""
        return {
            'county': self.county_name,
            'permit_number': kwargs.get('permit_number', ''),
            'address': kwargs.get('address', ''),
            'permit_type': kwargs.get('permit_type', ''),
            'work_description': kwargs.get('work_description', ''),
            'estimated_value': kwargs.get('estimated_value', 0),
            'issue_date': kwargs.get('issue_date', ''),
            'contractor': kwargs.get('contractor', ''),
            'owner': kwargs.get('owner', ''),
            'scraped_at': datetime.now().isoformat()
        }
