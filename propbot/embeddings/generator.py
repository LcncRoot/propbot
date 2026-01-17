"""Embedding generator for PropBot opportunities.

Generates OpenAI embeddings for opportunities and stores them in a FAISS index.
"""

import json
import os
import sqlite3
from pathlib import Path
from typing import Optional

import faiss
import numpy as np
from openai import OpenAI

from ..config import config


class EmbeddingGenerator:
    """Generates and stores embeddings for opportunities."""

    def __init__(self, batch_size: int = 100):
        """
        Initialize the embedding generator.

        Args:
            batch_size: Number of texts to embed in each API call.
        """
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.model = "text-embedding-3-small"
        self.dimension = 1536  # text-embedding-3-small dimension
        self.batch_size = batch_size
        
        # Paths for index and ID mapping
        self.data_dir = Path(config.DATABASE_PATH).parent
        self.index_path = self.data_dir / "faiss_index.bin"
        self.id_map_path = self.data_dir / "faiss_id_map.json"

    def _get_embedding(self, texts: list[str]) -> np.ndarray:
        """
        Get embeddings for a batch of texts.

        Args:
            texts: List of texts to embed.

        Returns:
            numpy array of embeddings (N x dimension).
        """
        response = self.client.embeddings.create(
            input=texts,
            model=self.model
        )
        embeddings = [item.embedding for item in response.data]
        return np.array(embeddings, dtype="float32")

    def _build_searchable_text(self, title: str, description: str) -> str:
        """
        Build searchable text from title and description.

        Args:
            title: Opportunity title.
            description: Opportunity description.

        Returns:
            Combined text for embedding.
        """
        title = title or ""
        description = description or ""
        # Limit description to avoid token limits
        if len(description) > 2000:
            description = description[:2000] + "..."
        return f"{title}\n{description}".strip()

    def generate_index(self, conn: Optional[sqlite3.Connection] = None) -> dict:
        """
        Generate FAISS index from all opportunities in database.

        Args:
            conn: Optional database connection (creates new if not provided).

        Returns:
            Statistics about the generation process.
        """
        from ..database.connection import get_connection

        if conn is None:
            conn = get_connection()
            should_close = True
        else:
            should_close = False

        try:
            # Fetch all opportunities
            cursor = conn.execute("""
                SELECT id, opportunity_id, title, description, source
                FROM opportunities
                ORDER BY id
            """)
            opportunities = cursor.fetchall()

            if not opportunities:
                print("No opportunities found in database.")
                return {"total": 0, "embedded": 0}

            print(f"Found {len(opportunities)} opportunities to embed")

            # Prepare data
            texts = []
            id_map = []  # Maps FAISS index position to (db_id, opportunity_id)

            for db_id, opp_id, title, description, source in opportunities:
                text = self._build_searchable_text(title, description)
                texts.append(text)
                id_map.append({
                    "db_id": db_id,
                    "opportunity_id": opp_id,
                    "source": source
                })

            # Generate embeddings in batches
            all_embeddings = []
            total_batches = (len(texts) + self.batch_size - 1) // self.batch_size

            for i in range(0, len(texts), self.batch_size):
                batch_num = i // self.batch_size + 1
                batch = texts[i:i + self.batch_size]
                print(f"Embedding batch {batch_num}/{total_batches} ({len(batch)} texts)")
                
                embeddings = self._get_embedding(batch)
                all_embeddings.append(embeddings)

            # Combine all embeddings
            all_embeddings = np.vstack(all_embeddings)
            print(f"Generated {all_embeddings.shape[0]} embeddings")

            # Create FAISS index
            index = faiss.IndexFlatIP(self.dimension)  # Inner product (cosine sim for normalized vectors)
            
            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(all_embeddings)
            index.add(all_embeddings)

            # Save index and ID mapping
            faiss.write_index(index, str(self.index_path))
            with open(self.id_map_path, "w") as f:
                json.dump(id_map, f)

            print(f"Saved FAISS index to {self.index_path}")
            print(f"Saved ID map to {self.id_map_path}")

            return {
                "total": len(opportunities),
                "embedded": all_embeddings.shape[0],
                "index_path": str(self.index_path),
                "id_map_path": str(self.id_map_path)
            }

        finally:
            if should_close:
                conn.close()

    def update_index(self, new_opportunity_ids: list[int], conn: Optional[sqlite3.Connection] = None) -> dict:
        """
        Update existing FAISS index with new opportunities.

        For simplicity, this rebuilds the entire index.
        For production, consider incremental updates.

        Args:
            new_opportunity_ids: Database IDs of new opportunities.
            conn: Optional database connection.

        Returns:
            Statistics about the update.
        """
        # For now, just rebuild the entire index
        return self.generate_index(conn)
