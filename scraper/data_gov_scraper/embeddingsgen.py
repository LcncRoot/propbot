from openai import OpenAI
import numpy as np
import json
from dotenv import load_dotenv
import os

# Look for .env file in the current directory
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
client = OpenAI()  # This will now find the key from .env

def get_embedding(text):
    """Fetch embedding from OpenAI API"""
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return np.array(response.data[0].embedding, dtype="float32")

def process_data(input_file, output_embeddings, output_metadata):
    """Generates OpenAI embeddings and stores metadata separately for grants & contracts"""
    
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    metadata = []
    embeddings = []

    for i, record in enumerate(data):
        text_for_embedding = f"{record['title']} {record['description']}"
        metadata.append({
            "id": i,
            "opportunity_id": record["opportunity_id"],
            "title": record["title"],
            "description": record["description"],
            "url": record.get("grant_url", record.get("link", "")),
            "type": "grant" if "grant_url" in record else "contract"
        })
        embeddings.append(get_embedding(text_for_embedding))

    # Save embeddings & metadata separately
    np.save(output_embeddings, np.array(embeddings))
    with open(output_metadata, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)

    print(f"✅ Processed {len(metadata)} records for {input_file}")

# Process grants and contracts separately
process_data("grants_data.json", "faiss_grants_embeddings.npy", "faiss_grants_metadata.json")
process_data("filtered_contracts.json", "faiss_contracts_embeddings.npy", "faiss_contracts_metadata.json")
