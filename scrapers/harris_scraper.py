
"""
Harris County (Texas) permit scraper
"""
import re
from typing import List, Dict
from .base_scraper import PermitScraper


class HarrisScraper(PermitScraper):
    """Scraper for Harris County, TX building permits"""
    
    def __init__(self):
        super().__init__(
            'Harris-TX',
            'https://www.harriscountytx.gov'  # Main homepage
        )
    
    def scrape(self) -> List[Dict]:
        """
        Scrape Harris County permits
        """
        permits = []
        
        try:
            # Find today's permits link dynamically
            permits_url = self.find_todays_permits_link()
            if not permits_url:
                print(f"No today's permits link found for {self.county_name}")
                return permits
            
            print(f"Found permits URL: {permits_url}")
            
            # Parse the permits page
            soup = self.parse_html(permits_url)
            if not soup:
                return permits
            
            # Look for permit data in tables
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows[1:]:  # Skip header row
                    cols = row.find_all(['td', 'th'])
                    if len(cols) >= 4:  # Ensure we have enough columns
                        permit_data = self.extract_from_table_row(cols)
                        if permit_data:
                            permits.append(permit_data)
            
            # If no table data found, try looking for permit links
            if not permits:
                permit_links = soup.find_all('a', href=re.compile(r'permit|application|pdf'))
                for link in permit_links[:20]:  # Limit to recent 20
                    permit_url = link.get('href')
                    if not permit_url.startswith('http'):
                        permit_url = f"{self.base_url.rstrip('/')}{permit_url}"
                    
                    # Check if it's a PDF
                    if permit_url.endswith('.pdf'):
                        pdf_text = self.parse_pdf(permit_url)
                        permit_data = self.extract_from_pdf(pdf_text)
                    else:
                        permit_soup = self.parse_html(permit_url)
                        permit_data = self.extract_from_html(permit_soup)
                    
                    if permit_data:
                        permits.append(permit_data)
        
        except Exception as e:
            print(f"Error scraping {self.county_name}: {e}")
        
        return permits
    
    def extract_from_table_row(self, cols) -> Dict:
        """Extract permit data from table row"""
        try:
            # Assuming table columns: Permit #, Address, Type, Value, Date
            permit_number = cols[0].get_text().strip() if len(cols) > 0 else ''
            address = cols[1].get_text().strip() if len(cols) > 1 else ''
            permit_type = cols[2].get_text().strip() if len(cols) > 2 else ''
            value_text = cols[3].get_text().strip() if len(cols) > 3 else '0'
            issue_date = cols[4].get_text().strip() if len(cols) > 4 else ''
            
            return self.create_permit_dict(
                permit_number=permit_number,
                address=address,
                permit_type=permit_type,
                estimated_value=self.parse_value(value_text),
                issue_date=issue_date
            )
        except Exception as e:
            print(f"Error extracting from table row: {e}")
            return None
    
    def extract_from_html(self, soup) -> Dict:
        """Extract permit data from HTML page"""
        if not soup:
            return None
        
        try:
            # Example extraction (adjust based on actual HTML structure)
            permit_number = soup.find('span', class_='permit-number')
            address = soup.find('div', class_='address')
            permit_type = soup.find('span', class_='permit-type')
            value = soup.find('span', class_='estimated-value')
            
            return self.create_permit_dict(
                permit_number=permit_number.text.strip() if permit_number else '',
                address=address.text.strip() if address else '',
                permit_type=permit_type.text.strip() if permit_type else '',
                estimated_value=self.parse_value(value.text if value else '0')
            )
        except Exception as e:
            print(f"Error extracting from HTML: {e}")
            return None
    
    def extract_from_pdf(self, text: str) -> Dict:
        """Extract permit data from PDF text"""
        if not text:
            return None
        
        try:
            # Use regex to extract common fields
            permit_number = re.search(r'Permit #?:?\s*(\S+)', text)
            address = re.search(r'Address:?\s*([^
]+)', text)
            permit_type = re.search(r'Type:?\s*([^
]+)', text)
            value = re.search(r'Value:?\s*$?([\d,]+)', text)
            
            return self.create_permit_dict(
                permit_number=permit_number.group(1) if permit_number else '',
                address=address.group(1).strip() if address else '',
                permit_type=permit_type.group(1).strip() if permit_type else '',
                estimated_value=self.parse_value(value.group(1) if value else '0')
            )
        except Exception as e:
            print(f"Error extracting from PDF: {e}")
            return None
    
    def parse_value(self, value_str: str) -> float:
        """Parse monetary value from string"""
        try:
            # Remove $ and commas, convert to float
            cleaned = re.sub(r'[,$]', '', value_str)
            return float(cleaned)
        except:
            return 0.0
