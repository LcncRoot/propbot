"""Grants.gov data source fetcher."""

import os
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from typing import Iterator

import requests
from bs4 import BeautifulSoup

from .base import BaseSource
from ..config import config


class GrantsGovSource(BaseSource):
    """Fetcher for Grants.gov opportunities via XML extract."""

    # XML namespace for Grants.gov data
    NAMESPACE = {"ns": "http://apply.grants.gov/system/OpportunityDetail-V1.0"}

    def get_source_name(self) -> str:
        return "grants.gov"

    def fetch(self) -> Iterator[dict]:
        """
        Download and parse Grants.gov XML extract.

        Yields:
            Standardized opportunity dictionaries.
        """
        # Get latest ZIP URL
        zip_url = self._get_latest_zip_url()
        if not zip_url:
            print("Failed to find Grants.gov ZIP URL")
            return

        # Download and extract XML
        xml_path = self._download_and_extract(zip_url)
        if not xml_path:
            print("Failed to download Grants.gov data")
            return

        # Parse and yield opportunities
        try:
            yield from self._parse_xml(xml_path)
        finally:
            # Cleanup temp file
            if os.path.exists(xml_path):
                os.remove(xml_path)

    def _get_latest_zip_url(self) -> str | None:
        """Scrape Grants.gov to find the latest XML extract ZIP URL."""
        print(f"Fetching Grants.gov extract directory: {config.GRANTS_XML_URL}")

        try:
            response = requests.get(config.GRANTS_XML_URL, timeout=30)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching Grants.gov directory: {e}")
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        # Find all ZIP links
        zip_links = [
            a["href"]
            for a in soup.find_all("a", class_="usa-link")
            if a.get("href", "").endswith(".zip")
        ]

        if not zip_links:
            print("No ZIP files found on Grants.gov extract page")
            return None

        # Get the most recent one (sorted alphabetically, latest is last)
        latest_zip = sorted(zip_links)[-1]
        print(f"Found latest ZIP: {latest_zip}")

        return latest_zip

    def _download_and_extract(self, zip_url: str) -> str | None:
        """Download ZIP and extract XML to temp file."""
        print(f"Downloading: {zip_url}")

        try:
            response = requests.get(zip_url, stream=True, timeout=300)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error downloading ZIP: {e}")
            return None

        # Save to temp file
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp_zip:
            for chunk in response.iter_content(chunk_size=8192):
                tmp_zip.write(chunk)
            tmp_zip_path = tmp_zip.name

        # Extract XML
        try:
            with zipfile.ZipFile(tmp_zip_path, "r") as zf:
                xml_files = [f for f in zf.namelist() if f.endswith(".xml")]
                if not xml_files:
                    print("No XML file found in ZIP")
                    return None

                # Extract to temp location
                xml_filename = xml_files[0]
                tmp_xml_path = tempfile.mktemp(suffix=".xml")
                with zf.open(xml_filename) as src, open(tmp_xml_path, "wb") as dst:
                    dst.write(src.read())

                print(f"Extracted: {xml_filename}")
                return tmp_xml_path

        except zipfile.BadZipFile:
            print("Downloaded file is not a valid ZIP")
            return None
        finally:
            # Cleanup ZIP
            if os.path.exists(tmp_zip_path):
                os.remove(tmp_zip_path)

    def _parse_xml(self, xml_path: str) -> Iterator[dict]:
        """Parse Grants.gov XML and yield opportunity dictionaries."""
        print(f"Parsing XML: {xml_path}")

        tree = ET.parse(xml_path)
        root = tree.getroot()

        opportunities = root.findall(".//ns:OpportunitySynopsisDetail_1_0", self.NAMESPACE)
        print(f"Found {len(opportunities)} grant opportunities")

        for grant in opportunities:
            try:
                yield self._parse_opportunity(grant)
            except Exception as e:
                opp_id = self._get_text(grant, "ns:OpportunityID")
                print(f"Error parsing grant {opp_id}: {e}")
                continue

    def _parse_opportunity(self, grant: ET.Element) -> dict:
        """Parse a single opportunity element."""
        opportunity_id = self._get_text(grant, "ns:OpportunityID")

        # Build grant URL
        url_elem = grant.find("ns:AdditionalInformationURL", self.NAMESPACE)
        url = (
            url_elem.text.strip() if url_elem is not None and url_elem.text
            else f"https://www.grants.gov/web/grants/view-opportunity.html?oppId={opportunity_id}"
        )

        # Parse funding amount
        funding_elem = grant.find("ns:EstimatedTotalProgramFunding", self.NAMESPACE)
        funding_amount = None
        if funding_elem is not None and funding_elem.text:
            try:
                funding_amount = int(funding_elem.text.replace(",", "").split(".")[0])
            except ValueError:
                funding_amount = None

        # Parse CFDA numbers
        cfda_elems = grant.findall("ns:CFDANumber", self.NAMESPACE)
        cfda_numbers = [
            cfda.text.strip()
            for cfda in cfda_elems
            if cfda.text and cfda.text.strip()
        ] or None

        return {
            "opportunity_id": opportunity_id,
            "title": self._get_text(grant, "ns:OpportunityTitle"),
            "description": self._get_text(grant, "ns:Description"),
            "agency": self._get_text(grant, "ns:AgencyName"),
            "deadline": self._get_text(grant, "ns:CloseDate"),  # MMDDYYYY format
            "funding_amount": funding_amount,
            "cfda_numbers": cfda_numbers,
            "naics_code": None,  # Grants don't have NAICS codes
            "url": url,
        }

    def _get_text(self, elem: ET.Element, tag: str) -> str | None:
        """Safely extract text from an XML element."""
        child = elem.find(tag, self.NAMESPACE)
        if child is not None and child.text:
            return child.text.strip()
        return None
