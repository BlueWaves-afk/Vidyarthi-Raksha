import requests
import pandas as pd
import time
import os

# Configuration
API_KEY = "579b464db66ec23bdd000001f251a4cb0a0d44cb62aa1ed59941aff4"
RESOURCE_ID = "ecd49b12-3084-4521-8f7e-ca8bf72069ba"
BASE_URL = f"https://api.data.gov.in/resource/{RESOURCE_ID}"

# Demo States
TARGET_STATES = ["Bihar", "Uttar Pradesh", "Maharashtra", "Odisha", "West Bengal"]

def fetch_demo_data():
    all_records = []

    # --- PHASE 0: COLUMN DISCOVERY ---
    # Fetch 1 record to see what the actual column names are for this session
    print("Checking API column names...")
    try:
        disc_res = requests.get(BASE_URL, params={"api-key": API_KEY, "format": "json", "limit": 1})
        disc_data = disc_res.json()
        sample_record = disc_data.get('records', [{}])[0]
        actual_keys = list(sample_record.keys())
        
        # Identify the correct keys dynamically
        # Filters often need exact case; response keys often have underscores
        state_key = next((k for k in actual_keys if k.lower() == 'state'), 'State')
        age_0_5_key = next((k for k in actual_keys if '0_5' in k or '0 5' in k), 'Age_0_5')
        age_5_17_key = next((k for k in actual_keys if '5_17' in k or '5 17' in k), 'Age_5_17')
        age_18_key = next((k for k in actual_keys if '18' in k), 'Age_18_Plus')
        
        print(f"Detected Keys -> State: {state_key}, 0-5: {age_0_5_key}, 5-17: {age_5_17_key}")
    except Exception as e:
        print(f"Discovery failed: {e}")
        return None

    # --- PHASE 1: DOWNLOAD RAW DATA (BRONZE) ---
    for state in TARGET_STATES:
        # Multi-format fallback for messy government data
        # Tries "Bihar", "BIHAR", and "bihar"
        formats_to_try = [state, state.upper(), state.lower()]
        
        state_found = False
        for state_format in formats_to_try:
            print(f"Trying format '{state_format}' for {state}...")
            offset = 0
            limit = 100
            
            # Reset for this specific format attempt
            format_records = []
            
            while True:
                params = {
                    "api-key": API_KEY,
                    "format": "json",
                    "offset": offset,
                    "limit": limit,
                    f"filters[{state_key}]": state_format
                }
                
                try:
                    response = requests.get(BASE_URL, params=params)
                    data = response.json()
                    records = data.get('records', [])
                    
                    if not records:
                        break
                    
                    format_records.extend(records)
                    offset += limit
                    time.sleep(0.2) 
                    
                except Exception as e:
                    print(f"Error fetching: {e}")
                    break
            
            if format_records:
                print(f"Successfully retrieved {len(format_records)} records for {state} using '{state_format}'")
                all_records.extend(format_records)
                state_found = True
                break # Format found, stop trying other cases for this state
        
        if not state_found:
            print(f"WARNING: No data found for {state} in any capitalization format.")

    if not all_records:
        print("CRITICAL: No records retrieved for any states. Check API key/Network.")
        return None

    # Save Bronze Layer
    df_bronze = pd.DataFrame(all_records)
    df_bronze.to_csv("aadhaar_raw_bronze.csv", index=False)
    print(f"\n[Bronze Layer] Saved {len(df_bronze)} raw records to 'aadhaar_raw_bronze.csv'")

    # --- PHASE 2: TRANSFORMATION (SILVER) ---
    df = df_bronze.copy()
    
    # Use the discovered keys for mapping to ensure no KeyErrors
    df['clean_0_5'] = pd.to_numeric(df[age_0_5_key], errors='coerce').fillna(0)
    df['clean_5_17'] = pd.to_numeric(df[age_5_17_key], errors='coerce').fillna(0)
    df['clean_18_plus'] = pd.to_numeric(df[age_18_key], errors='coerce').fillna(0)

    # Logic: Estimate Pending MBU (Mandatory for Hackathon Blueprint)
    df['mbu_due_5'] = (df['clean_0_5'] * 0.15).round(0) 
    df['mbu_due_15'] = (df['clean_5_17'] * 0.10).round(0)
    df['total_pending_mbu'] = df['mbu_due_5'] + df['mbu_due_15']
    
    # Logic: Demand Score (Gold Layer)
    # Normalizing total activity to create a priority rank
    total_vol = df['clean_0_5'] + df['clean_5_17'] + df['clean_18_plus'] + df['total_pending_mbu']
    max_val = total_vol.max() if total_vol.max() > 0 else 1
    df['demand_score'] = (total_vol / max_val * 100).round(2)
    
    # Save to CSV
    df.to_csv("aadhaar_silver_layer_demo.csv", index=False)
    print("[Silver Layer] Derived data saved to 'aadhaar_silver_layer_demo.csv'")
    
    return df

if __name__ == "__main__":
    df_demo = fetch_demo_data()