#!/usr/bin/env python3
"""
Vendor Permit Portal Scraper
Targets: Accela, CivicPlus, OpenGov portals

USAGE:
1. Run script with --setup flag to see login instructions
2. After login, copy cURL from DevTools Network tab
3. Save cURL to auth_cookies/[city_name].curl
4. Run script with --city [city_name] to scrape permits

"""
import os
import sys
import time
import csv
import json
import subprocess
from datetime import datetime
from pathlib import Path
import requests
from bs4 import BeautifulSoup

# Directory for storing auth cookies
AUTH_DIR = Path(__file__).parent / "auth_cookies"
OUTPUT_DIR = Path(__file__).parent / "scraped_permits"

# Ensure directories exist
AUTH_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)


class PermitPortalScraper:
    """Base scraper for permit portals"""
    
    def __init__(self, city_name, vendor_type):
        self.city_name = city_name
        self.vendor_type = vendor_type
        self.session = requests.Session()
        self.curl_file = AUTH_DIR / f"{city_name}.curl"
        
    def load_auth_from_curl(self):
        """Parse cURL command to extract cookies and headers"""
        if not self.curl_file.exists():
            print(f"❌ No auth file found: {self.curl_file}")
            print(f"\n📝 To create auth:")
            print(f"   1. Open browser, go to permit portal")
            print(f"   2. Login/search for permits")
            print(f"   3. Open DevTools → Network tab")
            print(f"   4. Right-click request → Copy → Copy as cURL")
            print(f"   5. Save to: {self.curl_file}")
            return False
        
        with open(self.curl_file, 'r') as f:
            curl_cmd = f.read()
        
        # Extract cookies from cURL
        cookies = {}
        headers = {}
        
        # Parse cURL format: curl 'URL' -H 'header: value' --cookie 'name=value'
        lines = curl_cmd.split('\n')
        for line in lines:
            line = line.strip()
            
            # Extract cookies
            if '--cookie' in line or '-b' in line:
                cookie_str = line.split("'")[1] if "'" in line else line.split('"')[1]
                for cookie in cookie_str.split(';'):
                    if '=' in cookie:
                        name, value = cookie.strip().split('=', 1)
                        cookies[name] = value
            
            # Extract headers
            if '-H' in line or '--header' in line:
                try:
                    header_str = line.split("'")[1] if "'" in line else line.split('"')[1]
                    if ':' in header_str:
                        name, value = header_str.split(':', 1)
                        headers[name.strip()] = value.strip()
                except:
                    pass
        
        # Apply to session
        self.session.cookies.update(cookies)
        self.session.headers.update(headers)
        
        print(f"✅ Loaded {len(cookies)} cookies, {len(headers)} headers")
        return True
    
    def scrape(self):
        """Override in subclasses"""
        raise NotImplementedError


class AccelaScraper(PermitPortalScraper):
    """Scraper for Accela Citizen Access portals
    
    Common URLs:
    - Round Rock: https://permits.roundrocktexas.gov/
    - Plano: Uses Accela (need to find URL)
    """
    
    def __init__(self, city_name, search_url):
        super().__init__(city_name, "Accela")
        self.search_url = search_url
    
    def scrape(self):
        """Scrape permits from Accela portal"""
        if not self.load_auth_from_curl():
            return []
        
        print(f"🔍 Scraping {self.city_name} Accela portal...")
        
        permits = []
        
        try:
            # Step 1: Hit the search results page
            response = self.session.get(self.search_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Step 2: Find permit table (Accela uses specific class names)
            # Common patterns: table with class "ACA_Grid_Table", "ACA_TabRow_Odd/Even"
            tables = soup.find_all('table', class_=['ACA_Grid_Table', 'permit-table', 'results-table'])
            
            for table in tables:
                rows = table.find_all('tr')
                
                for row in rows[1:]:  # Skip header
                    cols = row.find_all(['td', 'th'])
                    if len(cols) >= 4:  # Need at least permit#, address, type, date
                        permit = {
                            'city': self.city_name,
                            'permit_number': cols[0].get_text(strip=True),
                            'address': cols[1].get_text(strip=True),
                            'permit_type': cols[2].get_text(strip=True) if len(cols) > 2 else '',
                            'date': cols[3].get_text(strip=True) if len(cols) > 3 else '',
                            'owner': cols[4].get_text(strip=True) if len(cols) > 4 else '',
                            'status': cols[5].get_text(strip=True) if len(cols) > 5 else '',
                            'scraped_at': datetime.now().isoformat(),
                            'source': 'Accela'
                        }
                        permits.append(permit)
                        
                    time.sleep(0.1)  # Small delay between rows
            
            print(f"   ✅ Found {len(permits)} permits")
            
        except Exception as e:
            print(f"   ❌ Error scraping: {e}")
        
        return permits


class CivicPlusScraper(PermitPortalScraper):
    """Scraper for CivicPlus permit systems
    
    Common URLs:
    - Murfreesboro: https://www.murfreesborotn.gov/171/Building-Permits
    """
    
    def __init__(self, city_name, search_url):
        super().__init__(city_name, "CivicPlus")
        self.search_url = search_url
    
    def scrape(self):
        """Scrape permits from CivicPlus portal"""
        if not self.load_auth_from_curl():
            return []
        
        print(f"🔍 Scraping {self.city_name} CivicPlus portal...")
        
        permits = []
        
        try:
            response = self.session.get(self.search_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # CivicPlus often uses div-based layouts or tables
            # Look for permit listings
            permit_divs = soup.find_all('div', class_=['permit-item', 'record-item'])
            permit_tables = soup.find_all('table', class_=['permit-list', 'data-table'])
            
            # Try table format first
            for table in permit_tables:
                rows = table.find_all('tr')
                for row in rows[1:]:
                    cols = row.find_all(['td', 'th'])
                    if len(cols) >= 3:
                        permit = {
                            'city': self.city_name,
                            'permit_number': cols[0].get_text(strip=True),
                            'address': cols[1].get_text(strip=True),
                            'permit_type': cols[2].get_text(strip=True),
                            'date': cols[3].get_text(strip=True) if len(cols) > 3 else '',
                            'scraped_at': datetime.now().isoformat(),
                            'source': 'CivicPlus'
                        }
                        permits.append(permit)
            
            # Try div format
            for div in permit_divs:
                permit_num = div.find(class_=['permit-number', 'record-id'])
                address = div.find(class_=['address', 'location'])
                permit_type = div.find(class_=['type', 'category'])
                
                if permit_num and address:
                    permit = {
                        'city': self.city_name,
                        'permit_number': permit_num.get_text(strip=True),
                        'address': address.get_text(strip=True),
                        'permit_type': permit_type.get_text(strip=True) if permit_type else '',
                        'scraped_at': datetime.now().isoformat(),
                        'source': 'CivicPlus'
                    }
                    permits.append(permit)
            
            print(f"   ✅ Found {len(permits)} permits")
            
        except Exception as e:
            print(f"   ❌ Error scraping: {e}")
        
        return permits


class OpenGovScraper(PermitPortalScraper):
    """Scraper for OpenGov/CKAN data portals
    
    Common URLs:
    - San Antonio: https://data.sanantonio.gov/dataset/building-permits
    """
    
    def __init__(self, city_name, dataset_url, csv_direct=None):
        super().__init__(city_name, "OpenGov")
        self.dataset_url = dataset_url
        self.csv_direct = csv_direct
    
    def scrape(self):
        """Download CSV from OpenGov portal"""
        print(f"🔍 Downloading {self.city_name} OpenGov CSV...")
        
        permits = []
        
        try:
            # Use direct CSV link if provided
            if self.csv_direct:
                csv_url = self.csv_direct
                print(f"   📥 Using direct CSV link...")
            else:
                # OpenGov usually has direct CSV download links
                response = self.session.get(self.dataset_url, timeout=15)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find CSV download link
                csv_links = soup.find_all('a', href=lambda x: x and '.csv' in x.lower())
                
                if not csv_links:
                    print(f"   ⚠️  No CSV links found")
                    return []
                
                csv_url = csv_links[0]['href']
                if not csv_url.startswith('http'):
                    csv_url = self.dataset_url.rsplit('/', 1)[0] + '/' + csv_url
            
            print(f"   📥 Downloading: {csv_url}")
            
            # Download CSV
            csv_response = self.session.get(csv_url, timeout=30)
            csv_response.raise_for_status()
            
            # Parse CSV
            lines = csv_response.text.splitlines()
            reader = csv.DictReader(lines)
            
            for row in reader:
                # Map common CSV column names (case-insensitive search)
                row_upper = {k.upper(): v for k, v in row.items()}
                
                permit = {
                    'city': self.city_name,
                    'permit_number': (
                        row.get('Permit Number') or row.get('PermitNumber') or 
                        row.get('PERMIT_NUMBER') or row_upper.get('PERMIT #') or 
                        row_upper.get('PERMIT NUMBER') or ''
                    ),
                    'address': (
                        row.get('Address') or row.get('Location') or 
                        row.get('ADDRESS') or row_upper.get('ADDRESS') or ''
                    ),
                    'permit_type': (
                        row.get('Type') or row.get('Permit Type') or 
                        row.get('PERMIT_TYPE') or row_upper.get('PERMIT TYPE') or 
                        row_upper.get('WORK TYPE') or ''
                    ),
                    'date_submitted': (
                        row.get('Date') or row.get('Issue Date') or 
                        row.get('ISSUE_DATE') or row_upper.get('DATE SUBMITTED') or 
                        row_upper.get('DATE ISSUED') or ''
                    ),
                    'date_issued': row_upper.get('DATE ISSUED') or '',
                    'owner': (
                        row.get('Owner') or row.get('Applicant') or 
                        row_upper.get('PRIMARY CONTACT') or row_upper.get('PROJECT NAME') or ''
                    ),
                    'value': (
                        row.get('Value') or row.get('Valuation') or 
                        row_upper.get('DECLARED VALUATION') or ''
                    ),
                    'area_sf': row_upper.get('AREA (SF)') or '',
                    'work_type': row_upper.get('WORK TYPE') or '',
                    'scraped_at': datetime.now().isoformat(),
                    'source': 'OpenGov CSV'
                }
                permits.append(permit)
            
            print(f"   ✅ Found {len(permits)} permits from CSV")
            
        except Exception as e:
            print(f"   ❌ Error downloading CSV: {e}")
        
        return permits


def save_permits_to_csv(permits, city_name):
    """Save permits to CSV file"""
    if not permits:
        print(f"⚠️  No permits to save for {city_name}")
        return
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = OUTPUT_DIR / f"{city_name}_{timestamp}.csv"
    
    # Get all unique keys
    fieldnames = set()
    for permit in permits:
        fieldnames.update(permit.keys())
    fieldnames = sorted(fieldnames)
    
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(permits)
    
    print(f"💾 Saved {len(permits)} permits to: {filename}")


# ==================== CITY CONFIGURATIONS ====================

CITY_CONFIGS = {
    'roundrock': {
        'name': 'Round Rock',
        'vendor': 'Accela',
        'url': 'https://permits.roundrocktexas.gov/',
        'scraper_class': AccelaScraper
    },
    'murfreesboro': {
        'name': 'Murfreesboro',
        'vendor': 'CivicPlus',
        'url': 'https://www.murfreesborotn.gov/171/Building-Permits',
        'scraper_class': CivicPlusScraper
    },
    'sanantonio': {
        'name': 'San Antonio',
        'vendor': 'OpenGov',
        'url': 'https://data.sanantonio.gov/dataset/building-permits',
        'csv_direct': 'https://data.sanantonio.gov/dataset/05012dcb-ba1b-4ade-b5f3-7403bc7f52eb/resource/fbb7202e-c6c1-475b-849e-c5c2cfb65833/download/accelasubmitpermitsextract.csv',
        'scraper_class': OpenGovScraper
    }
}


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Scrape building permits from vendor portals')
    parser.add_argument('--city', choices=list(CITY_CONFIGS.keys()), help='City to scrape')
    parser.add_argument('--setup', action='store_true', help='Show setup instructions')
    parser.add_argument('--list', action='store_true', help='List available cities')
    
    args = parser.parse_args()
    
    if args.setup:
        print("\n" + "="*70)
        print("🔧 SETUP INSTRUCTIONS")
        print("="*70)
        print("\n1. Open browser and navigate to permit portal")
        print("2. Login (or just search if no login required)")
        print("3. Search for building permits")
        print("4. Open DevTools (F12) → Network tab")
        print("5. Look for the search results request")
        print("6. Right-click → Copy → Copy as cURL (bash)")
        print(f"7. Save to: {AUTH_DIR}/[city_name].curl")
        print("\nExample: Save Round Rock auth to:")
        print(f"   {AUTH_DIR}/roundrock.curl")
        print("\nThen run:")
        print("   python3 vendor_portal_scraper.py --city roundrock")
        print("="*70)
        return
    
    if args.list:
        print("\n📋 Available Cities:")
        for key, config in CITY_CONFIGS.items():
            print(f"  • {key:15} → {config['name']:20} ({config['vendor']})")
        print(f"\nRun: python3 vendor_portal_scraper.py --city [city_name]")
        return
    
    if not args.city:
        print("❌ Please specify --city or use --list to see options")
        print("   Example: python3 vendor_portal_scraper.py --city roundrock")
        return
    
    # Run scraper
    config = CITY_CONFIGS[args.city]
    
    print(f"\n{'='*70}")
    print(f"🏗️  SCRAPING: {config['name']} ({config['vendor']})")
    print(f"{'='*70}\n")
    
    # Create scraper with optional csv_direct parameter
    if config['vendor'] == 'OpenGov' and 'csv_direct' in config:
        scraper = config['scraper_class'](args.city, config['url'], config.get('csv_direct'))
    else:
        scraper = config['scraper_class'](args.city, config['url'])
    
    permits = scraper.scrape()
    
    if permits:
        save_permits_to_csv(permits, args.city)
        print(f"\n✅ SUCCESS: Scraped {len(permits)} permits from {config['name']}")
    else:
        print(f"\n⚠️  No permits found (check auth or URL)")
    
    print(f"\n{'='*70}\n")


if __name__ == "__main__":
    main()
