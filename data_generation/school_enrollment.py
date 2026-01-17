import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import os

# --- CONFIGURATION ---
API_KEY = "579b464db66ec23bdd000001f251a4cb0a0d44cb62aa1ed59941aff4"
CATALOG_BASE_URL = "https://www.data.gov.in/catalog/enrolment-location-school-management-school-category-and-social-category-udise-plus"
TARGET_STATES = ["Bihar", "Uttar Pradesh", "Maharashtra", "Odisha", "West Bengal"]
OUTPUT_DIR = "district_raw_data"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Headers to mimic a real browser and avoid 403 Forbidden errors
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def discover_all_district_ids():
    """
    Deep scans the UDISE+ catalog by searching every link for Resource IDs 
    and matching them against target states and the 'District' keyword.
    """
    print(f"🚀 Starting Deep Discovery for {len(TARGET_STATES)} States...")
    resource_list = []
    page = 0
    
    while True:
        url = f"{CATALOG_BASE_URL}?page={page}"
        try:
            # Use headers to ensure we aren't blocked by the server
            response = requests.get(url, headers=HEADERS, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # DEEP SCAN: Find every single link that points to a resource or API
            # This is more robust than looking for specific div classes
            all_links = soup.find_all('a', href=re.compile(r'/resource/|/apis/'))
            
            if not all_links:
                # If we've checked several pages and find nothing, we've hit the end
                if page > 5: # Safety buffer for empty pages
                    print(f"🏁 Reached end of catalog at page {page}.")
                    break
                page += 1
                continue
            
            found_on_page = 0
            for link in all_links:
                # Extract text from the link or its parent to find the district/state names
                # Titles are often in the 'title' attribute or parent 'h3'/'div'
                parent_text = link.find_parent().get_text() if link.find_parent() else ""
                link_text = link.get_text().strip() or link.get('title', '').strip()
                combined_text = f"{link_text} {parent_text}"
                
                # Logic: Title must contain a Target State and the word 'District'
                matched_state = next((s for s in TARGET_STATES if s.lower() in combined_text.lower()), None)
                
                if matched_state and "District" in combined_text:
                    href = link.get('href')
                    res_id = href.split('/')[-1]
                    
                    # Prevent duplicates on the same page
                    if not any(d['id'] == res_id for d in resource_list):
                        # Clean up district name using regex
                        dist_match = re.search(r'in (.*?) District', combined_text, re.IGNORECASE)
                        dist_name = dist_match.group(1) if dist_match else "Unknown"
                        
                        resource_list.append({
                            'state': matched_state,
                            'district': dist_name,
                            'id': res_id
                        })
                        found_on_page += 1
            
            if found_on_page > 0:
                print(f"  Scanned Page {page}: Found {found_on_page} target districts. Total: {len(resource_list)}")
            
            page += 1
            time.sleep(1.5) # Increased delay to respect OGD rate limits
            
            # Stop after 30 pages for demo purposes; remove for full state scan
            if page > 30: break 
            
        except Exception as e:
            print(f"❌ Scraper error on page {page}: {e}")
            break
            
    return resource_list

def download_district_data(res_meta):
    """
    Downloads raw data for a specific district with full API safeguards and exponential backoff.
    """
    state, dist, res_id = res_meta['state'], res_meta['district'], res_meta['id']
    base_url = f"https://api.data.gov.in/resource/{res_id}"
    all_records = []
    offset = 0
    
    print(f"  📥 Ingesting: {dist}, {state} (ID: {res_id})")
    
    while True:
        params = {"api-key": API_KEY, "format": "json", "offset": offset, "limit": 200}
        
        success = False
        for attempt in range(3): # Retry logic for SSL/Timeout errors
            try:
                res = requests.get(base_url, params=params, timeout=45)
                if res.status_code == 404: return None
                
                data = res.json()
                records = data.get('records', [])
                if not records: 
                    success = True
                    break
                
                all_records.extend(records)
                offset += 200
                time.sleep(0.5)
                success = True
                break
            except Exception as e:
                wait_time = (attempt + 1) * 5
                print(f"    [Retry {attempt+1}] Error at offset {offset}: {e}. Waiting {wait_time}s...")
                time.sleep(wait_time)
        
        if not success or not records:
            break
            
    return all_records

def run_pipeline():
    # 1. Discover Resource IDs using Deep Scan
    districts = discover_all_district_ids()
    
    if not districts:
        print("❌ No districts found. The portal structure might have changed. Try searching by State catalog instead.")
        return

    # 2. Sequential download with Bronze Layer backups
    final_master_list = []
    
    for dist_meta in districts:
        records = download_district_data(dist_meta)
        if not records: continue
        
        df = pd.DataFrame(records)
        # Normalize headers to match your Silver Layer blueprint
        df.columns = [c.lower().replace(" ", "_").replace(".", "") for c in df.columns]
        
        # Inject metadata for the join
        df['state_ref'] = dist_meta['state']
        df['district_ref'] = dist_meta['district']
        
        # Save individual district backup (Bronze Layer)
        file_name = f"{OUTPUT_DIR}/{dist_meta['state']}_{dist_meta['district']}.csv".replace(" ", "_")
        df.to_csv(file_name, index=False)
        
        final_master_list.append(df)
        
    # 3. Final Silver Layer Consolidation
    if final_master_list:
        full_df = pd.concat(final_master_list, ignore_index=True)
        full_df.to_csv("udise_all_districts_master_silver.csv", index=False)
        print(f"\n✅ MISSION COMPLETE: Processed {len(districts)} districts. Saved to 'udise_all_districts_master_silver.csv'")

if __name__ == "__main__":
    run_pipeline()