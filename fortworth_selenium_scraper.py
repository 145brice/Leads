"""
Fort Worth Accela Selenium Scraper
Scrapes building permits from Fort Worth's Accela Citizen Access portal
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta
import time
import json

def setup_driver():
    """Setup Chrome driver with headless options"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in background
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def scrape_fortworth_accela():
    """Scrape Fort Worth building permits from Accela"""
    print("\n" + "="*70)
    print("🕷️  Starting Fort Worth Accela Selenium Scraper")
    print("="*70)
    
    driver = None
    permits = []
    
    try:
        # Setup driver
        print("\n1️⃣  Setting up Chrome driver...")
        driver = setup_driver()
        
        # Navigate directly to Development permit search page
        print("2️⃣  Navigating to Fort Worth Development permit search...")
        url = "https://aca-prod.accela.com/CFW/Cap/CapHome.aspx?module=Development&TabName=Development"
        driver.get(url)
        
        # Wait for page to load
        print("3️⃣  Waiting for search page to load...")
        time.sleep(5)
        
        # Try to find and interact with search form
        print("4️⃣  Looking for permit search form...")
        
        # Save page source for debugging
        with open('/tmp/fortworth_search_page.html', 'w') as f:
            f.write(driver.page_source)
        print("   💾 Page source saved to /tmp/fortworth_search_page.html")
        
        # Common Accela search field IDs/names
        search_fields = [
            "ctl00$PlaceHolderMain$generalSearchForm$txtGSPermitNumber",
            "ctl00$PlaceHolderMain$generalSearchForm$txtGSStreetName",
            "txtGSPermitNumber",
            "txtGSStreetName"
        ]
        
        # Try to find date range or recent permits option
        print("7️⃣  Attempting to set date range...")
        
        # Calculate date range (last 30 days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # Try to find date fields
        date_fields = driver.find_elements(By.CSS_SELECTOR, "input[type='text'][id*='Date']")
        print(f"   Found {len(date_fields)} date fields")
        
        # Look for search button
        print("8️⃣  Looking for search button...")
        search_buttons = driver.find_elements(By.CSS_SELECTOR, "input[type='submit'][value*='Search'], a[id*='Search']")
        print(f"   Found {len(search_buttons)} search buttons")
        
        if search_buttons:
            print("9️⃣  Clicking search to get recent permits...")
            try:
                search_buttons[0].click()
                time.sleep(5)
            except Exception as e:
                print(f"   ⚠️  Could not click button: {e}")
        
        # Wait for results
        print("🔟 Waiting for results...")
        time.sleep(5)
        
        # Try to find results table
        print("📋 Looking for permit results table...")
        
        # Common table selectors in Accela
        table_selectors = [
            "table[id*='gdvPermitList']",
            "table[class*='ACA_GridView']",
            "table[class*='result']",
            "div[id*='divResultsTable'] table"
        ]
        
        results_table = None
        for selector in table_selectors:
            tables = driver.find_elements(By.CSS_SELECTOR, selector)
            if tables:
                results_table = tables[0]
                print(f"   ✅ Found results table with selector: {selector}")
                break
        
        if results_table:
            # Parse table rows
            rows = results_table.find_elements(By.TAG_NAME, "tr")
            print(f"   📊 Found {len(rows)} rows in results table")
            
            for i, row in enumerate(rows[1:]):  # Skip header row
                try:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) >= 3:
                        permit = {
                            'permit_number': cells[0].text.strip() if len(cells) > 0 else 'N/A',
                            'address': cells[1].text.strip() if len(cells) > 1 else 'N/A',
                            'permit_type': cells[2].text.strip() if len(cells) > 2 else 'Building',
                            'date': cells[3].text.strip() if len(cells) > 3 else datetime.now().strftime('%Y-%m-%d'),
                            'status': cells[4].text.strip() if len(cells) > 4 else 'Active',
                            'work_description': 'Scraped from Accela portal',
                            'estimated_value': 0,
                            'score': 85,
                            'source': 'Fort Worth Accela (Selenium)'
                        }
                        permits.append(permit)
                        
                        if i < 5:  # Show first 5
                            print(f"   ✅ {permit['permit_number']} - {permit['address']}")
                except Exception as e:
                    print(f"   ⚠️  Error parsing row {i}: {e}")
                    continue
        else:
            print("   ❌ Could not find results table")
            print("   📸 Taking screenshot for debugging...")
            driver.save_screenshot("/tmp/fortworth_no_results.png")
            print("   💾 Screenshot saved to /tmp/fortworth_no_results.png")
            
            # Print page source snippet for debugging
            print("\n   🔍 Page source snippet:")
            print(driver.page_source[:500])
        
    except Exception as e:
        print(f"\n❌ Error during scraping: {e}")
        if driver:
            driver.save_screenshot("/tmp/fortworth_error.png")
            print("📸 Screenshot saved to /tmp/fortworth_error.png")
    
    finally:
        if driver:
            print("\n🔄 Closing browser...")
            driver.quit()
    
    print("\n" + "="*70)
    print(f"✅ Scraping complete! Found {len(permits)} permits")
    print("="*70)
    
    return permits

if __name__ == '__main__':
    permits = scrape_fortworth_accela()
    
    if permits:
        print("\n📊 Sample permits:")
        for permit in permits[:5]:
            print(f"\n  Permit: {permit['permit_number']}")
            print(f"  Address: {permit['address']}")
            print(f"  Type: {permit['permit_type']}")
            print(f"  Date: {permit['date']}")
    else:
        print("\n⚠️  No permits found. The Accela portal may require:")
        print("  1. Manual interaction (captcha)")
        print("  2. Login credentials")
        print("  3. Different search approach")
        print("\n💡 Next steps:")
        print("  • Check screenshots in /tmp/")
        print("  • Try manual search on portal to see required fields")
        print("  • Consider requesting bulk data from city")
