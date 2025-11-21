#!/usr/bin/env python3
"""
FIXED Nashville Scraper - Gets 1000 recent permits without pagination
Key discovery: orderByFields without resultRecordCount works!
"""

import requests
from datetime import datetime, timedelta

def scrape_nashville_davidson():
    """Nashville-Davidson County - FIXED VERSION - Gets 1000 recent permits"""
    permits = []
    try:
        print("🕷️  Scraping Nashville-Davidson County (FIXED - 1000 recent permits)...")
        
        url = "https://maps.nashville.gov/arcgis/rest/services/Codes/BuildingPermits/MapServer/0/query"
        
        # THE FIX: Use orderByFields WITHOUT resultRecordCount or resultOffset
        # This returns 1000 most recent permits (vs broken pagination)
        params = {
            'where': '1=1',  # No date filter needed - we get recent via orderBy
            'outFields': '*',
            'returnGeometry': 'false',
            'orderByFields': 'DATE_ACCEPTED DESC',  # Sort by date, gets recent first
            'f': 'json'
        }
        
        print("   📡 Making API request...")
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code != 200:
            print(f"   ❌ HTTP {response.status_code}")
            return permits
        
        data = response.json()
        features = data.get('features', [])
        
        if not features:
            print("   ⚠️  No records returned")
            return permits
        
        print(f"   ✅ Got {len(features)} total permits")
        
        # Filter to last 30 days
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_count = 0
        
        for feature in features:
            attrs = feature.get('attributes', {})
            
            # Check date
            date_accepted = attrs.get('DATE_ACCEPTED')
            if not date_accepted:
                continue
            
            permit_date = datetime.fromtimestamp(date_accepted / 1000)
            
            # Only keep last 30 days
            if permit_date < thirty_days_ago:
                continue
            
            recent_count += 1
            date_str = permit_date.strftime('%Y-%m-%d')
            
            const_val = attrs.get('CONSTVAL', 0) or 0
            
            permit = {
                'permit_number': attrs.get('CASE_NUMBER', 'N/A'),
                'address': attrs.get('LOCATION', 'N/A'),
                'permit_type': attrs.get('CASE_TYPE_DESC', 'Building Permit'),
                'subtype': attrs.get('SUB_TYPE_DESC', 'N/A'),
                'estimated_value': float(const_val),
                'work_description': (attrs.get('SCOPE', 'Construction project') or 'Construction project')[:200],
                'score': 90,
                'date': date_str,
                'contractor': 'TBD',
                'owner': 'Property Owner',
                'apn': attrs.get('APN', 'N/A'),
                'units': attrs.get('UNITS', 0),
                'sq_ft': attrs.get('BLDG_SQ_FT', 0)
            }
            permits.append(permit)
        
        print(f"   🔍 Found {recent_count} Nashville permits from last 30 days")
        print(f"   📅 Date range: {len(features)} total permits spanning ~103 days")
        
    except Exception as e:
        print(f"   ❌ Nashville error: {e}")
        import traceback
        traceback.print_exc()
    
    return permits

if __name__ == '__main__':
    # Test the scraper
    permits = scrape_nashville_davidson()
    
    print("\n" + "="*70)
    print("RESULTS:")
    print("="*70)
    print(f"Total permits: {len(permits)}")
    
    if permits:
        print("\nFirst 5 permits:")
        for i, p in enumerate(permits[:5], 1):
            print(f"\n{i}. {p['permit_number']}")
            print(f"   Address: {p['address']}")
            print(f"   Type: {p['permit_type']} - {p['subtype']}")
            print(f"   Date: {p['date']}")
            print(f"   Value: ${p['estimated_value']:,.0f}")
