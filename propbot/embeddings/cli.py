"""CLI for embedding generation."""

import argparse
import sys

from ..config import config


def main():
    parser = argparse.ArgumentParser(description="PropBot embedding generator")
    parser.add_argument(
        "command",
        choices=["generate", "status"],
        help="Command to run: generate creates the FAISS index, status shows index info"
    )
    args = parser.parse_args()

    if not config.OPENAI_API_KEY:
        print("Error: OPENAI_API_KEY not configured in .env")
        sys.exit(1)

    if args.command == "generate":
        from .generator import EmbeddingGenerator
        
        print("Generating FAISS index...")
        generator = EmbeddingGenerator()
        stats = generator.generate_index()
        
        print(f"\nDone! Indexed {stats['embedded']} opportunities.")
        print(f"Index: {stats.get('index_path')}")
        print(f"ID map: {stats.get('id_map_path')}")

    elif args.command == "status":
        from .search import SemanticSearch
        
        search = SemanticSearch()
        if search.is_index_available():
            _ = search.index  # Load it
            _ = search.id_map
            print(f"FAISS index: {search.index_path}")
            print(f"  Vectors: {search.index.ntotal}")
            print(f"  Dimension: {search.dimension}")
            print(f"ID map: {search.id_map_path}")
            print(f"  Entries: {len(search.id_map)}")
        else:
            print("No FAISS index found.")
            print("Run 'python -m propbot.embeddings.cli generate' to create one.")


if __name__ == "__main__":
    main()
