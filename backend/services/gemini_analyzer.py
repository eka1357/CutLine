"""
Stage 1: Screenplay Analyzer
Converts screenplay text into strict structured JSON using Gemini (google-genai SDK)
with Pydantic schema enforcement.
"""

import logging
from google import genai
from google.genai import types

from backend.config import GEMINI_API_KEY, DEFAULT_GEMINI_MODEL, FALLBACK_GEMINI_MODELS
from backend.schemas import ScreenplayAnalysisResult

logger = logging.getLogger("cutline.gemini_analyzer")


SYSTEM_INSTRUCTION = """
You are CutLine's expert Screenplay Production Breakdown Specialist.
Your task is to analyze screenplays and extract structured production requirements
for every scene with extreme precision.

For each scene:
1. Assign a clear scene_id (e.g., 'SCENE_1', 'SCENE_2').
2. Identify the full slugline heading (e.g., 'INT. DIVE DINER - NIGHT').
3. Categorize interior_exterior as 'INT', 'EXT', or 'INT/EXT'.
4. Categorize time_of_day as 'DAY', 'NIGHT', 'DUSK', or 'DAWN'.
5. Extract the physical setting/location type (e.g., 'public pier', 'diner booth', 'residential street').
6. List all concrete production requirements that could impact real-world filming (e.g., 'drone filming', 'night exterior lighting', 'pyrotechnics/stunts', 'crowd control', 'moving vehicle', 'water/tide safety').
7. Summarize the real-world shoot implications (e.g., 'Requires municipal permit for public pier, high tide/wave risk, curfew after 10 PM, drone airspace clearance').

Extract all scenes chronologically. Adhere strictly to the requested JSON schema.
"""


def analyze_screenplay(screenplay_text: str) -> ScreenplayAnalysisResult:
    """
    Analyzes a screenplay using Gemini via google-genai SDK, enforcing
    the ScreenplayAnalysisResult Pydantic schema.
    """
    client = genai.Client(api_key=GEMINI_API_KEY)

    models_to_try = [DEFAULT_GEMINI_MODEL] + [
        m for m in FALLBACK_GEMINI_MODELS if m != DEFAULT_GEMINI_MODEL
    ]

    last_error = None
    for model_name in models_to_try:
        try:
            logger.info(f"Analyzing screenplay with model: {model_name}")
            response = client.models.generate_content(
                model=model_name,
                contents=(
                    f"{SYSTEM_INSTRUCTION}\n\n"
                    f"--- SCREENPLAY TEXT ---\n"
                    f"{screenplay_text}\n"
                    f"--- END SCREENPLAY ---"
                ),
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ScreenplayAnalysisResult,
                    temperature=0.1,  # Low temperature for deterministic extraction
                ),
            )

            # Validate against Pydantic schema
            raw_json = response.text
            parsed_result = ScreenplayAnalysisResult.model_validate_json(raw_json)
            logger.info(
                f"Successfully parsed {parsed_result.total_scenes} scenes using {model_name}"
            )
            return parsed_result

        except Exception as e:
            logger.warning(f"Model {model_name} failed: {e}")
            last_error = e
            import time
            time.sleep(1.2)

    raise RuntimeError(
        f"Stage 1 Screenplay Analyzer failed across all attempted models: {last_error}"
    )
