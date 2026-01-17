import requests
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from root .env
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

# SAM.gov API Endpoint
SAM_API_URL = "https://api.sam.gov/opportunities/v2/search"
SAM_DESCRIPTION_URL = "https://api.sam.gov/prod/opportunities/v1/noticedesc"
SAM_API_KEY = os.getenv("SAM_API_KEY")

if not SAM_API_KEY:
    raise ValueError("SAM_API_KEY not found in environment variables. Check your .env file.")

# Database file
DATABASE_FILE = "sam_contracts.json"

def fetch_sam_contracts():
    """Fetch ALL active contract opportunities from SAM.gov API using pagination."""
    today = datetime.today()
    one_year_ago = today - timedelta(days=365)

    posted_from = one_year_ago.strftime("%m/%d/%Y")
    posted_to = today.strftime("%m/%d/%Y")

    limit = 50  # Number of results per request
    offset = 0  # Start from the first page
    total_fetched = 0  # Track total contracts fetched

    while True:
        params = {
            "api_key": SAM_API_KEY,
            "postedFrom": posted_from,
            "postedTo": posted_to,
            "limit": limit,
            "offset": offset,  # Start fetching from the correct position
        }

        response = requests.get(SAM_API_URL, params=params)

        if response.status_code == 200:
            data = response.json()
            contracts = data.get("opportunitiesData", [])

            if not contracts:
                print("✅ No more contracts to fetch.")
                break  # Stop if there are no more contracts

            save_contracts_to_db(contracts)
            total_fetched += len(contracts)

            print(f"✅ Fetched {len(contracts)} contracts (Total: {total_fetched}).")
            offset += limit  # Move to the next batch

        else:
            print(f"❌ Error fetching SAM.gov contracts: {response.status_code}")
            print(f"Response: {response.text}")
            break  # Stop on an error

    print(f"✅ Finished fetching contracts. Total saved: {total_fetched}")

def save_contracts_to_db(contracts):
    """Save fetched contracts to a JSON database safely."""
    existing_contracts = []

    # ✅ Ensure file exists and is not empty
    if not os.path.exists(DATABASE_FILE) or os.path.getsize(DATABASE_FILE) == 0:
        print("⚠️ Warning: Database file is missing or empty. Initializing a new file.")
        with open(DATABASE_FILE, "w") as f:
            json.dump([], f)

    # ✅ Load existing contracts safely
    with open(DATABASE_FILE, "r") as f:
        try:
            existing_contracts = json.load(f)
            if not isinstance(existing_contracts, list):
                raise ValueError("Invalid JSON structure. Resetting database.")
        except (json.JSONDecodeError, ValueError):
            print("❌ Warning: JSON file is corrupted. Resetting database.")
            existing_contracts = []  # Reset the file if it's corrupted
            with open(DATABASE_FILE, "w") as f:
                json.dump([], f)

    # Ensure we don’t store duplicates
    contract_ids = {c["noticeId"] for c in existing_contracts}
    new_contracts = [c for c in contracts if c["noticeId"] not in contract_ids]

    existing_contracts.extend(new_contracts)

    with open(DATABASE_FILE, "w") as f:
        json.dump(existing_contracts, f, indent=4)

    print(f"✅ Saved {len(new_contracts)} new contracts to database.")

if __name__ == "__main__":
    fetch_sam_contracts()
