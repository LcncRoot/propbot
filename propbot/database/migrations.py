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


def seed_company_profile(conn: sqlite3.Connection) -> None:
    """
    Seed the company_profile table with Ariston LLC profile.

    Args:
        conn: SQLite database connection.
    """
    import json

    # Check if profile already exists
    cursor = conn.execute("SELECT id FROM company_profile WHERE company_name = 'Ariston LLC'")
    if cursor.fetchone():
        print("Company profile already exists, skipping seed.")
        return

    profile = {
        "company_name": "Ariston LLC",
        "owner_name": "Douglas Dan",
        "clearance_level": "secret",
        "capabilities": json.dumps([
            "cloud_infrastructure",
            "devops",
            "platform_engineering",
            "software_development",
            "ai_ml",
            "cybersecurity",
            "data_engineering",
            "mobile_development"
        ]),
        "technical_skills": json.dumps([
            "aws", "ec2", "s3", "rds", "lambda", "iam", "api_gateway",
            "kubernetes", "openshift", "docker", "helm",
            "terraform", "ansible",
            "python", "javascript", "nodejs", "rust", "cpp", "bash",
            "jenkins", "git", "cicd",
            "cloudwatch", "grafana",
            "linux", "unix",
            "ai_ml_pipelines", "generative_ai", "mlops",
            "disa", "nist", "fisma"
        ]),
        "naics_codes": json.dumps([
            "541512",  # Computer Systems Design Services
            "541511",  # Custom Computer Programming Services
            "541519",  # Other Computer Related Services
            "518210",  # Data Processing, Hosting, and Related Services
            "541715",  # R&D in Physical, Engineering, and Life Sciences
            "541330",  # Engineering Services
            "541690"   # Other Scientific and Technical Consulting
        ]),
        "past_performance": json.dumps([
            {
                "client": "ATF (via Leidos)",
                "description": "Managed AWS development sandbox environment, containerized deployments on Kubernetes/OpenShift",
                "role": "Software Engineer / DevOps Engineer"
            },
            {
                "client": "Intelligence Community (via Leidos)",
                "description": "Multi-node cloud-native data sharing solution using AWS S3, Kubernetes, OpenShift",
                "role": "DevOps Engineer"
            },
            {
                "client": "Classified (via Leidos)",
                "description": "AI/ML pipelines for text/image translation and analysis",
                "role": "Software Engineer"
            }
        ]),
        "contract_vehicles": json.dumps([]),  # None yet
        "certifications": json.dumps([
            "small_business",
            "aws_solutions_architect_associate"
        ]),
        "max_contract_value": None,  # TBD
        "location": "Washington, DC",
        "constraints": json.dumps({}),  # No hard constraints
        "summary": """Ariston LLC is a small business specializing in DevOps, cloud infrastructure,
and software engineering for federal government clients. Owner Douglas Dan holds a Secret clearance
and has 5+ years of experience supporting Intelligence Community and law enforcement agencies
through work at Leidos. Core competencies include AWS, Kubernetes, OpenShift, CI/CD automation,
AI/ML pipelines, and Python/JavaScript development. Ariston delivers secure, scalable solutions
for classified and sensitive environments."""
    }

    conn.execute(
        """
        INSERT INTO company_profile (
            company_name, owner_name, clearance_level, capabilities, technical_skills,
            naics_codes, past_performance, contract_vehicles, certifications,
            max_contract_value, location, constraints, summary
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            profile["company_name"],
            profile["owner_name"],
            profile["clearance_level"],
            profile["capabilities"],
            profile["technical_skills"],
            profile["naics_codes"],
            profile["past_performance"],
            profile["contract_vehicles"],
            profile["certifications"],
            profile["max_contract_value"],
            profile["location"],
            profile["constraints"],
            profile["summary"]
        )
    )
    conn.commit()
    print("Company profile seeded: Ariston LLC")


def get_company_profile(conn: sqlite3.Connection) -> dict | None:
    """
    Get the current company profile.

    Args:
        conn: SQLite database connection.

    Returns:
        Company profile as dictionary, or None if not found.
    """
    import json

    cursor = conn.execute("SELECT * FROM company_profile ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()

    if not row:
        return None

    profile = dict(row)

    # Parse JSON fields
    json_fields = [
        "capabilities", "technical_skills", "naics_codes",
        "past_performance", "contract_vehicles", "certifications", "constraints"
    ]
    for field in json_fields:
        if profile.get(field):
            try:
                profile[field] = json.loads(profile[field])
            except json.JSONDecodeError:
                pass

    return profile
