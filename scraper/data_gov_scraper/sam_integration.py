import requests
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from root .env
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

# SAM.gov API Endpoint
SAM_API_URL = "https://api.sam.gov/opportunities/v2/search"
SAM_API_KEY = os.getenv("SAM_API_KEY")

if not SAM_API_KEY:
    raise ValueError("SAM_API_KEY not found in environment variables. Check your .env file.")

# Database file (or use PostgreSQL, MongoDB, etc.)
DATABASE_FILE = "sam_contracts.json"

def fetch_sam_contracts():
    """Fetch active contract opportunities from SAM.gov API."""
    today = datetime.today()
    one_year_ago = today - timedelta(days=365)

    posted_from = one_year_ago.strftime("%m/%d/%Y")
    posted_to = today.strftime("%m/%d/%Y")

    params = {
        "api_key": SAM_API_KEY,
        "postedFrom": posted_from,
        "postedTo": posted_to,
        "limit": 50,  # Fetch 50 contracts at a time
    }

    response = requests.get(SAM_API_URL, params=params)

    if response.status_code == 200:
        data = response.json()
        contracts = data.get("opportunitiesData", [])
        print(f"✅ Successfully fetched {len(contracts)} contracts.")
        save_contracts_to_db(contracts)
    else:
        print(f"❌ Error fetching SAM.gov contracts: {response.status_code}")
        print(f"Response: {response.text}")  # Print full response for debugging

def save_contracts_to_db(contracts):
    """Save fetched contracts to a JSON database."""
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, "r") as f:
            existing_contracts = json.load(f)
    else:
        existing_contracts = []

    # Ensure we don't store duplicates
    contract_ids = {c["noticeId"] for c in existing_contracts}
    
    # Clean and add new contracts
    new_contracts = []
    for contract in contracts:
        if contract["noticeId"] not in contract_ids:
            # Clean NaN values before saving
            cleaned_contract = {}
            for key, value in contract.items():
                if isinstance(value, float) and (value != value):  # Check for NaN
                    cleaned_contract[key] = None  # or "N/A" if you prefer
                else:
                    cleaned_contract[key] = value
            new_contracts.append(cleaned_contract)

    existing_contracts.extend(new_contracts)

    with open(DATABASE_FILE, "w") as f:
        json.dump(existing_contracts, f, indent=4)

    print(f"✅ Saved {len(new_contracts)} new contracts to database.")

if __name__ == "__main__":
    fetch_sam_contracts()
