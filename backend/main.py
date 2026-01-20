"""
PropBot Backend API

FastAPI service for searching and retrieving grant and contract opportunities.
Uses SQLite database populated by the propbot pipeline.
"""

import json
import logging
import sys
from pathlib import Path
from typing import Optional

import requests
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

# Add propbot package to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from propbot.config import config
from propbot.database.connection import get_connection
from propbot.embeddings.search import SemanticSearch

# Initialize semantic search (lazy-loads FAISS index)
semantic_search = SemanticSearch()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="PropBot API",
    description="Search and retrieve government grant and contract opportunities",
    version="0.1.0"
)

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# External API for grant details
GRANTS_API_URL = "https://api.grants.gov/v1/api/fetchOpportunity"
DOCUMENTS_DIR = Path(__file__).parent.parent / "scraper/data_gov_scraper/documents"


def row_to_dict(row) -> dict:
    """Convert SQLite Row to dictionary."""
    if row is None:
        return None
    return dict(row)


def rows_to_list(rows) -> list[dict]:
    """Convert SQLite Rows to list of dictionaries."""
    return [dict(row) for row in rows]


# RFI notice types from SAM.gov
RFI_NOTICE_TYPES = ('Sources Sought', 'Special Notice')
# Contract notice types (solicitations)
CONTRACT_NOTICE_TYPES = ('Solicitation', 'Combined Synopsis/Solicitation', 'Presolicitation', 'Award Notice')


@app.get("/api/search")
def search_funding(
    query: str = Query(..., description="Search query"),
    source: Optional[str] = Query(None, description="Filter by source (grants.gov or sam.gov)"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results per type"),
    mode: str = Query("semantic", description="Search mode: 'semantic' (FAISS) or 'keyword' (LIKE)")
):
    """
    Search grants, contracts, and RFIs based on a user query.

    Uses semantic search (FAISS) for better term expansion and relevance.
    Falls back to keyword (LIKE) search if FAISS index unavailable.

    Returns grants, contracts (solicitations), and RFIs (Sources Sought) separately.
    """
    try:
        conn = get_connection()

        # Try semantic search if available and requested
        if mode == "semantic" and semantic_search.is_index_available():
            return _semantic_search(conn, query, source, limit)
        else:
            return _keyword_search(conn, query, source, limit)

    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=f"Error performing search: {str(e)}")


def _semantic_search(conn, query: str, source: Optional[str], limit: int) -> dict:
    """Perform semantic search using FAISS."""
    grants = []
    contracts = []
    rfis = []

    try:
        # Search grants if not filtered to contracts only
        if source != "sam.gov":
            grants_results = semantic_search.search_with_details(
                query=query,
                conn=conn,
                k=limit,
                source_filter="grants.gov"
            )
            grants = grants_results[:limit]

        # Search SAM.gov contracts (exclude RFIs) via FAISS
        if source != "grants.gov":
            sam_results = semantic_search.search_with_details(
                query=query,
                conn=conn,
                k=limit * 2,
                source_filter="sam.gov"
            )

            # Filter to contracts only (exclude RFIs)
            for item in sam_results:
                notice_type = item.get("notice_type")
                if notice_type not in RFI_NOTICE_TYPES:
                    if len(contracts) < limit:
                        contracts.append(item)

            # Query RFIs directly from database (keyword match since there are few)
            query_pattern = f"%{query}%"
            rfi_cursor = conn.execute("""
                SELECT id, opportunity_id, source, title, description, agency,
                       deadline, funding_amount, naics_code, cfda_numbers, url, notice_type
                FROM opportunities
                WHERE source = 'sam.gov'
                  AND notice_type IN ('Sources Sought', 'Special Notice')
                  AND (title LIKE ? OR description LIKE ?)
                ORDER BY deadline DESC
                LIMIT ?
            """, (query_pattern, query_pattern, limit))
            rfis = [dict(row) for row in rfi_cursor.fetchall()]

    finally:
        conn.close()

    # Format for frontend
    for grant in grants:
        if grant.get("cfda_numbers"):
            try:
                grant["cfda_number"] = json.loads(grant["cfda_numbers"])
            except json.JSONDecodeError:
                grant["cfda_number"] = [grant["cfda_numbers"]]
        else:
            grant["cfda_number"] = []
        grant["grant_url"] = grant.get("url")

    for contract in contracts:
        contract["link"] = contract.get("url")
        contract["response_deadline"] = contract.get("deadline")

    for rfi in rfis:
        rfi["link"] = rfi.get("url")
        rfi["response_deadline"] = rfi.get("deadline")

    return {
        "grants": grants,
        "contracts": contracts,
        "rfis": rfis,
        "search_mode": "semantic"
    }


def _keyword_search(conn, query: str, source: Optional[str], limit: int) -> dict:
    """Perform keyword (LIKE) search as fallback."""
    query_pattern = f"%{query}%"

    base_sql = """
        SELECT
            opportunity_id, source, title, description, agency,
            deadline, funding_amount, naics_code, cfda_numbers, url,
            notice_type, matched_keywords, matched_naics
        FROM opportunities
        WHERE (title LIKE ? OR description LIKE ?)
    """

    # Search grants
    grants_sql = base_sql + " AND source = 'grants.gov' ORDER BY deadline DESC LIMIT ?"
    grants_cursor = conn.execute(grants_sql, (query_pattern, query_pattern, limit))
    grants = rows_to_list(grants_cursor)

    # Search contracts (exclude RFI types)
    contracts_sql = base_sql + """
        AND source = 'sam.gov'
        AND (notice_type IS NULL OR notice_type NOT IN ('Sources Sought', 'Special Notice'))
        ORDER BY deadline DESC LIMIT ?
    """
    contracts_cursor = conn.execute(contracts_sql, (query_pattern, query_pattern, limit))
    contracts = rows_to_list(contracts_cursor)

    # Search RFIs (Sources Sought and Special Notice)
    rfis_sql = base_sql + """
        AND source = 'sam.gov'
        AND notice_type IN ('Sources Sought', 'Special Notice')
        ORDER BY deadline DESC LIMIT ?
    """
    rfis_cursor = conn.execute(rfis_sql, (query_pattern, query_pattern, limit))
    rfis = rows_to_list(rfis_cursor)

    conn.close()

    # Parse JSON fields
    for grant in grants:
        if grant.get("cfda_numbers"):
            try:
                grant["cfda_number"] = json.loads(grant["cfda_numbers"])
            except json.JSONDecodeError:
                grant["cfda_number"] = [grant["cfda_numbers"]]
        else:
            grant["cfda_number"] = []
        grant["grant_url"] = grant.get("url")

    for contract in contracts:
        contract["link"] = contract.get("url")
        contract["response_deadline"] = contract.get("deadline")

    for rfi in rfis:
        rfi["link"] = rfi.get("url")
        rfi["response_deadline"] = rfi.get("deadline")

    return {
        "grants": grants,
        "contracts": contracts,
        "rfis": rfis,
        "search_mode": "keyword"
    }


@app.get("/api/opportunities")
def list_opportunities(
    source: Optional[str] = Query(None, description="Filter by source"),
    limit: int = Query(50, ge=1, le=500, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """
    List all opportunities with pagination.

    Returns opportunities ordered by deadline (soonest first).
    """
    try:
        conn = get_connection()

        if source:
            cursor = conn.execute(
                """
                SELECT * FROM opportunities
                WHERE source = ?
                ORDER BY deadline ASC
                LIMIT ? OFFSET ?
                """,
                (source, limit, offset)
            )
        else:
            cursor = conn.execute(
                """
                SELECT * FROM opportunities
                ORDER BY deadline ASC
                LIMIT ? OFFSET ?
                """,
                (limit, offset)
            )

        opportunities = rows_to_list(cursor)
        conn.close()

        return {"opportunities": opportunities, "count": len(opportunities)}

    except Exception as e:
        logger.error(f"List error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/grant/{opportunity_id}")
def fetch_grant_details(opportunity_id: str, fetch_details: bool = False):
    """
    Fetch detailed grant data.

    If fetch_details=true, also fetches additional information from Grants.gov API.
    """
    try:
        conn = get_connection()
        cursor = conn.execute(
            "SELECT * FROM opportunities WHERE opportunity_id = ? AND source = 'grants.gov'",
            (opportunity_id,)
        )
        row = cursor.fetchone()
        conn.close()

        if not row:
            raise HTTPException(status_code=404, detail="Grant not found")

        grant = row_to_dict(row)

        # Parse CFDA numbers
        if grant.get("cfda_numbers"):
            try:
                grant["cfda_number"] = json.loads(grant["cfda_numbers"])
            except json.JSONDecodeError:
                grant["cfda_number"] = [grant["cfda_numbers"]]

        # Map url to grant_url for compatibility
        grant["grant_url"] = grant.get("url")

        if fetch_details:
            # Fetch additional details from Grants.gov API
            try:
                response = requests.post(
                    GRANTS_API_URL,
                    json={"opportunityId": opportunity_id},
                    timeout=30
                )
                response.raise_for_status()
                api_data = response.json().get("data", {})

                grant.update({
                    "opportunity_number": api_data.get("opportunityNumber", "N/A"),
                    "synopsis_description": api_data.get("synopsis", {}).get("synopsisDesc", "N/A"),
                    "eligibility": api_data.get("synopsis", {}).get("applicantEligibilityDesc", "N/A"),
                    "funding_instruments": [
                        fi.get("description", "N/A")
                        for fi in api_data.get("synopsis", {}).get("fundingInstruments", [])
                    ],
                    "award_ceiling": api_data.get("synopsis", {}).get("awardCeilingFormatted", "N/A"),
                    "award_floor": api_data.get("synopsis", {}).get("awardFloorFormatted", "N/A"),
                    "num_awards": api_data.get("synopsis", {}).get("numberOfAwards", "N/A"),
                    "contact_name": api_data.get("synopsis", {}).get("agencyContactName", "-"),
                    "contact_email": api_data.get("synopsis", {}).get("agencyContactEmail", "-"),
                    "contact_phone": api_data.get("synopsis", {}).get("agencyContactPhone", "-"),
                    "funding_activity_categories": [
                        cat.get("description", "N/A")
                        for cat in api_data.get("fundingActivityCategories", [])
                    ],
                    "apply_url": api_data.get("synopsis", {}).get("fundingDescLinkUrl", "N/A"),
                    "attachments": [
                        {
                            "fileName": att.get("fileName", "N/A"),
                            "fileDescription": att.get("fileDescription", "N/A"),
                            "fileUrl": att.get("fileUrl", "N/A")
                        }
                        for folder in api_data.get("synopsisAttachmentFolders", [])
                        for att in folder.get("synopsisAttachments", [])
                    ]
                })
            except requests.RequestException as e:
                logger.warning(f"Failed to fetch grant details from API: {e}")
                # Don't fail the request, just return without extra details

        return grant

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Grant detail error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/contract/{opportunity_id}")
def fetch_contract_details(opportunity_id: str, fetch_details: bool = True):
    """Fetch contract details by opportunity ID.

    If fetch_details=true (default), fetches the full description from SAM.gov API.
    """
    try:
        conn = get_connection()
        cursor = conn.execute(
            "SELECT * FROM opportunities WHERE opportunity_id = ? AND source = 'sam.gov'",
            (opportunity_id,)
        )
        row = cursor.fetchone()
        conn.close()

        if not row:
            raise HTTPException(status_code=404, detail="Contract not found")

        contract = row_to_dict(row)

        # Map fields for frontend compatibility
        contract["link"] = contract.get("url")
        contract["response_deadline"] = contract.get("deadline")

        # Fetch full description from SAM.gov API if description is a URL
        if fetch_details:
            description = contract.get("description", "")
            if description and description.startswith("https://api.sam.gov/"):
                try:
                    # Add API key to the request
                    desc_url = description
                    if "?" in desc_url:
                        desc_url += f"&api_key={config.SAM_API_KEY}"
                    else:
                        desc_url += f"?api_key={config.SAM_API_KEY}"

                    response = requests.get(desc_url, timeout=30)
                    response.raise_for_status()

                    # Response is typically HTML or plain text
                    desc_text = response.text

                    # Clean up the description (remove excessive whitespace)
                    import re
                    desc_text = re.sub(r'\s+', ' ', desc_text).strip()

                    if desc_text:
                        contract["description"] = desc_text

                        # Cache the description in the database
                        try:
                            cache_conn = get_connection()
                            cache_conn.execute(
                                "UPDATE opportunities SET description = ? WHERE opportunity_id = ?",
                                (desc_text, opportunity_id)
                            )
                            cache_conn.commit()
                            cache_conn.close()
                            logger.info(f"Cached description for contract {opportunity_id}")
                        except Exception as cache_err:
                            logger.warning(f"Failed to cache description: {cache_err}")

                except requests.RequestException as e:
                    logger.warning(f"Failed to fetch contract description: {e}")
                    contract["description"] = "Description not available. View on SAM.gov for details."

        return contract

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Contract detail error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats")
def get_stats():
    """Get database statistics."""
    try:
        conn = get_connection()

        # Total counts by source
        cursor = conn.execute(
            "SELECT source, COUNT(*) as count FROM opportunities GROUP BY source"
        )
        source_counts = {row["source"]: row["count"] for row in cursor}

        # Recent ingest runs
        cursor = conn.execute(
            """
            SELECT * FROM ingest_runs
            ORDER BY started_at DESC
            LIMIT 5
            """
        )
        recent_runs = rows_to_list(cursor)

        # Capability filters
        cursor = conn.execute(
            "SELECT filter_type, COUNT(*) as count FROM capability_filters WHERE active = 1 GROUP BY filter_type"
        )
        filter_counts = {row["filter_type"]: row["count"] for row in cursor}

        conn.close()

        return {
            "opportunities": source_counts,
            "total": sum(source_counts.values()),
            "capability_filters": filter_counts,
            "recent_ingest_runs": recent_runs
        }

    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/documents/{doc_id}")
def get_document(doc_id: str):
    """Serve grant-related PDF documents."""
    file_path = DOCUMENTS_DIR / f"{doc_id}.pdf"
    if file_path.exists():
        return FileResponse(str(file_path))
    raise HTTPException(status_code=404, detail="Document not found")


# ============================================================================
# INTEL AGENT ENDPOINTS
# ============================================================================

class BatchAnalyzeRequest(BaseModel):
    """Request body for batch analysis."""
    opportunity_ids: list[str]


@app.post("/api/analyze/batch")
def batch_analyze_opportunities(request: BatchAnalyzeRequest):
    """
    Analyze multiple opportunities in batch with streaming progress.

    Uses Server-Sent Events (SSE) to stream progress updates as each
    opportunity is analyzed.

    Args:
        request: BatchAnalyzeRequest with list of opportunity IDs.

    Returns:
        SSE stream with progress events and final results.
    """
    import time

    def generate():
        from propbot.intel.analyzer import OpportunityAnalyzer

        analyzer = OpportunityAnalyzer()
        total = len(request.opportunity_ids)
        results = []
        skipped = 0

        for idx, opp_id in enumerate(request.opportunity_ids):
            # Check if already analyzed (cached)
            existing = analyzer.get_analysis(opp_id)
            if existing:
                results.append({
                    "opportunity_id": opp_id,
                    "analysis": existing,
                    "cached": True
                })
                skipped += 1
            else:
                try:
                    # Analyze the opportunity
                    result = analyzer.analyze_opportunity(opp_id, fetch_documents=False)
                    results.append({
                        "opportunity_id": opp_id,
                        "analysis": result,
                        "cached": False
                    })
                except Exception as e:
                    logger.error(f"Batch analysis error for {opp_id}: {e}")
                    results.append({
                        "opportunity_id": opp_id,
                        "error": str(e),
                        "cached": False
                    })

                # Rate limit between API calls (only for non-cached)
                time.sleep(0.1)

            # Send progress update
            progress_event = {
                "type": "progress",
                "analyzed": idx + 1,
                "total": total,
                "current_id": opp_id,
                "skipped": skipped
            }
            yield f"data: {json.dumps(progress_event)}\n\n"

        # Send final results
        final_event = {
            "type": "complete",
            "results": results,
            "total_analyzed": total,
            "skipped_cached": skipped
        }
        yield f"data: {json.dumps(final_event)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@app.post("/api/analyze/{opportunity_id}")
def analyze_opportunity(opportunity_id: str, fetch_docs: bool = True):
    """
    Analyze an opportunity using AI.

    Fetches documents, extracts text, and generates AI-powered analysis
    including fit score, summary, and recommendations.

    Args:
        opportunity_id: The opportunity ID to analyze.
        fetch_docs: Whether to fetch and extract documents first.

    Returns:
        Analysis results including summary, fit_score, and recommended_action.
    """
    try:
        from propbot.intel.analyzer import OpportunityAnalyzer

        analyzer = OpportunityAnalyzer()
        result = analyzer.analyze_opportunity(opportunity_id, fetch_documents=fetch_docs)

        return {
            "opportunity_id": opportunity_id,
            "analysis": result
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.get("/api/analysis/{opportunity_id}")
def get_analysis(opportunity_id: str):
    """
    Get stored analysis for an opportunity.

    Returns cached analysis if available, or 404 if not yet analyzed.
    """
    try:
        from propbot.intel.analyzer import OpportunityAnalyzer

        analyzer = OpportunityAnalyzer()
        result = analyzer.get_analysis(opportunity_id)

        if not result:
            raise HTTPException(status_code=404, detail="Analysis not found. Call POST /api/analyze first.")

        return {
            "opportunity_id": opportunity_id,
            "analysis": result
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/recommendations")
def get_recommended_opportunities(min_score: int = Query(7, ge=1, le=10)):
    """
    Get opportunities with high fit scores (recommended for you).

    Args:
        min_score: Minimum fit score to include (default 7).

    Returns:
        List of opportunities with their analysis, sorted by fit score descending.
    """
    try:
        conn = get_connection()

        # Join opportunities with their analysis, filter by fit score
        cursor = conn.execute("""
            SELECT
                o.*,
                a.summary,
                a.fit_score,
                a.fit_reasoning,
                a.key_requirements,
                a.red_flags,
                a.recommended_action,
                a.analyzed_at
            FROM opportunities o
            INNER JOIN opportunity_analysis a ON o.opportunity_id = a.opportunity_id
            WHERE a.fit_score >= ?
            ORDER BY a.fit_score DESC, o.deadline ASC
        """, (min_score,))

        results = []
        for row in cursor.fetchall():
            opp = dict(row)
            # Parse JSON fields from analysis
            if opp.get("key_requirements"):
                try:
                    opp["key_requirements"] = json.loads(opp["key_requirements"])
                except:
                    pass
            if opp.get("red_flags"):
                try:
                    opp["red_flags"] = json.loads(opp["red_flags"])
                except:
                    pass
            results.append(opp)

        conn.close()

        return {
            "opportunities": results,
            "count": len(results),
            "min_score": min_score
        }

    except Exception as e:
        logger.error(f"Recommendations error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/profile")
def get_company_profile():
    """Get the current company profile used for matching."""
    try:
        from propbot.database.migrations import get_company_profile as get_profile

        conn = get_connection()
        profile = get_profile(conn)
        conn.close()

        if not profile:
            raise HTTPException(status_code=404, detail="Company profile not found")

        return profile

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health_check():
    """Health check endpoint."""
    try:
        conn = get_connection()
        cursor = conn.execute("SELECT 1")
        cursor.fetchone()
        conn.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
