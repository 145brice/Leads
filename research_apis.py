#!/usr/bin/env python3
"""
Research script to find REAL building permit APIs for all cities
"""
import requests
import json

def test_api(name, url, params=None):
    """Test an API endpoint"""
    try:
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        response = requests.get(url, params=params, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    print(f"   ✅ SUCCESS! Found {len(data)} records")
                    print(f"   Sample fields: {list(data[0].keys())[:10]}")
                    return True
                elif isinstance(data, dict) and 'features' in data:
                    print(f"   ✅ SUCCESS! Found {len(data['features'])} features")
                    return True
                else:
                    print(f"   ⚠️  Response format: {type(data)}")
            except:
                print(f"   ⚠️  Not JSON")
        else:
            print(f"   ❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    return False

# ==================== TEXAS CITIES ====================

print("="*70)
print("TEXAS CITIES - Building Permit API Research")
print("="*70)

# Austin - Try common Socrata patterns
test_api("Austin - Residential Permits", 
         "https://data.austintexas.gov/resource/3syk-w9eu.json",
         {"$limit": "5"})

test_api("Austin - Issued Construction Permits",
         "https://data.austintexas.gov/resource/3m5p-pqeq.json",
         {"$limit": "5"})

test_api("Austin - Building Permits (v1)",
         "https://data.austintexas.gov/resource/8h6p-5cht.json",
         {"$limit": "5"})

# Dallas
test_api("Dallas - Building Permits",
         "https://www.dallasopendata.com/resource/rbdn-nurt.json",
         {"$limit": "5"})

test_api("Dallas - Construction Permits",
         "https://www.dallasopendata.com/resource/ce45-fdnk.json",
         {"$limit": "5"})

# San Antonio
test_api("San Antonio - Building Permits",
         "https://data.sanantonio.gov/resource/6v7m-p87p.json",
         {"$limit": "5"})

test_api("San Antonio - Development Services",
         "https://data.sanantonio.gov/resource/nxh7-e6px.json",
         {"$limit": "5"})

# Houston - Try city data portals
test_api("Houston - Building Permits",
         "https://data.houstontx.gov/resource/cai6-vj6c.json",
         {"$limit": "5"})

test_api("Houston - Construction Permits",
         "https://cohgis-mycity.opendata.arcgis.com/datasets/building-permits.json")

# ==================== TENNESSEE CITIES ====================

print("\n" + "="*70)
print("TENNESSEE CITIES - Building Permit API Research")
print("="*70)

# Memphis/Shelby
test_api("Memphis - Building Permits",
         "https://data.memphistn.gov/resource/wiv8-6yce.json",
         {"$limit": "5"})

test_api("Shelby County - Building Permits",
         "https://data.shelbycountytn.gov/resource/building-permits.json")

# Chattanooga/Hamilton
test_api("Chattanooga - Open Data",
         "https://data.chattlibrary.org/resource/permits.json")

test_api("Hamilton County - Building",
         "https://maps.hamiltontn.gov/arcgis/rest/services",
         None)

# Knoxville/Knox
test_api("Knox County - Building Permits",
         "https://knoxcounty.org/apps/permits/api.json")

test_api("Knoxville - ArcGIS Permits",
         "https://gis.knoxcountytn.gov/arcgis/rest/services")

print("\n" + "="*70)
print("Research Complete!")
print("="*70)
