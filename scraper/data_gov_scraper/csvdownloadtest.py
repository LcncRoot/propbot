import requests

CSV_URL = "https://sam.gov/data-services/ContractOpportunitiesFullCSV.csv"
headers = {
    "User-Agent": "Mozilla/5.0",
}

response = requests.get(CSV_URL, headers=headers)

# Check if it's an HTML file instead of CSV
if "<!doctype html>" in response.text.lower():
    print("Error: Received an HTML page instead of CSV. The URL might require authentication.")
else:
    with open("contract_opportunities.csv", "wb") as file:
        file.write(response.content)
    print("CSV downloaded successfully.")