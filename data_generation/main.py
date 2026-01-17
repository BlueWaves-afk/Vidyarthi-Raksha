import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import time

# --- CONFIGURATION ---
BASE_CATALOG_URL = "https://www.data.gov.in/catalog/enrolment-location-school-management-school-category-and-social-category-udise-plus"
TARGET_STATES = ["Bihar", "Uttar Pradesh", "Maharashtra", "Odisha", "West Bengal"]

# Headers to ensure the server sees us as a real browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

def get_uuid_from_nuxt_state(session, resource_url):
    """
    Visits the district page and extracts the machine UUID from the Nuxt state.
    This is the most reliable way to get the ID shown in the API tab.
    """
    try:
        if not resource_url.startswith('http'):
            resource_url = "https://www.data.gov.in" + resource_url
            
        res = session.get(resource_url, headers=HEADERS, timeout=20)
        
        # Look for the UUID in the Nuxt state as seen in your body snippet:
        # It looks like: uuid:"2bf668f2-3f8f-49f9-a125-761bff74e1a4"
        uuid_match = re.search(r'uuid:"([a-f0-9\-]{36})"', res.text)
        
        if uuid_match:
            return uuid_match.group(1)
        
        # Fallback to general UUID pattern
        fallback = re.search(r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}', res.text)
        return fallback.group(0) if fallback else None
    except Exception:
        return None

def run_discovery():
    print(f"🚀 Starting Discovery for {TARGET_STATES}...")
    session = requests.Session()
    final_registry = []

    for state in TARGET_STATES:
        print(f"  🔍 Scanning State: {state}")
        page = 0
        
        while True:
            # Construct search URL with filters
            url = f"{BASE_CATALOG_URL}?apiavailable=1&title={state}&sortby=_score&page={page}"
            
            try:
                response = session.get(url, headers=HEADERS, timeout=30)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # TARGETING: grid-header > h3 > a (Exactly as in your body snippet)
                district_links = soup.select('div.grid-header h3 a')
                
                if not district_links:
                    # Broad fallback if selector fails
                    district_links = soup.find_all('a', href=re.compile(r'/resource/enrolment-location'))

                if not district_links:
                    print(f"    🏁 Reached end for {state} at page {page}.")
                    break
                
                found_on_page = 0
                for link in district_links:
                    href = link.get('href')
                    title_text = link.get_text().strip()
                    
                    # Filter for district resources for the specific state
                    if "District" in title_text and state.lower() in title_text.lower():
                        if any(d['url'] == href for d in final_registry): continue
                            
                        print(f"      📍 Found: {title_text[:45]}...")
                        res_id = get_uuid_from_nuxt_state(session, href)
                        
                        if res_id:
                            # Extract clean district name
                            dist_match = re.search(r'in (.*?) District', title_text, re.IGNORECASE)
                            dist_name = dist_match.group(1) if dist_match else "Unknown"
                            
                            final_registry.append({
                                'state': state,
                                'district': dist_name,
                                'id': res_id,
                                'url': href
                            })
                            found_on_page += 1
                            time.sleep(1.2) # Safety delay

                print(f"    [+] Page {page}: Mapped {found_on_page} districts.")
                
                if found_on_page == 0: break
                page += 1
                time.sleep(2)
                if page > 15: break # Demo limit
                
            except Exception as e:
                print(f"    [!] Error: {e}")
                break
                
    if final_registry:
        df = pd.DataFrame(final_registry)
        df.to_csv("udise_resource_registry_v3.csv", index=False)
        print(f"\n✅ DONE: Captured {len(df)} Resource IDs.")
    else:
        print("\n❌ Still no results. The server may be blocking the automated requests.")

if __name__ == "__main__":
    run_discovery()