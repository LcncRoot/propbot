import json
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List

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

def load_grants():
    """Load grants from the JSON file."""
    try:
        with open(GRANTS_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

@app.get("/grants")
def get_all_grants(limit: int = Query(10, description="Number of grants to return")):
    """Returns a paginated list of grants."""
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
            "opportunity_id": g["opportunity_id"],  # ✅ Ensure opportunity_id is included
            "description": g["description"],
            "grant_url": g["grant_url"],
        }
        for g in grants if query.lower() in g["title"].lower() 
                          or query.lower() in g["agency"].lower()
                          or query.lower() in g["opportunity_id"].lower()  # ✅ Search includes opportunity_id
    ]
    
    return {"matches": matches[:limit], "total_matches": len(matches)}

@app.get("/grant/{opportunity_id}")
def get_grant_by_id(opportunity_id: str):
    """Retrieve details of a grant by opportunity ID."""
    grants = load_grants()
    grant = next((g for g in grants if g["opportunity_id"] == opportunity_id), None)
    if grant:
        return grant
    return {"error": "Grant not found"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
