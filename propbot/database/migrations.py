"""Database migrations and seeding for PropBot."""

import sqlite3
from pathlib import Path


def run_migrations(conn: sqlite3.Connection) -> None:
    """
    Run all database migrations (create tables, indexes).

    Args:
        conn: SQLite database connection.
    """
    schema_path = Path(__file__).parent / "schema.sql"

    with open(schema_path, "r") as f:
        schema_sql = f.read()

    conn.executescript(schema_sql)
    print("Database schema created/updated successfully.")


def seed_capability_filters(conn: sqlite3.Connection) -> None:
    """
    Seed the capability_filters table with default NAICS codes and keywords.

    Args:
        conn: SQLite database connection.
    """
    # NAICS codes relevant to IT infrastructure, cloud, DevOps
    naics_codes = [
        ("541512", "Computer Systems Design Services"),
        ("541511", "Custom Computer Programming Services"),
        ("541519", "Other Computer Related Services"),
        ("518210", "Data Processing, Hosting, and Related Services"),
        ("541513", "Computer Facilities Management Services"),
        ("541690", "Other Scientific and Technical Consulting Services"),
        ("517110", "Wired Telecommunications Carriers"),
        ("517210", "Wireless Telecommunications Carriers"),
        ("519190", "All Other Information Services"),
        ("541330", "Engineering Services"),
    ]

    # Keywords for capability matching
    keywords = [
        ("kubernetes", "Container orchestration platform"),
        ("openshift", "Red Hat container platform"),
        ("devops", "Development and operations practices"),
        ("docker", "Container technology"),
        ("container", "Containerization technology"),
        ("cloud infrastructure", "Cloud computing infrastructure"),
        ("platform automation", "Automated platform deployment"),
        ("aws", "Amazon Web Services"),
        ("azure", "Microsoft Azure cloud"),
        ("gcp", "Google Cloud Platform"),
        ("terraform", "Infrastructure as code tool"),
        ("ansible", "Configuration management and automation"),
        ("ci/cd", "Continuous integration and deployment"),
        ("cicd", "Continuous integration and deployment"),
        ("microservices", "Microservices architecture"),
        ("infrastructure as code", "IaC practices"),
        ("cloud native", "Cloud-native application development"),
        ("devsecops", "Security-integrated DevOps"),
        ("site reliability", "Site reliability engineering"),
        ("sre", "Site reliability engineering"),
        ("linux", "Linux operating system"),
        ("red hat", "Red Hat enterprise solutions"),
        ("vmware", "Virtualization platform"),
        ("networking", "Network infrastructure"),
        ("cybersecurity", "Information security"),
        ("zero trust", "Zero trust security architecture"),
    ]

    # Insert NAICS codes
    for code, description in naics_codes:
        conn.execute(
            """
            INSERT OR IGNORE INTO capability_filters (filter_type, value, description)
            VALUES ('naics', ?, ?)
            """,
            (code, description)
        )

    # Insert keywords
    for keyword, description in keywords:
        conn.execute(
            """
            INSERT OR IGNORE INTO capability_filters (filter_type, value, description)
            VALUES ('keyword', ?, ?)
            """,
            (keyword, description)
        )

    conn.commit()

    # Report counts
    cursor = conn.execute(
        "SELECT filter_type, COUNT(*) FROM capability_filters WHERE active = 1 GROUP BY filter_type"
    )
    counts = dict(cursor.fetchall())
    print(f"Capability filters seeded: {counts.get('naics', 0)} NAICS codes, {counts.get('keyword', 0)} keywords")


def load_capability_filters(conn: sqlite3.Connection) -> tuple[set[str], set[str]]:
    """
    Load active capability filters from the database.

    Args:
        conn: SQLite database connection.

    Returns:
        Tuple of (naics_codes set, keywords set).
    """
    cursor = conn.execute(
        "SELECT filter_type, value FROM capability_filters WHERE active = 1"
    )

    naics_codes: set[str] = set()
    keywords: set[str] = set()

    for row in cursor:
        if row["filter_type"] == "naics":
            naics_codes.add(row["value"])
        else:
            keywords.add(row["value"].lower())

    return naics_codes, keywords
