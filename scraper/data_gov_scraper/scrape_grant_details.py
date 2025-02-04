import requests
from bs4 import BeautifulSoup
import json
import time
import random

INPUT_FILE = "./grants_data.json"
OUTPUT_FILE = "./grants_data_enriched.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
}

def scrape_grant_details(grant_url):
    """Scrapes a Grants.gov page for detailed grant information."""
    try:
        response = requests.get(grant_url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            print(f"❌ ERROR: Failed to fetch {grant_url} (Status {response.status_code})")
            return {}

        soup = BeautifulSoup(response.text, "html.parser")

        # Extract general info
        details = {}

        # Funding amount (if present)
        funding_section = soup.find("div", class_="grants-amount")
        details["funding_details"] = funding_section.text.strip() if funding_section else "Not Available"

        # Eligibility
        eligibility_section = soup.find("div", class_="grants-eligibility")
        details["eligibility_details"] = eligibility_section.text.strip() if eligibility_section else "Not Available"

        # Application Steps
        application_section = soup.find("div", class_="grants-application-instructions")
        details["application_steps"] = application_section.text.strip() if application_section else "Not Available"

        # Required Documents
        required_docs_section = soup.find("div", class_="grants-required-documents")
        details["required_documents"] = required_docs_section.text.strip() if required_docs_section else "Not Available"

        return details

    except Exception as e:
        print(f"❌ ERROR scraping {grant_url}: {e}")
        return {}

def update_grant_data(limit=20):  # Default limit to 20 results for testing
    """Loops through grants and updates them with additional details."""
    with open(INPUT_FILE, "r") as file:
        grants = json.load(file)

    updated_grants = []
    total_grants = min(len(grants), limit)  # Ensure we don't exceed total grants

    for i, grant in enumerate(grants[:total_grants]):  # ✅ Process only `limit` grants
        print(f"🔍 Scraping grant {i+1}/{total_grants}: {grant['title']}")

        # Ensure 'grant_url' exists
        grant_url = grant.get("grant_url", "N/A")

        # Skip if no valid grant URL
        if grant_url == "N/A" or not grant_url.startswith("http"):
            print("⚠️ Skipping: No valid grant URL available.")
            continue

        # Scrape the grant details
        grant_details = scrape_grant_details(grant_url)

        # Merge the details into the original grant data
        grant.update(grant_details)
        updated_grants.append(grant)

        # Randomized sleep (to avoid bans)
        time.sleep(random.uniform(1.5, 3.5))

    # Save the enriched data
    with open(OUTPUT_FILE, "w") as file:
        json.dump(updated_grants, file, indent=4)

    print(f"✅ Saved enriched grants data to {OUTPUT_FILE}")

if __name__ == "__main__":
    update_grant_data(limit=20)  # ✅ Only scrape 20 grants for testing

