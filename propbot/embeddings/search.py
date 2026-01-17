"""Semantic search using FAISS for PropBot.

Provides semantic search over opportunities using pre-computed embeddings.
"""

import json
import sqlite3
from pathlib import Path
from typing import Optional

import faiss
import numpy as np
from openai import OpenAI

from ..config import config


class SemanticSearch:
    """Semantic search over opportunities using FAISS."""

    def __init__(self):
        """Initialize semantic search."""
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.model = "text-embedding-3-small"
        self.dimension = 1536
        
        # Paths for index and ID mapping
        self.data_dir = Path(config.DATABASE_PATH).parent
        self.index_path = self.data_dir / "faiss_index.bin"
        self.id_map_path = self.data_dir / "faiss_id_map.json"
        
        # Lazy-loaded index and ID map
        self._index: Optional[faiss.Index] = None
        self._id_map: Optional[list[dict]] = None

    @property
    def index(self) -> faiss.Index:
        """Lazy-load FAISS index."""
        if self._index is None:
            if not self.index_path.exists():
                raise FileNotFoundError(
                    f"FAISS index not found at {self.index_path}. "
                    "Run 'python -m propbot.embeddings.cli generate' first."
                )
            self._index = faiss.read_index(str(self.index_path))
        return self._index

    @property
    def id_map(self) -> list[dict]:
        """Lazy-load ID mapping."""
        if self._id_map is None:
            if not self.id_map_path.exists():
                raise FileNotFoundError(
                    f"ID map not found at {self.id_map_path}. "
                    "Run 'python -m propbot.embeddings.cli generate' first."
                )
            with open(self.id_map_path) as f:
                self._id_map = json.load(f)
        return self._id_map

    def reload_index(self) -> None:
        """Force reload of FAISS index and ID map."""
        self._index = None
        self._id_map = None
        # Trigger lazy load
        _ = self.index
        _ = self.id_map

    def _embed_query(self, query: str) -> np.ndarray:
        """
        Embed a search query.

        Args:
            query: Search query text.

        Returns:
            Embedding vector (1 x dimension).
        """
        response = self.client.embeddings.create(
            input=[query],
            model=self.model
        )
        embedding = np.array([response.data[0].embedding], dtype="float32")
        # Normalize for cosine similarity
        faiss.normalize_L2(embedding)
        return embedding

    def search(
        self,
        query: str,
        k: int = 20,
        source_filter: Optional[str] = None,
        min_score: float = 0.0
    ) -> list[dict]:
        """
        Search for opportunities semantically similar to query.

        Args:
            query: Search query text.
            k: Maximum number of results to return.
            source_filter: Optional filter by source ('grants.gov' or 'sam.gov').
            min_score: Minimum similarity score (0-1).

        Returns:
            List of dicts with 'db_id', 'opportunity_id', 'source', 'score'.
        """
        # Embed the query
        query_embedding = self._embed_query(query)

        # Search FAISS index (get more results if filtering)
        search_k = k * 3 if source_filter else k
        scores, indices = self.index.search(query_embedding, search_k)

        # Build results
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:  # FAISS returns -1 for empty slots
                continue
            if score < min_score:
                continue

            entry = self.id_map[idx]
            
            # Apply source filter
            if source_filter and entry["source"] != source_filter:
                continue

            results.append({
                "db_id": entry["db_id"],
                "opportunity_id": entry["opportunity_id"],
                "source": entry["source"],
                "score": float(score)
            })

            if len(results) >= k:
                break

        return results

    def search_with_details(
        self,
        query: str,
        conn: sqlite3.Connection,
        k: int = 20,
        source_filter: Optional[str] = None,
        min_score: float = 0.0
    ) -> list[dict]:
        """
        Search and return full opportunity details.

        Args:
            query: Search query text.
            conn: Database connection.
            k: Maximum number of results.
            source_filter: Optional filter by source.
            min_score: Minimum similarity score.

        Returns:
            List of opportunity dicts with all fields + similarity score.
        """
        # Get matching IDs
        matches = self.search(query, k, source_filter, min_score)
        
        if not matches:
            return []

        # Fetch full details from database
        db_ids = [m["db_id"] for m in matches]
        scores_by_id = {m["db_id"]: m["score"] for m in matches}

        placeholders = ",".join("?" * len(db_ids))
        cursor = conn.execute(
            f"""
            SELECT id, opportunity_id, source, title, description, agency,
                   deadline, funding_amount, naics_code, cfda_numbers, url
            FROM opportunities
            WHERE id IN ({placeholders})
            """,
            db_ids
        )

        results = []
        for row in cursor.fetchall():
            result = {
                "id": row[0],
                "opportunity_id": row[1],
                "source": row[2],
                "title": row[3],
                "description": row[4],
                "agency": row[5],
                "deadline": row[6],
                "funding_amount": row[7],
                "naics_code": row[8],
                "cfda_numbers": row[9],
                "url": row[10],
                "similarity_score": scores_by_id[row[0]]
            }
            results.append(result)

        # Sort by similarity score (descending)
        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        return results

    def is_index_available(self) -> bool:
        """Check if FAISS index exists and is loadable."""
        return self.index_path.exists() and self.id_map_path.exists()
