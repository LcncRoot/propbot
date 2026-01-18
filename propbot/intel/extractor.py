"""PDF and document text extraction for opportunity analysis."""

from pathlib import Path
from typing import Optional
from datetime import datetime

import pdfplumber

from ..database.connection import get_connection


class PDFExtractor:
    """Extracts text from PDF and HTML documents."""

    def __init__(self):
        """Initialize the PDF extractor."""
        pass

    def extract_pdf(self, file_path: Path) -> dict:
        """
        Extract text from a PDF file.

        Args:
            file_path: Path to the PDF file.

        Returns:
            Dictionary with 'text', 'page_count', 'method' keys.
        """
        text_parts = []
        page_count = 0

        try:
            with pdfplumber.open(file_path) as pdf:
                page_count = len(pdf.pages)

                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)

            full_text = "\n\n".join(text_parts)

            return {
                "text": full_text,
                "page_count": page_count,
                "method": "pdfplumber"
            }

        except Exception as e:
            print(f"Error extracting PDF {file_path}: {e}")
            return {
                "text": "",
                "page_count": 0,
                "method": "failed"
            }

    def extract_html(self, file_path: Path) -> dict:
        """
        Extract text from an HTML file.

        Args:
            file_path: Path to the HTML file.

        Returns:
            Dictionary with 'text', 'page_count', 'method' keys.
        """
        try:
            from bs4 import BeautifulSoup

            content = file_path.read_text(encoding="utf-8", errors="ignore")
            soup = BeautifulSoup(content, "html.parser")

            # Remove script and style elements
            for element in soup(["script", "style"]):
                element.decompose()

            text = soup.get_text(separator="\n", strip=True)

            return {
                "text": text,
                "page_count": 1,
                "method": "html"
            }

        except Exception as e:
            print(f"Error extracting HTML {file_path}: {e}")
            return {
                "text": "",
                "page_count": 0,
                "method": "failed"
            }

    def extract_document(self, file_path: Path) -> dict:
        """
        Extract text from a document, auto-detecting type.

        Args:
            file_path: Path to the document.

        Returns:
            Dictionary with 'text', 'page_count', 'method' keys.
        """
        file_path = Path(file_path)
        suffix = file_path.suffix.lower()

        if suffix == ".pdf":
            return self.extract_pdf(file_path)
        elif suffix in [".html", ".htm"]:
            return self.extract_html(file_path)
        else:
            # Try to read as text
            try:
                text = file_path.read_text(encoding="utf-8", errors="ignore")
                return {
                    "text": text,
                    "page_count": 1,
                    "method": "text"
                }
            except Exception:
                return {
                    "text": "",
                    "page_count": 0,
                    "method": "unsupported"
                }

    def extract_and_store(self, opportunity_id: str) -> list[dict]:
        """
        Extract text from all documents for an opportunity and update database.

        Args:
            opportunity_id: The opportunity ID.

        Returns:
            List of updated document records.
        """
        conn = get_connection()
        updated_docs = []

        try:
            # Get all documents for this opportunity
            cursor = conn.execute(
                "SELECT * FROM opportunity_documents WHERE opportunity_id = ?",
                (opportunity_id,)
            )
            documents = [dict(row) for row in cursor.fetchall()]

            for doc in documents:
                file_path = Path(doc["file_path"])

                if not file_path.exists():
                    print(f"File not found: {file_path}")
                    continue

                # Skip if already extracted
                if doc.get("extracted_text"):
                    updated_docs.append(doc)
                    continue

                # Extract text
                result = self.extract_document(file_path)

                if result["text"]:
                    # Update database
                    conn.execute("""
                        UPDATE opportunity_documents
                        SET extracted_text = ?, page_count = ?, extraction_method = ?, extracted_at = ?
                        WHERE id = ?
                    """, (
                        result["text"],
                        result["page_count"],
                        result["method"],
                        datetime.now().isoformat(),
                        doc["id"]
                    ))

                    doc["extracted_text"] = result["text"]
                    doc["page_count"] = result["page_count"]
                    doc["extraction_method"] = result["method"]

                updated_docs.append(doc)

            conn.commit()

        except Exception as e:
            print(f"Error in extract_and_store: {e}")
            raise
        finally:
            conn.close()

        return updated_docs

    def get_combined_text(self, opportunity_id: str) -> str:
        """
        Get combined extracted text from all documents for an opportunity.

        Args:
            opportunity_id: The opportunity ID.

        Returns:
            Combined text from all documents.
        """
        conn = get_connection()
        try:
            cursor = conn.execute(
                "SELECT filename, document_type, extracted_text FROM opportunity_documents WHERE opportunity_id = ? AND extracted_text IS NOT NULL",
                (opportunity_id,)
            )

            parts = []
            for row in cursor.fetchall():
                doc = dict(row)
                header = f"=== {doc['filename']} ({doc['document_type']}) ==="
                parts.append(f"{header}\n{doc['extracted_text']}")

            return "\n\n".join(parts)

        finally:
            conn.close()
