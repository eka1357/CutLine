"""
CutLine Configuration
Loads environment variables, validates required API keys, and provides safe logging.
"""

import os
from dotenv import load_dotenv

# Load .env file from project root
load_dotenv()

GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
PARALLEL_API_KEY: str = os.getenv("PARALLEL_API_KEY", "")

# Recommended Gemini model supported for structured generation
DEFAULT_GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

# Fallback Gemini models in case of temporary provider capacity spikes
FALLBACK_GEMINI_MODELS: list[str] = [
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.7-flash",
    "gemini-3.8-flash",
]

# The 5 canonical Parallel Research categories strictly required by AGENTS.md
RESEARCH_CATEGORIES = {
    "filming_permits": "Filming/permit requirements for the stated city/region",
    "location_restrictions": "General location-type filming restrictions (e.g., beaches, piers, drones, curfews)",
    "weather_climate": "Seasonal/weather patterns for the shoot window",
    "public_events": "Public events, festivals, holidays, and street closures in the shoot window",
    "regional_regulations": "General regional filming regulations (noise, fire safety, police monitoring)",
}


def mask_secret(secret: str) -> str:
    """Safely mask API keys so they are never printed in logs or terminal output."""
    if not secret:
        return "<NOT SET>"
    if len(secret) <= 8:
        return "****"
    return f"{secret[:4]}...{secret[-4:]}"


def validate_environment() -> None:
    """Validate that required secrets are present without exposing them."""
    missing = []
    if not GEMINI_API_KEY:
        missing.append("GEMINI_API_KEY")
    if not PARALLEL_API_KEY:
        missing.append("PARALLEL_API_KEY")

    if missing:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing)}. "
            f"Please set them in your .env file or environment."
        )


# Run validation on import to catch missing configuration early
validate_environment()
