import json
import requests
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from fastapi.responses import FileResponse
import os

app = FastAPI()

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (for development)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GRANTS_FILE = "../scraper/data_gov_scraper/grants_data.json"
API_URL = "https://api.training.grants.gov/v1/api/fetchOpportunity"
DOCUMENTS_DIR = "../scraper/data_gov_scraper/documents/"

def load_grants():
    """Load grants from the JSON file."""
    try:
        with open(GRANTS_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def fetch_grant_details(opportunity_id: str):
    """Fetch detailed grant data from the API and return all available fields."""
    try:
        response = requests.post(API_URL, json={"opportunityId": opportunity_id})
        response.raise_for_status()

        api_data = response.json().get("data", {})

        if not api_data:
            return {"error": "No details found for this grant."}

        return {
            "title": api_data.get("opportunityTitle"),
            "agency": api_data.get("topAgencyDetails", {}).get("agencyName"),
            "description": api_data.get("synopsis", {}).get("synopsisDesc"),
            "funding_amount": api_data.get("forecast", {}).get("estimatedFundingFormatted"),
            "deadline": api_data.get("synopsis", {}).get("responseDateDesc"),
            "contact_name": api_data.get("synopsis", {}).get("agencyContactName"),
            "contact_email": api_data.get("synopsis", {}).get("agencyContactEmail"),
            "contact_phone": api_data.get("synopsis", {}).get("agencyContactPhone"),
            "cfda_number": api_data.get("cfdas", [{}])[0].get("cfdaNumber", "N/A"),
            "funding_instruments": [fi.get("description") for fi in api_data.get("fundingInstruments", [])],
            "funding_categories": [fc.get("description") for fc in api_data.get("fundingActivityCategories", [])],
            "eligibility": api_data.get("synopsis", {}).get("applicantEligibilityDesc"),
            "attachments": api_data.get("synopsisAttachmentFolders", []),
        }
    
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch grant details: {str(e)}"}

@app.get("/grants")
def get_all_grants(limit: int = Query(10, description="Number of grants to return")):
    """Returns a paginated list of grants from the local JSON file."""
    grants = load_grants()
    return {"grants": grants[:limit], "total": len(grants)}

@app.get("/search")
def search_grants(query: str = "", limit: int = Query(10, description="Number of results to return")):
    """Search for grants matching a query in the title, agency name, or opportunity ID."""
    grants = load_grants()
    
    if not query.strip():
        return {"matches": grants[:limit], "total_matches": len(grants)}
    
    matches = [
        {
            "title": g["title"],
            "agency": g["agency"],
            "funding_amount": g["funding_amount"],
            "deadline": g["deadline"],
            "cfda_number": g["cfda_number"],
            "opportunity_id": g["opportunity_id"],
            "description": g["description"],
            "grant_url": g["grant_url"],
        }
        for g in grants if query.lower() in g["title"].lower() 
                          or query.lower() in g["agency"].lower()
                          or query.lower() in g["opportunity_id"].lower()
    ]
    
    return {"matches": matches[:limit], "total_matches": len(matches)}

@app.get("/grant/{opportunity_id}")
def get_grant_by_id(opportunity_id: str, fetch_details: Optional[bool] = False):
    """Retrieve grant by opportunity ID. Fetch details from API if requested."""
    grants = load_grants()
    grant = next((g for g in grants if g["opportunity_id"] == opportunity_id), None)

    if grant:
        if fetch_details:
            details = fetch_grant_details(opportunity_id)
            grant.update(details)
        return grant
    return {"error": "Grant not found"}

@app.get("/documents/{doc_id}")
def get_document(doc_id: str):
    """Serve grant-related documents."""
    file_path = os.path.join(DOCUMENTS_DIR, doc_id)
    
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="application/pdf", filename=doc_id)
    
    return {"error": "Document not found"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
