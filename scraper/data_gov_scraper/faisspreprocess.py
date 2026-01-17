import json
import re

def clean_text(text):
    """Removes special characters, HTML tags, and excessive spaces."""
    text = re.sub(r"<[^>]+>", "", text)  # Remove HTML tags
    text = re.sub(r"\s+", " ", text).strip()  # Normalize spaces
    return text.lower()  # Convert to lowercase

def preprocess_data():
    """Loads grants & contracts, preprocesses them, and stores in a structured JSON file."""
    
    # Load grants data
    with open("grants_data.json", "r", encoding="utf-8") as f:
        grants = json.load(f)

    # Load contracts data
    with open("filtered_contracts.json", "r", encoding="utf-8") as f:
        contracts = json.load(f)

    metadata = []
    index_id = 0

    # Process grants
    for grant in grants:
        metadata.append({
            "id": index_id,
            "opportunity_id": grant["opportunity_id"],
            "title": clean_text(grant["title"]),
            "description": clean_text(grant["description"]),
            "text_for_embedding": clean_text(grant["title"] + " " + grant["description"]),
            "url": grant["grant_url"],
            "type": "grant"
        })
        index_id += 1

    # Process contracts
    for contract in contracts:
        metadata.append({
            "id": index_id,
            "opportunity_id": contract["opportunity_id"],
            "title": clean_text(contract["title"]),
            "description": clean_text(contract["description"]),
            "text_for_embedding": clean_text(contract["title"] + " " + contract["description"]),
            "url": contract["link"],
            "type": "contract"
        })
        index_id += 1

    # Save preprocessed data
    with open("faiss_metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)

    print(f"✅ Preprocessed {len(metadata)} records and saved to faiss_metadata.json")

if __name__ == "__main__":
    preprocess_data()
 