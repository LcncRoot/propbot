#!/usr/bin/env python3
"""
CLI entry point for PropBot pipeline.

Usage:
    python -m propbot.pipeline.run [options]

Options:
    --source SOURCE     Run only specified source (grants.gov or sam.gov)
    --skip-grants       Skip Grants.gov source
    --skip-sam          Skip SAM.gov source
    --init-only         Only initialize database, don't run pipeline
    --help              Show this help message
"""

import argparse
import sys

from ..config import config
from ..database.connection import init_db
from ..database.migrations import seed_capability_filters
from .orchestrator import run_pipeline


def main():
    """Main entry point for pipeline CLI."""
    parser = argparse.ArgumentParser(
        description="PropBot data ingestion pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Run full pipeline (both sources)
    python -m propbot.pipeline.run

    # Run only SAM.gov source
    python -m propbot.pipeline.run --source sam.gov

    # Run only Grants.gov source
    python -m propbot.pipeline.run --source grants.gov

    # Initialize database without running pipeline
    python -m propbot.pipeline.run --init-only
        """
    )

    parser.add_argument(
        "--source",
        choices=["grants.gov", "sam.gov"],
        help="Run only specified source"
    )
    parser.add_argument(
        "--skip-grants",
        action="store_true",
        help="Skip Grants.gov source"
    )
    parser.add_argument(
        "--skip-sam",
        action="store_true",
        help="Skip SAM.gov source"
    )
    parser.add_argument(
        "--init-only",
        action="store_true",
        help="Only initialize database, don't run pipeline"
    )

    args = parser.parse_args()

    # Validate configuration
    print("Validating configuration...")
    errors = config.validate()
    if errors:
        print("Configuration errors:")
        for error in errors:
            print(f"  - {error}")

        if not args.init_only:
            print("\nFix configuration errors before running pipeline.")
            sys.exit(1)

    print(f"Database path: {config.DATABASE_PATH}")

    if args.init_only:
        print("\nInitializing database only...")
        init_db()
        # Also seed capability filters
        from ..database.connection import get_connection
        conn = get_connection()
        seed_capability_filters(conn)
        conn.close()
        print("Database initialized successfully!")
        return

    # Determine sources
    sources = None
    if args.source:
        sources = [args.source]

    # Run pipeline
    print("\nStarting pipeline...")
    try:
        results = run_pipeline(
            sources=sources,
            skip_grants=args.skip_grants,
            skip_sam=args.skip_sam,
        )

        # Report total records in database
        from ..database.connection import get_connection
        conn = get_connection()
        cursor = conn.execute("SELECT COUNT(*) FROM opportunities")
        total_records = cursor.fetchone()[0]
        conn.close()

        print(f"\nTotal records in database: {total_records}")
        print("\nPipeline completed successfully!")

    except KeyboardInterrupt:
        print("\nPipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nPipeline failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
