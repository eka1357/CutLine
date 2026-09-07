"""
Pydantic Schemas for CutLine
Defines strict data models for Screenplay Analysis, Parallel Web Research, and Phase 1 API.
"""

from typing import Literal
from pydantic import BaseModel, Field


# -----------------------------------------------------------------------------
# Stage 1: Screenplay Analyzer Schemas
# -----------------------------------------------------------------------------

class ExtractedScene(BaseModel):
    """Structured representation of a parsed screenplay scene."""
    scene_id: str = Field(
        description="Unique scene identifier, e.g., 'SCENE_1', 'SCENE_2'."
    )
    heading: str = Field(
        description="Full scene heading slugline, e.g., 'INT. DIVE DINER - NIGHT'."
    )
    interior_exterior: Literal["INT", "EXT", "INT/EXT"] = Field(
        description="Whether the scene takes place interior, exterior, or both."
    )
    time_of_day: Literal["DAY", "NIGHT", "DUSK", "DAWN"] = Field(
        description="Time of day for the shoot."
    )
    setting: str = Field(
        description="Physical location or setting type, e.g., 'pier', 'beach', 'coffee shop', 'rooftop'."
    )
    requirements: list[str] = Field(
        default_factory=list,
        description=(
            "Specific production-relevant requirements extracted from action or context, "
            "e.g., 'drone filming', 'night exterior lighting', 'pyrotechnics', 'crowd extras', 'moving vehicle'."
        )
    )
    shoot_implications: str = Field(
        description=(
            "Specific real-world production implications, such as night noise curfews, "
            "tide sensitivity, public property permits, or traffic control."
        )
    )


class ScreenplayAnalysisResult(BaseModel):
    """Container for the complete structured output from Stage 1."""
    title: str = Field(
        default="Untitled Screenplay",
        description="Title of the screenplay or scene collection."
    )
    total_scenes: int = Field(
        description="Total count of extracted scenes."
    )
    scenes: list[ExtractedScene] = Field(
        default_factory=list,
        description="Chronological list of parsed scenes with production attributes."
    )


# -----------------------------------------------------------------------------
# Stage 2: Parallel Research Agent Schemas
# -----------------------------------------------------------------------------

ResearchCategoryType = Literal[
    "filming_permits",
    "location_restrictions",
    "weather_climate",
    "public_events",
    "regional_regulations",
]


class ResearchFact(BaseModel):
    """Structured fact retrieved from Parallel Search API with verifiable provenance."""
    claim: str = Field(
        description="Concrete factual claim or rule discovered from live web research."
    )
    source_url: str = Field(
        description="Exact HTTP(S) URL where this fact was retrieved."
    )
    category: ResearchCategoryType = Field(
        description="One of the exactly 5 authorized research categories."
    )
    relevance_summary: str = Field(
        default="",
        description="Brief summary of how this fact relates to filming in this region or date window."
    )


class ResearchResult(BaseModel):
    """Aggregated research results across all 5 categories."""
    location: str
    shoot_start_date: str
    shoot_end_date: str
    total_facts: int
    category_counts: dict[str, int]
    facts: list[ResearchFact]


# -----------------------------------------------------------------------------
# Phase 1: API Request & Response Schemas
# -----------------------------------------------------------------------------

class Phase1Request(BaseModel):
    """Payload for the CutLine Phase 1 test endpoint."""
    screenplay: str = Field(
        ...,
        min_length=20,
        description="Raw text of the screenplay or scene to analyze."
    )
    location: str = Field(
        ...,
        description="Proposed shoot location (e.g., 'Santa Monica, CA', 'Los Angeles, CA')."
    )
    shoot_start_date: str = Field(
        ...,
        description="Proposed start date (YYYY-MM-DD)."
    )
    shoot_end_date: str = Field(
        ...,
        description="Proposed end date (YYYY-MM-DD)."
    )
    budget: float = Field(
        ...,
        ge=0.0,
        description="Total proposed production budget in USD."
    )


class Phase1Response(BaseModel):
    """Response returned by the CutLine Phase 1 test endpoint."""
    status: Literal["success", "partial_success", "error"]
    location: str
    shoot_window: str
    budget: float
    screenplay_analysis: ScreenplayAnalysisResult
    research_facts: list[ResearchFact]
    category_summary: dict[str, int]
    execution_steps: list[str]
