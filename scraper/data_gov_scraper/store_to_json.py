import json
from parse_xml import parse_grants

JSON_FILE = "grants_data.json"

def store_grants_to_json():
    """Parses the XML file and saves grants to a JSON file."""
    grants = parse_grants("grants_data.xml")

    with open(JSON_FILE, "w") as file:
        json.dump(grants, file, indent=4)

    print(f"✅ Saved {len(grants)} grants to {JSON_FILE}!")

if __name__ == "__main__":
    store_grants_to_json()
