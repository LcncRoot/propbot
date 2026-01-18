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

-- ============================================================================
-- INTEL AGENT TABLES (for AI-powered opportunity analysis)
-- ============================================================================

-- Company profile for matching opportunities against capabilities
CREATE TABLE IF NOT EXISTS company_profile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT NOT NULL,
    owner_name TEXT,
    clearance_level TEXT,  -- 'none', 'public_trust', 'secret', 'top_secret', 'ts_sci'
    capabilities TEXT,     -- JSON array: ['cloud', 'devops', 'ai_ml', ...]
    technical_skills TEXT, -- JSON array: ['aws', 'kubernetes', 'python', ...]
    naics_codes TEXT,      -- JSON array: ['541512', '541511', ...]
    past_performance TEXT, -- JSON array of past contract descriptions
    contract_vehicles TEXT, -- JSON array: ['GSA_MAS', 'SEWP', ...]
    certifications TEXT,   -- JSON array: ['small_business', 'sdvosb', ...]
    max_contract_value INTEGER,
    location TEXT,
    constraints TEXT,      -- JSON: any hard constraints
    summary TEXT,          -- Brief company description for AI context
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Store fetched opportunity documents (PDFs, attachments)
CREATE TABLE IF NOT EXISTS opportunity_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    opportunity_id TEXT NOT NULL,
    document_type TEXT,    -- 'sow', 'pws', 'rfi', 'amendment', 'attachment', 'other'
    filename TEXT,
    source_url TEXT,
    file_path TEXT,        -- Local path to stored PDF
    extracted_text TEXT,   -- Full extracted text content
    page_count INTEGER,
    file_size_bytes INTEGER,
    extraction_method TEXT, -- 'pdfplumber', 'ocr', 'html'
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    extracted_at TIMESTAMP,
    FOREIGN KEY (opportunity_id) REFERENCES opportunities(opportunity_id)
);

-- Store AI analysis results
CREATE TABLE IF NOT EXISTS opportunity_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    opportunity_id TEXT NOT NULL UNIQUE,
    summary TEXT,          -- 2-3 sentence TL;DR
    fit_score INTEGER,     -- 1-10 score
    fit_reasoning TEXT,    -- Why this score
    key_requirements TEXT, -- JSON array of extracted requirements
    red_flags TEXT,        -- JSON array of potential disqualifiers
    recommended_action TEXT CHECK(recommended_action IN ('pursue', 'research', 'skip')),
    action_plan TEXT,      -- Suggested next steps
    model_used TEXT,       -- 'gpt-4o-mini', 'claude-sonnet', etc.
    tokens_used INTEGER,
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (opportunity_id) REFERENCES opportunities(opportunity_id)
);

-- Indexes for intel agent tables
CREATE INDEX IF NOT EXISTS idx_documents_opportunity ON opportunity_documents(opportunity_id);
CREATE INDEX IF NOT EXISTS idx_analysis_opportunity ON opportunity_analysis(opportunity_id);
CREATE INDEX IF NOT EXISTS idx_analysis_score ON opportunity_analysis(fit_score DESC);
CREATE INDEX IF NOT EXISTS idx_analysis_action ON opportunity_analysis(recommended_action);
