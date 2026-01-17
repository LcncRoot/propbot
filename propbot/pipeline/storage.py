"""Storage utilities for PropBot pipeline.

Handles writing opportunities to SQLite database.
"""

import json
import sqlite3
from datetime import datetime
from typing import Optional

from .normalizer import normalize_deadline


class OpportunityStorage:
    """Handles storing opportunities in SQLite."""

    def __init__(self, conn: sqlite3.Connection):
        """
        Initialize storage with database connection.

        Args:
            conn: SQLite database connection.
        """
        self.conn = conn
        self.inserted = 0
        self.updated = 0

    def upsert_opportunity(self, record: dict, source: str) -> bool:
        """
        Insert or update an opportunity record.

        Args:
            record: Opportunity record to store.
            source: Source name ('grants.gov' or 'sam.gov').

        Returns:
            True if inserted, False if updated existing.
        """
        opportunity_id = record.get("opportunity_id")
        if not opportunity_id:
            return False

        # Normalize deadline
        deadline = normalize_deadline(record.get("deadline"), source)

        # Serialize CFDA numbers to JSON if present
        cfda_numbers = record.get("cfda_numbers")
        if cfda_numbers and isinstance(cfda_numbers, list):
            cfda_numbers = json.dumps(cfda_numbers)

        # Check if record exists
        cursor = self.conn.execute(
            "SELECT id FROM opportunities WHERE opportunity_id = ?",
            (opportunity_id,)
        )
        existing = cursor.fetchone()

        if existing:
            # Update existing record
            self.conn.execute(
                """
                UPDATE opportunities SET
                    title = ?,
                    description = ?,
                    agency = ?,
                    deadline = ?,
                    funding_amount = ?,
                    naics_code = ?,
                    cfda_numbers = ?,
                    url = ?,
                    notice_type = ?,
                    matched_keywords = ?,
                    matched_naics = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE opportunity_id = ?
                """,
                (
                    record.get("title"),
                    record.get("description"),
                    record.get("agency"),
                    deadline,
                    record.get("funding_amount"),
                    record.get("naics_code"),
                    cfda_numbers,
                    record.get("url"),
                    record.get("notice_type"),
                    record.get("matched_keywords"),
                    record.get("matched_naics"),
                    opportunity_id,
                )
            )
            self.updated += 1
            return False
        else:
            # Insert new record
            self.conn.execute(
                """
                INSERT INTO opportunities (
                    opportunity_id, source, title, description, agency,
                    deadline, funding_amount, naics_code, cfda_numbers,
                    url, notice_type, matched_keywords, matched_naics
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    opportunity_id,
                    source,
                    record.get("title"),
                    record.get("description"),
                    record.get("agency"),
                    deadline,
                    record.get("funding_amount"),
                    record.get("naics_code"),
                    cfda_numbers,
                    record.get("url"),
                    record.get("notice_type"),
                    record.get("matched_keywords"),
                    record.get("matched_naics"),
                )
            )
            self.inserted += 1
            return True

    def get_stats(self) -> dict:
        """Get storage statistics."""
        return {
            "inserted": self.inserted,
            "updated": self.updated,
        }


class IngestRunTracker:
    """Tracks ingest run statistics."""

    def __init__(self, conn: sqlite3.Connection, source: str):
        """
        Initialize tracker and create ingest run record.

        Args:
            conn: SQLite database connection.
            source: Source name being ingested.
        """
        self.conn = conn
        self.source = source

        # Create ingest run record
        cursor = self.conn.execute(
            "INSERT INTO ingest_runs (source) VALUES (?)",
            (source,)
        )
        self.run_id = cursor.lastrowid
        self.conn.commit()

        # Initialize counters
        self.records_fetched = 0
        self.records_filtered_expired = 0
        self.records_filtered_capability = 0
        self.records_inserted = 0
        self.records_updated = 0

    def increment_fetched(self, count: int = 1) -> None:
        self.records_fetched += count

    def increment_filtered_expired(self, count: int = 1) -> None:
        self.records_filtered_expired += count

    def increment_filtered_capability(self, count: int = 1) -> None:
        self.records_filtered_capability += count

    def increment_inserted(self, count: int = 1) -> None:
        self.records_inserted += count

    def increment_updated(self, count: int = 1) -> None:
        self.records_updated += count

    def complete(self, error_message: Optional[str] = None) -> None:
        """Mark the ingest run as completed."""
        status = "failed" if error_message else "completed"

        self.conn.execute(
            """
            UPDATE ingest_runs SET
                completed_at = CURRENT_TIMESTAMP,
                status = ?,
                records_fetched = ?,
                records_filtered_expired = ?,
                records_filtered_capability = ?,
                records_inserted = ?,
                records_updated = ?,
                error_message = ?
            WHERE id = ?
            """,
            (
                status,
                self.records_fetched,
                self.records_filtered_expired,
                self.records_filtered_capability,
                self.records_inserted,
                self.records_updated,
                error_message,
                self.run_id,
            )
        )
        self.conn.commit()

    def get_summary(self) -> dict:
        """Get summary of the ingest run."""
        return {
            "run_id": self.run_id,
            "source": self.source,
            "records_fetched": self.records_fetched,
            "records_filtered_expired": self.records_filtered_expired,
            "records_filtered_capability": self.records_filtered_capability,
            "records_inserted": self.records_inserted,
            "records_updated": self.records_updated,
        }
