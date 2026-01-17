import pandas as pd
import json
import chardet

# Define the CSV file path
CSV_FILE_PATH = "ContractOpportunitiesFullCSV.csv"

# Detect file encoding
def detect_encoding(file_path):
    with open(file_path, "rb") as f:
        result = chardet.detect(f.read(100000))
    return result["encoding"]

# Load and parse CSV with detected encoding
def parse_csv(file_path):
    encoding = detect_encoding(file_path)
    df = pd.read_csv(file_path, encoding=encoding, low_memory=False, dtype={"NaicsCode": str})
    return df

# Grab ALL contracts instead of just 10
def get_all_contracts(df):
    return df.copy()

# Main function to execute the workflow
def main():
    df = parse_csv(CSV_FILE_PATH)
    
    # Ensure Description and AdditionalInfoLink are not NaN
    df.loc[:, "Description"] = df["Description"].fillna("")
    df.loc[:, "AdditionalInfoLink"] = df["AdditionalInfoLink"].fillna("")
    
    # Fill NaN values with None (or "N/A" if you prefer) for all columns
    df = df.replace({float('nan'): None})

    # Standardize JSON output format to match grants data
    json_data = df.rename(columns={
        "Sol#": "opportunity_id",
        "Title": "title",
        "NaicsCode": "naics_code",
        "ResponseDeadLine": "response_deadline",
        "Description": "description",
        "AdditionalInfoLink": "link"
    })[["opportunity_id", "title", "naics_code", "response_deadline", "description", "link"]].to_dict(orient="records")
    
    # Save JSON output in readable format
    with open("filtered_contracts.json", "w") as json_file:
        json.dump(json_data, json_file, indent=4)

    print(f"Filtered contracts saved to filtered_contracts.json with {len(json_data)} entries.")

if __name__ == "__main__":
    main()
