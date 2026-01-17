-- PropBot Database Schema
-- SQLite database for storing grant and contract opportunities

-- Core opportunities table (unified for grants and contracts)
CREATE TABLE IF NOT EXISTS opportunities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    opportunity_id TEXT UNIQUE NOT NULL,
    source TEXT NOT NULL CHECK(source IN ('grants.gov', 'sam.gov')),
    title TEXT NOT NULL,
    description TEXT,
    agency TEXT,

    -- Deadline (normalized to ISO 8601)
    deadline TEXT,

    -- Funding (nullable for contracts)
    funding_amount INTEGER,

    -- Category codes
    naics_code TEXT,
    cfda_numbers TEXT,  -- JSON array for grants

    -- Notice type (for SAM.gov: Sources Sought, Solicitation, etc.)
    notice_type TEXT,

    -- Links
    url TEXT,

    -- Capability matching results
    matched_keywords TEXT,  -- JSON array of matched keywords
    matched_naics TEXT,     -- JSON array of matched NAICS codes

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Capability configuration table
CREATE TABLE IF NOT EXISTS capability_filters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filter_type TEXT NOT NULL CHECK(filter_type IN ('naics', 'keyword')),
    value TEXT NOT NULL,
    description TEXT,
    active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(filter_type, value)
);

-- Ingest run tracking table
CREATE TABLE IF NOT EXISTS ingest_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    status TEXT DEFAULT 'running' CHECK(status IN ('running', 'completed', 'failed')),
    records_fetched INTEGER DEFAULT 0,
    records_filtered_expired INTEGER DEFAULT 0,
    records_filtered_capability INTEGER DEFAULT 0,
    records_inserted INTEGER DEFAULT 0,
    records_updated INTEGER DEFAULT 0,
    error_message TEXT
);

-- Indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_opportunities_source ON opportunities(source);
CREATE INDEX IF NOT EXISTS idx_opportunities_deadline ON opportunities(deadline);
CREATE INDEX IF NOT EXISTS idx_opportunities_naics ON opportunities(naics_code);
CREATE INDEX IF NOT EXISTS idx_opportunities_created ON opportunities(created_at);
CREATE INDEX IF NOT EXISTS idx_capability_filters_type ON capability_filters(filter_type, active);
CREATE INDEX IF NOT EXISTS idx_ingest_runs_source ON ingest_runs(source, started_at);
