import requests
import json

API_BASE_URL = "https://api.grants.gov/v1/api"
SEARCH_ENDPOINT = f"{API_BASE_URL}/search2"
FETCH_OPPORTUNITY_ENDPOINT = f"{API_BASE_URL}/fetchOpportunity"

HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
}

OPPORTUNITY_ID = 355457  # Explicitly fetching this opportunity


def fetch_opportunity_details(opportunity_id):
    """Fetches detailed grant information for a specific opportunity ID."""
    print(f"\n🔍 Fetching details for Opportunity ID: {opportunity_id}...")
    
    response = requests.post(
        FETCH_OPPORTUNITY_ENDPOINT,
        headers=HEADERS,
        json={"opportunityId": opportunity_id},
        timeout=10
    )

    if response.status_code != 200:
        print(f"❌ ERROR: Failed to fetch opportunity details (Status {response.status_code})")
        return None

    try:
        data = response.json()
        if data.get("errorcode") == 0:
            return data["data"]
        else:
            print(f"⚠️ API returned an error: {data.get('msg')}")
            return None
    except json.JSONDecodeError:
        print("❌ ERROR decoding JSON response")
        return None


def main():
    print("\n🔍 Searching for grant details...")
    
    grant_data = fetch_opportunity_details(OPPORTUNITY_ID)

    if grant_data:
        print("\n✅ Detailed Grant Data:")
        print(json.dumps(grant_data, indent=4))

        # Check for associated documents
        attachments = grant_data.get("synopsisAttachmentFolders", [])
        document_urls = grant_data.get("synopsisDocumentURLs", [])

        if attachments or document_urls:
            print("\n📄 Associated Documents Found:")
            for attachment in attachments:
                print(f"- {attachment.get('folderName', 'Unknown Folder')} (Size: {attachment.get('zipLobSize', 'N/A')})")

            for doc in document_urls:
                print(f"- Document URL: {doc}")
        else:
            print("\n📄 No associated documents found.")

    else:
        print("\n❌ No grant data retrieved.")

if __name__ == "__main__":
    main()
