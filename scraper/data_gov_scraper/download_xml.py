import requests
import zipfile
import os
from bs4 import BeautifulSoup

BASE_URL = "https://www.grants.gov/xml-extract/"
XML_FILE = "grants_data.xml"

def get_latest_zip_url():
    """Scrape Grants.gov XML Extract page to get the actual latest ZIP file URL."""
    print(f"🔍 Fetching Grants.gov extract directory: {BASE_URL}")
    response = requests.get(BASE_URL)

    if response.status_code != 200:
        print(f"❌ ERROR: Failed to fetch Grants.gov directory. HTTP Status: {response.status_code}")
        return None, None

    soup = BeautifulSoup(response.text, "html.parser")

    # Find all <a> tags with class="usa-link" that end in .zip
    zip_links = [a["href"] for a in soup.find_all("a", class_="usa-link") if a["href"].endswith(".zip")]

    if not zip_links:
        print("❌ ERROR: No ZIP file found on the page. Check the HTML structure.")
        return None, None

    latest_zip_file = sorted(zip_links)[-1]  # Get the most recent one
    print(f"✅ Found latest ZIP file: {latest_zip_file}")
    return latest_zip_file, latest_zip_file.split("/")[-1]

def download_latest_grants():
    """Download the latest Grants.gov ZIP file and extract the XML."""
    zip_url, zip_filename = get_latest_zip_url()
    if not zip_url:
        print("❌ ERROR: No valid ZIP URL found.")
        return

    print(f"📥 Downloading ZIP file: {zip_url}")

    response = requests.get(zip_url, stream=True)

    if response.status_code == 200:
        with open(zip_filename, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"✅ Downloaded {zip_filename}!")

        # Verify the file exists
        if not os.path.exists(zip_filename):
            print(f"❌ ERROR: {zip_filename} was not saved correctly.")
            return

        # Extract XML from ZIP
        try:
            with zipfile.ZipFile(zip_filename, "r") as zip_ref:
                zip_ref.extractall(".")
            print(f"✅ Extracted XML file!")

            # Rename extracted XML file
            for extracted_file in zip_ref.namelist():
                if extracted_file.endswith(".xml"):
                    os.rename(extracted_file, XML_FILE)
                    print(f"✅ Renamed {extracted_file} to {XML_FILE}")
        except zipfile.BadZipFile:
            print("❌ ERROR: The downloaded file is not a valid ZIP archive.")
            os.remove(zip_filename)  # Remove the bad file

    else:
        print(f"❌ ERROR: Failed to download ZIP file. HTTP Status: {response.status_code}")

if __name__ == "__main__":
    download_latest_grants()
