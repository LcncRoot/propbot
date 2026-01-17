import requests
import json
import sys

API_BASE_URL = "https://api.grants.gov/v1/api"
FETCH_OPPORTUNITY_ENDPOINT = f"{API_BASE_URL}/fetchOpportunity"

HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
}

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
    # Get Opportunity ID from command-line argument or prompt user
    if len(sys.argv) > 1:
        opportunity_id = sys.argv[1]
    else:
        opportunity_id = input("Enter Opportunity ID: ").strip()

    if not opportunity_id.isdigit():
        print("❌ Invalid input. Please enter a numeric Opportunity ID.")
        return

    grant_data = fetch_opportunity_details(opportunity_id)

    if grant_data:
        print("\n✅ Detailed Grant Data:")
        print(json.dumps(grant_data, indent=4))

        # Display all essential grant details
        print("\n📄 Key Information:")
        print(f"Title: {grant_data.get('opportunityTitle', 'N/A')}")
        print(f"Agency: {grant_data.get('topAgencyDetails', {}).get('agencyName', 'N/A')}")
        print(f"Funding Amount: ${grant_data.get('forecast', {}).get('estimatedFundingFormatted', 'N/A')}")
        print(f"Deadline: {grant_data.get('synopsis', {}).get('responseDateDesc', 'N/A')}")
        print(f"Opportunity Number: {grant_data.get('opportunityNumber', 'N/A')}")
        print(f"CFDA Number: {grant_data.get('cfdas', [{}])[0].get('cfdaNumber', 'N/A')}")
        print(f"Synopsis: {grant_data.get('synopsis', {}).get('synopsisDesc', 'N/A')}")
        print(f"Eligibility: {grant_data.get('synopsis', {}).get('applicantEligibilityDesc', 'N/A')}")
        print(f"Funding Instruments: {[fi.get('description', 'N/A') for fi in grant_data.get('fundingInstruments', [])]}")
        print(f"Award Ceiling: ${grant_data.get('synopsis', {}).get('awardCeilingFormatted', 'N/A')}")
        print(f"Award Floor: ${grant_data.get('synopsis', {}).get('awardFloorFormatted', 'N/A')}")
        print(f"Number of Expected Awards: {grant_data.get('synopsis', {}).get('numberOfAwards', 'N/A')}")
        print(f"Contact Name: {grant_data.get('synopsis', {}).get('agencyContactName', 'N/A')}")
        print(f"Contact Email: {grant_data.get('synopsis', {}).get('agencyContactEmail', 'N/A')}")
        print(f"Contact Phone: {grant_data.get('synopsis', {}).get('agencyContactPhone', 'N/A')}")
        print(f"Funding Activity Categories: {[fc.get('description', 'N/A') for fc in grant_data.get('fundingActivityCategories', [])]}")
        print(f"Application URL: {grant_data.get('synopsis', {}).get('fundingDescLinkUrl', 'N/A')}")

        # Check for attachments
        attachments = grant_data.get("synopsisAttachmentFolders", [])
        if attachments:
            print("\n📎 Attachments:")
            for folder in attachments:
                for doc in folder.get("synopsisAttachments", []):
                    print(f"- {doc.get('fileName', 'Unknown File')}")

    else:
        print("\n❌ No grant data retrieved.")

if __name__ == "__main__":
    main()
