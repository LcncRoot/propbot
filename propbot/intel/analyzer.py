"""AI-powered opportunity analyzer using OpenAI GPT models."""

import json
from typing import Optional
from datetime import datetime

from openai import OpenAI

from ..config import config
from ..database.connection import get_connection
from ..database.migrations import get_company_profile
from .fetcher import DocumentFetcher
from .extractor import PDFExtractor


class OpportunityAnalyzer:
    """Analyzes opportunities against company profile using AI."""

    def __init__(self, model: str = "gpt-4o-mini"):
        """
        Initialize the analyzer.

        Args:
            model: OpenAI model to use for analysis.
        """
        self.model = model
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.fetcher = DocumentFetcher()
        self.extractor = PDFExtractor()

    def analyze_opportunity(
        self,
        opportunity_id: str,
        fetch_documents: bool = True
    ) -> dict:
        """
        Perform full analysis of an opportunity.

        Args:
            opportunity_id: The opportunity ID to analyze.
            fetch_documents: Whether to fetch/extract documents first.

        Returns:
            Analysis results dictionary.
        """
        conn = get_connection()

        try:
            # Get opportunity from database
            cursor = conn.execute(
                "SELECT * FROM opportunities WHERE opportunity_id = ?",
                (opportunity_id,)
            )
            row = cursor.fetchone()

            if not row:
                raise ValueError(f"Opportunity not found: {opportunity_id}")

            opportunity = dict(row)

            # Get company profile
            profile = get_company_profile(conn)
            if not profile:
                raise ValueError("Company profile not found. Run seed_company_profile first.")

            # Fetch and extract documents if requested
            document_text = ""
            if fetch_documents and opportunity["source"] == "sam.gov":
                try:
                    # Fetch documents
                    self.fetcher.fetch_and_store_documents(opportunity_id)
                    # Extract text
                    self.extractor.extract_and_store(opportunity_id)
                    # Get combined text
                    document_text = self.extractor.get_combined_text(opportunity_id)
                except Exception as e:
                    print(f"Warning: Could not fetch/extract documents: {e}")

            # Build context for AI
            context = self._build_analysis_context(opportunity, profile, document_text)

            # Call OpenAI for analysis
            analysis = self._call_openai(context)

            # Store results
            self._store_analysis(opportunity_id, analysis)

            return analysis

        finally:
            conn.close()

    def _build_analysis_context(
        self,
        opportunity: dict,
        profile: dict,
        document_text: str
    ) -> str:
        """Build the context string for AI analysis."""

        # Truncate document text if too long (keep under ~8k tokens)
        max_doc_chars = 20000
        if len(document_text) > max_doc_chars:
            document_text = document_text[:max_doc_chars] + "\n\n[... truncated ...]"

        context = f"""
## COMPANY PROFILE: {profile['company_name']}

**Owner:** {profile['owner_name']}
**Location:** {profile['location']}
**Clearance Level:** {profile['clearance_level']}

**Capabilities:**
{json.dumps(profile['capabilities'], indent=2)}

**Technical Skills:**
{json.dumps(profile['technical_skills'], indent=2)}

**Relevant NAICS Codes:**
{json.dumps(profile['naics_codes'], indent=2)}

**Past Performance:**
{json.dumps(profile['past_performance'], indent=2)}

**Certifications:**
{json.dumps(profile['certifications'], indent=2)}

**Company Summary:**
{profile['summary']}

---

## OPPORTUNITY DETAILS

**Title:** {opportunity['title']}
**Source:** {opportunity['source']}
**Agency:** {opportunity.get('agency', 'N/A')}
**Notice Type:** {opportunity.get('notice_type', 'N/A')}
**NAICS Code:** {opportunity.get('naics_code', 'N/A')}
**Deadline:** {opportunity.get('deadline', 'N/A')}
**Funding Amount:** {opportunity.get('funding_amount', 'N/A')}

**Description:**
{opportunity.get('description', 'No description available')}

**URL:** {opportunity.get('url', 'N/A')}
"""

        if document_text:
            context += f"""
---

## ATTACHED DOCUMENTS

{document_text}
"""

        return context

    def _call_openai(self, context: str) -> dict:
        """Call OpenAI API for analysis."""

        system_prompt = """You are an expert government contracting analyst helping a small business identify and evaluate federal contract opportunities.

Your task is to analyze the given opportunity against the company's profile and provide:

1. A brief 2-3 sentence summary of what this opportunity is about
2. A fit score from 1-10 (10 = perfect match for company's capabilities)
3. Brief reasoning for the score
4. Key requirements extracted from the opportunity
5. Any red flags or potential disqualifiers
6. Recommended action: "pursue", "research", or "skip"

Respond in JSON format with these exact keys:
{
    "summary": "string",
    "fit_score": number,
    "fit_reasoning": "string",
    "key_requirements": ["requirement1", "requirement2", ...],
    "red_flags": ["flag1", "flag2", ...],
    "recommended_action": "pursue" | "research" | "skip"
}

Be concise but thorough. Focus on actionable insights."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": context}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)

            # Add metadata
            result["model_used"] = self.model
            result["tokens_used"] = response.usage.total_tokens if response.usage else 0

            return result

        except Exception as e:
            print(f"OpenAI API error: {e}")
            return {
                "summary": "Analysis failed due to API error.",
                "fit_score": 0,
                "fit_reasoning": str(e),
                "key_requirements": [],
                "red_flags": ["Analysis failed"],
                "recommended_action": "research",
                "model_used": self.model,
                "tokens_used": 0
            }

    def _store_analysis(self, opportunity_id: str, analysis: dict) -> None:
        """Store analysis results in database."""
        conn = get_connection()

        try:
            conn.execute("""
                INSERT OR REPLACE INTO opportunity_analysis
                (opportunity_id, summary, fit_score, fit_reasoning, key_requirements,
                 red_flags, recommended_action, model_used, tokens_used, analyzed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                opportunity_id,
                analysis.get("summary"),
                analysis.get("fit_score"),
                analysis.get("fit_reasoning"),
                json.dumps(analysis.get("key_requirements", [])),
                json.dumps(analysis.get("red_flags", [])),
                analysis.get("recommended_action"),
                analysis.get("model_used"),
                analysis.get("tokens_used"),
                datetime.now().isoformat()
            ))
            conn.commit()

        finally:
            conn.close()

    def get_analysis(self, opportunity_id: str) -> Optional[dict]:
        """
        Get stored analysis for an opportunity.

        Args:
            opportunity_id: The opportunity ID.

        Returns:
            Analysis dictionary or None if not found.
        """
        conn = get_connection()

        try:
            cursor = conn.execute(
                "SELECT * FROM opportunity_analysis WHERE opportunity_id = ?",
                (opportunity_id,)
            )
            row = cursor.fetchone()

            if not row:
                return None

            analysis = dict(row)

            # Parse JSON fields
            for field in ["key_requirements", "red_flags"]:
                if analysis.get(field):
                    try:
                        analysis[field] = json.loads(analysis[field])
                    except json.JSONDecodeError:
                        pass

            return analysis

        finally:
            conn.close()

    def batch_analyze(
        self,
        opportunity_ids: list[str],
        skip_existing: bool = True
    ) -> list[dict]:
        """
        Analyze multiple opportunities.

        Args:
            opportunity_ids: List of opportunity IDs to analyze.
            skip_existing: Skip opportunities that already have analysis.

        Returns:
            List of analysis results.
        """
        results = []

        for opp_id in opportunity_ids:
            # Check if already analyzed
            if skip_existing:
                existing = self.get_analysis(opp_id)
                if existing:
                    print(f"Skipping {opp_id} (already analyzed)")
                    results.append(existing)
                    continue

            print(f"Analyzing {opp_id}...")
            try:
                result = self.analyze_opportunity(opp_id)
                results.append(result)
            except Exception as e:
                print(f"Error analyzing {opp_id}: {e}")
                results.append({
                    "opportunity_id": opp_id,
                    "error": str(e)
                })

        return results
