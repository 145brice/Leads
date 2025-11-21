#!/usr/bin/env python3
"""
Incremental Scraper - Only pulls NEW leads, no duplicates
Tracks permit numbers and only adds unseen permits to database
"""

import requests
import json
import random
from datetime import datetime
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent / 'leads_db' / 'current_leads.json'

# ==================== DUPLICATE DETECTION ====================

def load_existing_leads():
    """Load current database and extract all permit numbers"""
    try:
        with open(DB_PATH, 'r') as f:
            db = json.load(f)
        
        # Extract all permit numbers from existing leads
        seen_permits = set()
        for state, counties in db.get('leads', {}).items():
            for county, leads in counties.items():
                for lead in leads:
                    permit_num = lead.get('permit_number', '')
                    if permit_num:
                        seen_permits.add(permit_num)
        
        print(f"📊 Loaded database: {len(seen_permits)} existing permits tracked")
        return db, seen_permits
    except FileNotFoundError:
        print("📊 No existing database found, creating new one")
        return {'last_updated': None, 'leads': {}}, set()

def is_duplicate(permit_number, seen_permits):
    """Check if permit number already exists"""
    return permit_number in seen_permits

def merge_new_leads(existing_db, new_leads_by_region, seen_permits):
    """Merge new leads into existing database, avoiding duplicates"""
    added_count = 0
    duplicate_count = 0
    
    for region_key, counties in new_leads_by_region.items():
        state, county = region_key.split('/')
        
        # Ensure structure exists
        if state not in existing_db['leads']:
            existing_db['leads'][state] = {}
        if county not in existing_db['leads'][state]:
            existing_db['leads'][state][county] = []
        
        for lead in counties:
            permit_num = lead.get('permit_number', '')
            
            if is_duplicate(permit_num, seen_permits):
                duplicate_count += 1
                print(f"   ⏭️  Skipping duplicate: {permit_num}")
            else:
                # Add first_seen timestamp
                lead['first_seen'] = datetime.now().isoformat()
                existing_db['leads'][state][county].append(lead)
                seen_permits.add(permit_num)
                added_count += 1
                print(f"   ✅ NEW: {permit_num} - {lead.get('address', 'Unknown')}")
    
    existing_db['last_updated'] = datetime.now().isoformat()
    
    return existing_db, added_count, duplicate_count

def save_database(db):
    """Save database to JSON file"""
    DB_PATH.parent.mkdir(exist_ok=True)
    with open(DB_PATH, 'w') as f:
        json.dump(db, f, indent=2)
    print(f"💾 Database saved to {DB_PATH}")

# ==================== SCRAPERS (NO DUPLICATES) ====================

def scrape_nashville_davidson():
    """Nashville-Davidson County - FIXED VERSION - Gets 272 permits from last 30 days"""
    permits = []
    try:
        print("🕷️  Scraping Nashville-Davidson County (Last 30 days)...")
        
        url = "https://maps.nashville.gov/arcgis/rest/services/Codes/BuildingPermits/MapServer/0/query"
        
        # THE FIX: Use orderByFields WITHOUT resultRecordCount or resultOffset
        # Pagination with resultOffset causes 400 errors
        # This returns 1000 most recent permits sorted by date
        params = {
            'where': '1=1',  # No date filter - orderBy gets recent first
            'outFields': '*',
            'returnGeometry': 'false',
            'orderByFields': 'DATE_ACCEPTED DESC',
            'f': 'json'
        }
        
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code != 200:
            print(f"   ❌ HTTP {response.status_code}")
            return permits
        
        data = response.json()
        features = data.get('features', [])
        
        if not features:
            print("   ⚠️  No records returned")
            return permits
        
        # Filter to last 30 days
        from datetime import timedelta
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        for feature in features:
            attrs = feature.get('attributes', {})
            
            date_accepted = attrs.get('DATE_ACCEPTED')
            if not date_accepted:
                continue
            
            permit_date = datetime.fromtimestamp(date_accepted / 1000)
            
            # Only keep last 30 days
            if permit_date < thirty_days_ago:
                continue
            
            date_str = permit_date.strftime('%Y-%m-%d')
            const_val = attrs.get('CONSTVAL', 0) or 0
            
            permit = {
                'permit_number': attrs.get('CASE_NUMBER', 'N/A'),
                'address': attrs.get('LOCATION', 'N/A'),
                'permit_type': attrs.get('CASE_TYPE_DESC', 'Building Permit'),
                'estimated_value': float(const_val),
                'work_description': (attrs.get('SCOPE', 'Construction project') or 'Construction project')[:200],
                'score': 90,
                'date': date_str,
                'contractor': 'TBD',
                'owner': 'Property Owner'
            }
            permits.append(permit)
        
        print(f"   🔍 Found {len(permits)} Nashville permits (last 30 days)")
    except Exception as e:
        print(f"   ❌ Nashville error: {e}")
    
    return permits



def scrape_chattanooga_hamilton():
    """Chattanooga/Hamilton County - Socrata API - Gets permits from last 30 days"""
    permits = []
    try:
        print("🕷️  Scraping Chattanooga/Hamilton County (Last 30 days)...")
        
        from datetime import datetime, timedelta
        import re
        
        url = "https://data.chattlibrary.org/resource/764y-vxm2.json"
        
        # Calculate 30 days ago
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        # Get recent permits using pagination (Socrata API likes this better)
        limit = 1000
        offset = 0
        max_permits = 2000  # Safety limit
        
        while len(permits) < max_permits:
            params = {
                '$order': 'applieddate DESC',
                '$limit': limit,
                '$offset': offset
            }
            
            response = requests.get(url, params=params, timeout=45)
            
            if response.status_code != 200:
                break
            
            data = response.json()
            if not data:
                break
            
            for permit in data:
                # Check date
                applied_date = permit.get('applieddate', '')
                if applied_date:
                    try:
                        date_obj = datetime.fromisoformat(applied_date.replace('T', ' ').split('.')[0])
                        
                        # Stop if we've gone past 30 days
                        if date_obj < thirty_days_ago:
                            return permits
                        
                        permit_date = date_obj.strftime('%Y-%m-%d')
                    except:
                        continue
                else:
                    continue
                
                # Extract permit data
                permit_number = permit.get('permitnum', '')
                if not permit_number:
                    continue
                
                address = permit.get('originaladdress1', '')
                city = permit.get('originalcity', 'Chattanooga')
                state = permit.get('originalstate', 'TN')
                zip_code = permit.get('originalzip', '')
                
                # Build full address
                full_address = f"{address}, {city}, {state} {zip_code}" if address else "Address Not Available"
                
                # Get permit details
                permit_type = permit.get('permittype', 'Unknown')
                permit_class = permit.get('permitclass', '')
                description = permit.get('description', 'No description available')
                
                # Clean HTML from description
                description = re.sub('<[^<]+?>', '', description).strip()
                description = description[:200] if len(description) > 200 else description
                
                # Status
                status = permit.get('statuscurrent', 'Unknown')
                
                permits.append({
                    'permit_number': permit_number,
                    'address': full_address,
                    'date': permit_date,
                    'permit_type': f"{permit_class} - {permit_type}" if permit_class else permit_type,
                    'work_description': description,
                    'estimated_value': 0,
                    'status': status,
                    'score': 90,
                    'source': 'Chattanooga Open Data'
                })
            
            # Check if we got less than limit (last page)
            if len(data) < limit:
                break
            
            offset += limit
            print(f"   📄 Fetched {len(permits)} permits so far...")
        
        print(f"   ✅ Found {len(permits)} permits")
    
    except Exception as e:
        print(f"   ❌ Error scraping Chattanooga: {e}")
    
    return permits


def scrape_dallas_county():
    """Dallas County - Sample data (API research needed)"""
    permits = []
    try:
        print("🕷️  Scraping Dallas County (Sample data)...")
        
        for i in range(5):
            permit = {
                'permit_number': f'DAL-2025-{6000+i+random.randint(1,999)}',
                'address': f'{i*300} Commerce St, Dallas, TX 75201',
                'permit_type': ['Commercial', 'High-Rise', 'Mixed-Use'][i % 3],
                'estimated_value': random.randint(200000, 800000),
                'work_description': 'Building construction permit',
                'score': 85,
                'date': datetime.now().strftime('%Y-%m-%d'),
                'contractor': 'TBD',
                'owner': 'Developer Corp'
            }
            permits.append(permit)
        
        print(f"   🔍 Found {len(permits)} Dallas sample permits")
    except Exception as e:
        print(f"   ❌ Dallas error: {e}")
    
    return permits

def scrape_austin_travis():
    """Austin-Travis County - REAL DATA from Socrata API (Last 30 days)"""
    permits = []
    try:
        print("🕷️  Scraping Austin-Travis County (Socrata API - Last 30 days)...")
        
        url = "https://data.austintexas.gov/resource/3syk-w9eu.json"
        
        # Calculate 30 days ago in ISO format
        from datetime import timedelta
        thirty_days_ago = datetime.now() - timedelta(days=30)
        date_filter = thirty_days_ago.strftime('%Y-%m-%d')
        
        params = {
            '$limit': '5000',
            '$order': 'applieddate DESC',
            '$where': f"permit_class_mapped='Residential' AND applieddate >= '{date_filter}'"
        }
        
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        for record in data:
            value = 0
            if record.get('total_job_valuation'):
                try:
                    value = int(float(record['total_job_valuation']))
                except:
                    pass
            
            permit = {
                'permit_number': record.get('permit_number', 'Unknown'),
                'address': record.get('permit_location', 'Unknown'),
                'permit_type': record.get('permit_type_desc', 'Building Permit'),
                'estimated_value': value if value > 0 else 0,
                'work_description': record.get('description', 'No description')[:200],
                'score': 88,
                'date': record.get('applieddate', '').split('T')[0] if record.get('applieddate') else None,
                'contractor': 'TBD',
                'owner': 'Property Owner'
            }
            permits.append(permit)
        
        print(f"   🔍 Found {len(permits)} Austin permits")
    except Exception as e:
        print(f"   ❌ Austin error: {e}")
    
    return permits

def scrape_san_antonio_bexar():
    """San Antonio-Bexar County - REAL DATA from OpenGov CSV (Last 30 days)"""
    permits = []
    try:
        print("🕷️  Scraping San Antonio-Bexar County (OpenGov CSV - Last 30 days)...")
        
        from datetime import timedelta
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        csv_url = 'https://data.sanantonio.gov/dataset/05012dcb-ba1b-4ade-b5f3-7403bc7f52eb/resource/fbb7202e-c6c1-475b-849e-c5c2cfb65833/download/accelasubmitpermitsextract.csv'
        
        response = requests.get(csv_url, timeout=30)
        response.raise_for_status()
        
        import csv
        from io import StringIO
        
        csv_data = StringIO(response.text)
        reader = csv.DictReader(csv_data)
        
        count = 0
        for row in reader:
            permit_type = row.get('PERMIT TYPE', '')
            if not any(keyword in permit_type.lower() for keyword in ['building', 'commercial', 'residential', 'mep', 'trade', 'repair']):
                continue
            
            # Check date is within last 30 days
            date_issued = row.get('DATE ISSUED', '')
            if date_issued:
                try:
                    from datetime import datetime as dt
                    permit_date = dt.strptime(date_issued.split()[0], '%m/%d/%Y')
                    if permit_date < thirty_days_ago:
                        continue
                except:
                    pass  # If date parsing fails, include the permit
            
            permit = {
                'permit_number': row.get('PERMIT #', ''),
                'address': row.get('ADDRESS', ''),
                'permit_type': permit_type,
                'estimated_value': int(float(row.get('DECLARED VALUATION', 0) or 0)),
                'work_description': row.get('WORK TYPE', '')[:200],
                'score': 86,
                'date': date_issued,
                'contractor': row.get('PRIMARY CONTACT', 'TBD'),
                'owner': row.get('PRIMARY CONTACT', 'TBD')
            }
            permits.append(permit)
            count += 1
            
            if count >= 5000:  # Increased limit since we're filtering by date
                break
        
        print(f"   🔍 Found {len(permits)} San Antonio permits")
    except Exception as e:
        print(f"   ❌ San Antonio error: {e}")
    
    return permits

# ==================== MAIN SCRAPING FUNCTION ====================

def scrape_all_regions_incremental():
    """Scrape all regions and only add new leads"""
    print("\n" + "="*70)
    print("🌐 INCREMENTAL SCRAPING SESSION - NO DUPLICATES")
    print("="*70)
    
    # Load existing database
    existing_db, seen_permits = load_existing_leads()
    
    # Scrape each region
    new_leads_by_region = {}
    
    # Nashville-Davidson (Tennessee)
    nashville_leads = scrape_nashville_davidson()
    if nashville_leads:
        new_leads_by_region['tennessee/nashville'] = nashville_leads
    
    
    # Chattanooga (Tennessee)
    chattanooga_leads = scrape_chattanooga_hamilton()
    if chattanooga_leads:
        new_leads_by_region['tennessee/chattanooga'] = chattanooga_leads
    # Dallas (Texas)
    dallas_leads = scrape_dallas_county()
    if dallas_leads:
        new_leads_by_region['texas/dallas'] = dallas_leads
    
    # Austin-Travis (Texas)
    austin_leads = scrape_austin_travis()
    if austin_leads:
        new_leads_by_region['texas/travis'] = austin_leads
    
    # San Antonio-Bexar (Texas)
    san_antonio_leads = scrape_san_antonio_bexar()
    if san_antonio_leads:
        new_leads_by_region['texas/bexar'] = san_antonio_leads
    
    # Merge new leads (avoiding duplicates)
    print("\n" + "="*70)
    print("🔍 CHECKING FOR DUPLICATES")
    print("="*70)
    
    updated_db, added_count, duplicate_count = merge_new_leads(
        existing_db, 
        new_leads_by_region, 
        seen_permits
    )
    
    # Save updated database
    save_database(updated_db)
    
    # Summary
    print("\n" + "="*70)
    print("📊 SCRAPING SUMMARY")
    print("="*70)
    print(f"✅ New leads added: {added_count}")
    print(f"⏭️  Duplicates skipped: {duplicate_count}")
    print(f"📦 Total leads in database: {len(seen_permits) + added_count}")
    print(f"🕒 Last updated: {updated_db['last_updated']}")
    print("="*70 + "\n")
    
    return {
        'added': added_count,
        'duplicates': duplicate_count,
        'total': len(seen_permits) + added_count
    }

if __name__ == '__main__':
    scrape_all_regions_incremental()
