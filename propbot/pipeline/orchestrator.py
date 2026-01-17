"""Pipeline orchestrator for PropBot.

Coordinates the full ingest pipeline:
1. Initialize database
2. Fetch opportunities from sources
3. Normalize dates
4. Filter by freshness (expired deadlines only)
5. Store ALL non-expired opportunities to database
6. Track ingest run statistics

Note: Capability filtering has been removed from ingest.
All non-expired opportunities are stored; relevance filtering
happens at query time via semantic search (FAISS).
"""

from typing import Optional

from ..database.connection import get_connection, init_db
from ..database.migrations import run_migrations
from ..sources.base import BaseSource
from ..sources.grants import GrantsGovSource
from ..sources.sam import SamGovSource
from .filters import filter_freshness_only
from .storage import OpportunityStorage, IngestRunTracker


def run_pipeline(
    sources: Optional[list[str]] = None,
    skip_grants: bool = False,
    skip_sam: bool = False,
) -> dict:
    """
    Run the full ingest pipeline.

    Args:
        sources: List of source names to run ('grants.gov', 'sam.gov').
                If None, runs all sources unless skip flags are set.
        skip_grants: Skip Grants.gov source.
        skip_sam: Skip SAM.gov source.

    Returns:
        Dictionary with summary statistics for each source.
    """
    # Initialize database
    print("Initializing database...")
    conn = get_connection()
    run_migrations(conn)
    conn.commit()

    # Determine which sources to run
    sources_to_run: list[BaseSource] = []

    if sources:
        # Use specified sources
        for source_name in sources:
            if source_name == "grants.gov":
                sources_to_run.append(GrantsGovSource())
            elif source_name == "sam.gov":
                sources_to_run.append(SamGovSource())
            else:
                print(f"Unknown source: {source_name}")
    else:
        # Use all sources unless skipped
        if not skip_grants:
            sources_to_run.append(GrantsGovSource())
        if not skip_sam:
            sources_to_run.append(SamGovSource())

    if not sources_to_run:
        print("No sources to run!")
        return {}

    # Run each source
    results = {}
    for source in sources_to_run:
        print(f"\n{'='*60}")
        print(f"Processing source: {source.get_source_name()}")
        print(f"{'='*60}")

        result = _process_source(conn, source)
        results[source.get_source_name()] = result

    conn.close()

    # Print summary
    print(f"\n{'='*60}")
    print("PIPELINE SUMMARY")
    print(f"{'='*60}")
    for source_name, stats in results.items():
        print(f"\n{source_name}:")
        print(f"  Fetched: {stats['records_fetched']}")
        print(f"  Filtered (expired): {stats['records_filtered_expired']}")
        print(f"  Inserted: {stats['records_inserted']}")
        print(f"  Updated: {stats['records_updated']}")

    return results


def _process_source(conn, source: BaseSource) -> dict:
    """
    Process a single data source through the pipeline.

    Applies only freshness filtering (removes expired opportunities).
    All non-expired opportunities are stored for semantic search.

    Args:
        conn: Database connection.
        source: Data source to process.

    Returns:
        Dictionary with ingest run statistics.
    """
    source_name = source.get_source_name()

    # Initialize tracker and storage
    tracker = IngestRunTracker(conn, source_name)
    storage = OpportunityStorage(conn)

    try:
        # Fetch and process opportunities
        for record in source.fetch():
            tracker.increment_fetched()

            # Apply freshness filter only (no capability filtering)
            filtered_record, filter_reason = filter_freshness_only(
                record, source_name
            )

            if filtered_record is None:
                if filter_reason == "expired":
                    tracker.increment_filtered_expired()
                continue

            # Store to database
            is_new = storage.upsert_opportunity(filtered_record, source_name)
            if is_new:
                tracker.increment_inserted()
            else:
                tracker.increment_updated()

            # Commit periodically
            if (tracker.records_fetched % 100) == 0:
                conn.commit()

        # Final commit
        conn.commit()
        tracker.complete()

    except Exception as e:
        error_msg = str(e)
        print(f"Error processing {source_name}: {error_msg}")
        tracker.complete(error_message=error_msg)
        raise

    return tracker.get_summary()


def run_single_source(source_name: str) -> dict:
    """
    Run pipeline for a single source.

    Args:
        source_name: Name of source to run ('grants.gov' or 'sam.gov').

    Returns:
        Dictionary with ingest run statistics.
    """
    return run_pipeline(sources=[source_name])
