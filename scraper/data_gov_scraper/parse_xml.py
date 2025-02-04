import xml.etree.ElementTree as ET
import json

# File paths
INPUT_FILE = "grants_data.xml"
OUTPUT_FILE = "grants_data.json"

# XML Namespace
NAMESPACE = {"ns": "http://apply.grants.gov/system/OpportunityDetail-V1.0"}

def parse_grants(xml_file):
    """Parse Grants.gov XML extract and save relevant grants to JSON."""
    tree = ET.parse(xml_file)
    root = tree.getroot()

    grants_list = []
    opportunities = root.findall(".//ns:OpportunitySynopsisDetail_1_0", NAMESPACE)

    print(f"🔍 Found {len(opportunities)} grant opportunities.")

    for grant in opportunities:
        # Debug: Print raw XML to check field names
        print("🔎 RAW GRANT DATA:\n", ET.tostring(grant, encoding="unicode"))

        # Extract data with better error handling
        opportunity_id = grant.find("ns:OpportunityID", NAMESPACE)
        opportunity_id = opportunity_id.text.strip() if opportunity_id is not None else "N/A"

        grant_url_element = grant.find("ns:AdditionalInformationURL", NAMESPACE)
        grant_url = (
            grant_url_element.text.strip() if grant_url_element is not None 
            else f"https://www.grants.gov/web/grants/view-opportunity.html?oppId={opportunity_id}"
        )

        funding_amount = grant.find("ns:EstimatedTotalProgramFunding", NAMESPACE)
        if funding_amount is not None and funding_amount.text:
            try:
                funding_amount = int(funding_amount.text.replace(",", "").split(".")[0])
            except ValueError:
                funding_amount = 0
        else:
            funding_amount = 0

        # Extract CFDA numbers properly
        cfda_numbers = grant.findall("ns:CFDANumber", NAMESPACE)  # Adjusted tag
        cfda_numbers = [cfda.text.strip() for cfda in cfda_numbers if cfda.text] if cfda_numbers else ["N/A"]

        # Construct grant object
        grants_list.append({
            "title": grant.find("ns:OpportunityTitle", NAMESPACE).text.strip() if grant.find("ns:OpportunityTitle", NAMESPACE) is not None else "N/A",
            "agency": grant.find("ns:AgencyName", NAMESPACE).text.strip() if grant.find("ns:AgencyName", NAMESPACE) is not None else "N/A",
            "funding_amount": funding_amount,
            "deadline": grant.find("ns:CloseDate", NAMESPACE).text.strip() if grant.find("ns:CloseDate", NAMESPACE) is not None else "N/A",
            "cfda_number": cfda_numbers,
            "opportunity_id": opportunity_id,
            "description": grant.find("ns:Description", NAMESPACE).text.strip() if grant.find("ns:Description", NAMESPACE) is not None else "N/A",
            "grant_url": grant_url
        })

    # Save to JSON
    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(grants_list, file, indent=4, ensure_ascii=False)

    print(f"✅ Parsed {len(grants_list)} grants and saved to {OUTPUT_FILE}!")

# Run parser
if __name__ == "__main__":
    parse_grants(INPUT_FILE)
