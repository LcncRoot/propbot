import requests
import json
import datetime

SAM_API_KEY = "vzbgHmOMSYexaLBCKeyc8UH7GWcRyB5TLW9tBcc0"
BASE_URL = "https://api.sam.gov/opportunities/v2/search"

def fetch_sam_contracts(limit=10):
    """Fetches contract opportunities from SAM.gov API with correct parameters."""
    
    # Ensure correct date range (1-year limit)
    today = datetime.datetime.today()
    one_year_ago = today - datetime.timedelta(days=365)
    
    params = {
        "api_key": SAM_API_KEY,
        "postedFrom": one_year_ago.strftime("%m/%d/%Y"),  
        "postedTo": today.strftime("%m/%d/%Y"),
        "limit": limit,
    }

    headers = {"Accept": "application/json"}

    print(f"🔍 Fetching SAM.gov contracts from {BASE_URL} with params: {params}")

    response = requests.get(BASE_URL, headers=headers, params=params)

    print(f"🔎 Response Status: {response.status_code}")

    if response.status_code == 200:
        try:
            data = response.json()
            with open("sam_contracts.json", "w") as file:
                json.dump(data, file, indent=4)
            print(f"✅ Saved {len(data.get('opportunitiesData', []))} contracts to sam_contracts.json")
            return data.get("opportunitiesData", [])
        except json.JSONDecodeError:
            print("❌ ERROR: SAM.gov returned invalid JSON.")
            return []
    
    elif response.status_code == 429:
        print("⚠️ RATE LIMITED! Try again later.")
    
    else:
        print(f"❌ ERROR: Failed to fetch SAM.gov data. HTTP {response.status_code}")
        print(f"🔎 Response Content: {response.text}")

    return []

if __name__ == "__main__":
    fetch_sam_contracts(limit=10)
