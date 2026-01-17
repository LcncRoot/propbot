"""Configuration module for PropBot.

Loads settings from environment variables with sensible defaults.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Find project root (directory containing .env)
PROJECT_ROOT = Path(__file__).parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

# Load environment variables
load_dotenv(ENV_FILE)


class Config:
    """Application configuration loaded from environment variables."""

    # API Keys
    SAM_API_KEY: str = os.getenv("SAM_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # Database
    DATABASE_PATH: Path = PROJECT_ROOT / os.getenv("DATABASE_PATH", "propbot/data/propbot.db")

    # API Endpoints
    SAM_API_URL: str = "https://api.sam.gov/opportunities/v2/search"
    GRANTS_XML_URL: str = "https://www.grants.gov/xml-extract/"

    # Pipeline settings
    SAM_PAGE_SIZE: int = 100  # Records per API request
    SAM_RATE_LIMIT_DELAY: float = 0.5  # Seconds between requests

    @classmethod
    def validate(cls) -> list[str]:
        """Validate configuration and return list of errors."""
        errors = []
        if not cls.SAM_API_KEY:
            errors.append("SAM_API_KEY is not set")
        if not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is not set")
        return errors


# Singleton instance
config = Config()
