"""Document fetcher for downloading opportunity attachments from SAM.gov."""

import re
import time
from pathlib import Path
from typing import Optional
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from ..config import config, PROJECT_ROOT
from ..database.connection import get_connection


class DocumentFetcher:
    """Fetches and stores documents attached to opportunities."""

    # SAM.gov opportunity detail URL pattern
    SAM_OPPORTUNITY_URL = "https://sam.gov/opp/{notice_id}/view"
    SAM_API_RESOURCES_URL = "https://api.sam.gov/opportunities/v2/search"

    def __init__(self, storage_dir: Optional[Path] = None):
        """
        Initialize the document fetcher.

        Args:
            storage_dir: Directory to store downloaded documents.
                        Defaults to propbot/data/documents/
        """
        self.storage_dir = storage_dir or (PROJECT_ROOT / "propbot" / "data" / "documents")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "PropBot/1.0 (Government Opportunity Analyzer)"
        })

    def fetch_opportunity_resources(self, opportunity_id: str) -> list[dict]:
        """
        Fetch resource links (attachments) for a SAM.gov opportunity.

        Uses the SAM.gov API to get attachment URLs.

        Args:
            opportunity_id: The SAM.gov notice ID.

        Returns:
            List of resource dictionaries with 'name', 'url', 'type' keys.
        """
        resources = []

        # Try the SAM.gov API first
        try:
            api_url = f"https://api.sam.gov/opportunities/v2/search"
            params = {
                "api_key": config.SAM_API_KEY,
                "noticeid": opportunity_id,
                "limit": 1
            }

            response = self.session.get(api_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            opportunities = data.get("opportunitiesData", [])
            if opportunities:
                opp = opportunities[0]

                # Get resource links
                resource_links = opp.get("resourceLinks", [])
                for link in resource_links:
                    resources.append({
                        "name": link.get("name", "attachment"),
                        "url": link,
                        "type": self._guess_doc_type(link.get("name", ""))
                    })

                # Also check for description URL (sometimes contains the full SOW)
                desc = opp.get("description", "")
                if desc and desc.startswith("https://"):
                    resources.append({
                        "name": "description.html",
                        "url": desc,
                        "type": "description"
                    })

        except Exception as e:
            print(f"Error fetching resources from API: {e}")

        return resources

    def fetch_sam_attachments(self, opportunity_id: str) -> list[dict]:
        """
        Fetch attachment metadata for a SAM.gov opportunity using the public API.

        Args:
            opportunity_id: The SAM.gov notice ID.

        Returns:
            List of attachment info dicts.
        """
        attachments = []

        try:
            # Use the opportunities API with the specific notice ID
            url = "https://api.sam.gov/opportunities/v2/search"
            params = {
                "api_key": config.SAM_API_KEY,
                "noticeid": opportunity_id,
                "limit": 1
            }

            response = self.session.get(url, params=params, timeout=30)
            time.sleep(1.5)  # Rate limiting

            if response.status_code == 200:
                data = response.json()
                opps = data.get("opportunitiesData", [])

                if opps:
                    opp = opps[0]

                    # Check resourceLinks field
                    for idx, link in enumerate(opp.get("resourceLinks", [])):
                        if isinstance(link, str):
                            attachments.append({
                                "name": f"attachment_{idx}.pdf",
                                "url": link,
                                "type": self._guess_doc_type(link)
                            })
                        elif isinstance(link, dict):
                            attachments.append({
                                "name": link.get("name", f"attachment_{idx}"),
                                "url": link.get("url", ""),
                                "type": self._guess_doc_type(link.get("name", ""))
                            })

                    # Check for description URL
                    desc_url = opp.get("description", "")
                    if desc_url and isinstance(desc_url, str) and desc_url.startswith("https://api.sam.gov"):
                        attachments.append({
                            "name": "description.html",
                            "url": desc_url,
                            "type": "description"
                        })

        except Exception as e:
            print(f"Error fetching SAM attachments: {e}")

        return attachments

    def download_document(self, url: str, opportunity_id: str, filename: str) -> Optional[Path]:
        """
        Download a document and save it locally.

        Args:
            url: URL to download from.
            opportunity_id: Associated opportunity ID.
            filename: Name to save the file as.

        Returns:
            Path to saved file, or None if download failed.
        """
        try:
            # Create opportunity-specific directory
            opp_dir = self.storage_dir / opportunity_id
            opp_dir.mkdir(parents=True, exist_ok=True)

            # Add API key if it's a SAM.gov API URL
            download_url = url
            if "api.sam.gov" in url and "api_key" not in url:
                separator = "&" if "?" in url else "?"
                download_url = f"{url}{separator}api_key={config.SAM_API_KEY}"

            # Download
            response = self.session.get(download_url, timeout=60)
            response.raise_for_status()

            # Determine filename and extension
            content_type = response.headers.get("Content-Type", "")
            if not filename or filename == "attachment":
                if "pdf" in content_type:
                    filename = "document.pdf"
                elif "html" in content_type:
                    filename = "document.html"
                else:
                    filename = "document.bin"

            # Save file
            file_path = opp_dir / filename
            file_path.write_bytes(response.content)

            return file_path

        except Exception as e:
            print(f"Error downloading document from {url}: {e}")
            return None

    def fetch_and_store_documents(self, opportunity_id: str) -> list[dict]:
        """
        Fetch all documents for an opportunity and store them in the database.

        Args:
            opportunity_id: The opportunity ID to fetch documents for.

        Returns:
            List of document records that were stored.
        """
        conn = get_connection()
        stored_docs = []

        try:
            # Get attachments
            attachments = self.fetch_sam_attachments(opportunity_id)

            for att in attachments:
                # Download the document
                file_path = self.download_document(
                    url=att["url"],
                    opportunity_id=opportunity_id,
                    filename=att["name"]
                )

                if file_path and file_path.exists():
                    # Store in database
                    doc_record = {
                        "opportunity_id": opportunity_id,
                        "document_type": att["type"],
                        "filename": att["name"],
                        "source_url": att["url"],
                        "file_path": str(file_path),
                        "file_size_bytes": file_path.stat().st_size
                    }

                    conn.execute("""
                        INSERT OR REPLACE INTO opportunity_documents
                        (opportunity_id, document_type, filename, source_url, file_path, file_size_bytes, fetched_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        doc_record["opportunity_id"],
                        doc_record["document_type"],
                        doc_record["filename"],
                        doc_record["source_url"],
                        doc_record["file_path"],
                        doc_record["file_size_bytes"],
                        datetime.now().isoformat()
                    ))

                    stored_docs.append(doc_record)

            conn.commit()

        except Exception as e:
            print(f"Error in fetch_and_store_documents: {e}")
            raise
        finally:
            conn.close()

        return stored_docs

    def _guess_doc_type(self, filename: str) -> str:
        """Guess document type from filename."""
        filename_lower = filename.lower()

        if any(x in filename_lower for x in ["sow", "statement of work"]):
            return "sow"
        elif any(x in filename_lower for x in ["pws", "performance work"]):
            return "pws"
        elif any(x in filename_lower for x in ["rfi", "request for info"]):
            return "rfi"
        elif any(x in filename_lower for x in ["amendment", "mod"]):
            return "amendment"
        elif any(x in filename_lower for x in ["qa", "q&a", "question"]):
            return "qa"
        elif ".pdf" in filename_lower:
            return "attachment"
        else:
            return "other"

    def get_stored_documents(self, opportunity_id: str) -> list[dict]:
        """
        Get all stored documents for an opportunity.

        Args:
            opportunity_id: The opportunity ID.

        Returns:
            List of document records from database.
        """
        conn = get_connection()
        try:
            cursor = conn.execute(
                "SELECT * FROM opportunity_documents WHERE opportunity_id = ?",
                (opportunity_id,)
            )
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
