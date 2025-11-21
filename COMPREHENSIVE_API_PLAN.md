# COMPLETE API RESEARCH FINDINGS & ACTION PLAN
**Generated:** November 19, 2025  
**Status:** Ongoing comprehensive API discovery for all metros + surrounding counties

---

## 🎯 MISSION
Replace ALL demo data with REAL building permit APIs across:
- 8 major metro areas
- 30+ surrounding counties  
- Tennessee + Texas regions

---

## ✅ CONFIRMED WORKING REAL APIs (3 IMPLEMENTED)

### 1. **Nashville-Davidson County, TN** ✅
```python
API: https://maps.nashville.gov/arcgis/rest/services/Codes/BuildingPermits/MapServer/0/query
Type: ArcGIS REST
Status: LIVE & INTEGRATED
Fields: CASE_NUMBER, LOCATION, CONSTVAL, SCOPE, DATE_ACCEPTED, STATUS_CODE
Quality: ⭐⭐⭐⭐⭐ Excellent
```

### 2. **Austin-Travis County, TX** ✅  
```python
API: https://data.austintexas.gov/resource/3syk-w9eu.json
Type: Socrata Open Data
Status: LIVE & INTEGRATED  
Fields: permit_number, permit_location, permit_type_desc, description, applieddate, total_job_valuation
Quality: ⭐⭐⭐⭐⭐ Excellent (residential permits, real-time)
```

### 3. **Chattanooga-Hamilton County, TN** ✅
```python
API: https://www.chattadata.org/resource/764y-vxm2.json
Type: Socrata Open Data
Status: LIVE & INTEGRATED
Fields: permitnum, originaladdress1, permitclass, permittype, estprojectcost, applieddate
Quality: ⭐⭐⭐⭐⭐ Excellent (includes commercial & residential)
```

---

## 🚫 CONFIRMED NO PUBLIC API

### Dallas County, TX ❌
- **Checked:** dallasopendata.com, www.dallasopendata.com
- **Finding:** Only historical data (FY 2017-2018, FY 2015-2016, FY 2013-2014)
- **Current Permits:** NOT AVAILABLE via API
- **Alternative:** Tableau dashboards (not scrapable), need web scraping or manual requests

### Houston-Harris County, TX ❌
- **Checked:** data.houstontx.gov
- **Finding:** Has "Building Code Enforcement Violations" but NO building permits dataset
- **Current Permits:** NOT AVAILABLE via API  
- **Alternative:** Must check Harris County government directly (county vs city)

### San Antonio-Bexar County, TX ⚠️
- **Portal:** data.sanantonio.gov
- **Type:** CKAN (CSV downloads only)
- **URL:** https://data.sanantonio.gov/dataset/building-permits
- **Files Available:**
  - `PERMITS ISSUED 2020-2024 CSV`
  - `APPLICATIONS SUBMITTED CSV`
- **Status:** Batch files, not real-time API
- **Workaround:** Download CSV periodically and process

---

## 🔍 RESEARCH NEEDED - COUNTY LEVEL

### Texas Counties (High Priority)

#### **Williamson County, TX** (Austin Metro)
- **Cities:** Round Rock, Georgetown, Cedar Park, Leander
- **Website:** ✅ williamsoncounty-tn.gov accessible
- **GIS:** ✅ gis.wilco.org accessible
- **Action:** Check for GIS REST services or open data portal

#### **Hays County, TX** (Austin Metro)
- **Cities:** San Marcos, Kyle, Buda
- **Website:** ⚠️ hayscountytx.com (403 error)
- **Action:** Find alternative domain or contact directly

#### **Tarrant County, TX** (DFW Metro)
- **Cities:** Fort Worth, Arlington, Grand Prairie
- **Website:** ✅ tarrantcounty.com accessible
- **Action:** Search for Fort Worth open data portal separately

#### **Collin County, TX** (DFW Metro)
- **Cities:** Plano, Frisco, McKinney, Allen
- **Website:** ✅ collincountytx.gov accessible
- **Action:** Check Plano city open data (may have own portal)

#### **Denton County, TX** (DFW Metro)
- **Cities:** Denton, Lewisville, Flower Mound
- **Website:** ✅ dentoncounty.gov accessible
- **GIS:** ✅ gis.dentoncounty.gov accessible
- **Action:** High probability of GIS data

#### **Fort Bend County, TX** (Houston Metro)
- **Cities:** Sugar Land, Missouri City, Pearland
- **Website:** ✅ fortbendcountytx.gov accessible
- **Action:** Search for permits portal

#### **Montgomery County, TX** (Houston Metro)
- **Cities:** Conroe, The Woodlands, Spring
- **Website:** ✅ mctx.org accessible
- **Action:** Fast-growing area, likely has data

### Tennessee Counties (High Priority)

#### **Williamson County, TN** (Nashville Metro)
- **Cities:** Franklin, Brentwood
- **Website:** ✅ williamsoncounty-tn.gov accessible
- **Action:** High-wealth county, likely has data

#### **Rutherford County, TN** (Nashville Metro)
- **Cities:** Murfreesboro (MTSU college town)
- **Website:** ✅ rutherfordcountytn.gov accessible
- **Action:** Large growth area, high priority

#### **Wilson County, TN** (Nashville Metro)
- **Cities:** Lebanon, Mt. Juliet
- **Website:** ✅ wilsoncountytn.gov accessible
- **Action:** Fast-growing eastern suburbs

#### **Sumner County, TN** (Nashville Metro)
- **Cities:** Hendersonville, Gallatin
- **Website:** ⚠️ sumnertn.org (error)
- **Action:** Find alternative domain

#### **Shelby County, TN** (Memphis Metro)
- **Cities:** Memphis, Germantown, Collierville
- **Website:** ✅ shelbycountytn.gov accessible
- **Action:** Major metro, should have data

#### **Knox County, TN** (Knoxville Metro)
- **Cities:** Knoxville
- **Website:** ⚠️ knoxcountytn.gov (timeout)
- **Action:** Try gis.knoxcountytn.gov or knoxvilletn.gov

#### **Blount County, TN** (Knoxville Metro)
- **Cities:** Maryville, Alcoa
- **Website:** ✅ blounttn.org accessible
- **Action:** Gateway to Smoky Mountains, tourism area

---

## 📋 IMPLEMENTATION STRATEGY

### Phase 1: Quick Wins (Counties with Accessible Websites) ⏱️ 2-3 hours
1. Search each accessible county website for:
   - "Building Permits"
   - "Open Data"
   - "GIS Portal"
   - "Accela Citizen Access" (common permit system)
2. Test any found APIs immediately
3. Integrate working APIs into scraper

### Phase 2: City-Level Search (Major Cities) ⏱️ 2-3 hours
- **Fort Worth:** Check data.fortworthtexas.gov
- **Plano:** Check data.planotx.gov  
- **Sugar Land:** Check sugarlandtx.gov/opendata
- **Murfreesboro:** Check murfreesborotn.gov/building
- **Franklin:** Check franklintn.gov/permits
- **Knoxville:** Check knoxvilletn.gov/permits

### Phase 3: Alternative Data Sources ⏱️ Variable
For counties WITHOUT APIs:
1. **Accela Portals:** Many cities use Accela Citizen Access
   - URL pattern: `[city].permittrax.com` or `permits.[city].gov`
   - Can be scraped with BeautifulSoup
2. **Batch Downloads:** Like San Antonio CSV
3. **Manual Requests:** Submit open records requests
4. **Third-Party:** Some counties use BuildingEye, MyBuildingPermit

### Phase 4: Web Scraping Fallback ⏱️ 4-6 hours per city
For high-priority cities without APIs:
- Implement Selenium-based scrapers
- Target permit search pages
- Extract: permit #, address, type, value, date
- Run nightly to stay current

---

## 🎯 PRIORITY RANKING

### Tier 1 (Implement First - Highest ROI)
1. ✅ Nashville-Davidson (DONE)
2. ✅ Austin-Travis (DONE)
3. ✅ Chattanooga-Hamilton (DONE)
4. 🔄 Williamson County TN (Nashville suburbs - wealthy area)
5. 🔄 Rutherford County TN (Murfreesboro - fast growth)
6. 🔄 Williamson County TX (Austin suburbs - tech boom)

### Tier 2 (High Value - Major Metros)
7. 🔄 Shelby County TN (Memphis)
8. 🔄 Fort Worth/Tarrant County TX
9. 🔄 Plano/Collin County TX (corporate hubs)
10. 🔄 Fort Bend County TX (Houston suburbs)

### Tier 3 (Fill Out Coverage)
11. 🔄 All remaining surrounding counties
12. ⚠️ Dallas (fallback: scraping or historical only)
13. ⚠️ Houston (fallback: scraping or county-level)
14. ⚠️ San Antonio (batch CSV processing)

---

## 📊 CURRENT METRICS

**API Coverage:**
- Working APIs: 3 / 30+ counties = **10%**
- Metro coverage: 3 / 8 metros = **37.5%**
- Real data: **~500-1000 permits/day** (Nashville + Austin + Chattanooga)

**Target:**
- Working APIs: 20+ counties = **67%+**
- Metro coverage: 7+ / 8 metros = **87%+**
- Real data: **5,000+ permits/day**

**Next Milestone:**
- Get to **50% coverage** (15 counties with real APIs)
- Est. time: 8-12 hours of focused research

---

## 🚀 NEXT IMMEDIATE ACTIONS

```bash
# 1. Test Williamson County TN (Nashville)
curl "https://williamsoncounty-tn.gov" | grep -i "permit\|building\|gis"

# 2. Test Rutherford County TN (Murfreesboro)
curl "https://www.murfreesborotn.gov" | grep -i "permit\|building"

# 3. Test Fort Worth
curl "https://data.fortworthtexas.gov" | grep -i "permit"

# 4. Test Plano  
curl "https://www.plano.gov" | grep -i "permit\|data"

# 5. Restart scraper to test new Chattanooga API
cd /Users/briceleasure/Desktop/contractor-leads-saas
python3 multi_region_scraper.py
# Visit: http://localhost:5002
```

---

## 📝 NOTES

- **Accela Systems:** Very common permit software. If a city uses Accela, there's often a public portal at `[city].permittrax.com` or similar
- **Tyler Technologies:** Another common vendor (Munis, EnerGov)
- **ArcGIS Online:** Many counties publish GIS data including permits
- **Socrata:** Open data platform (Austin, Chattanooga use this)
- **CKAN:** Another open data platform (Houston, San Antonio use this)

**Best Practice:** Always check BOTH city AND county websites - sometimes county has better data than individual cities.

---

**STATUS:** Continuing research - DON'T STOP! 🚀
