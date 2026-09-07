"""
Pydantic Schemas for CutLine
Defines strict data models for Screenplay Analysis, Parallel Web Research, and Phase 1 API.
"""

from typing import Literal, Optional
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
    source_title: str = Field(
        default="",
        description="Title of the source webpage or publication."
    )
    source_domain: str = Field(
        default="",
        description="Domain name of the source (e.g., santamonica.gov, film.ca.gov)."
    )
    evidence_text: str = Field(
        default="",
        description="Exact excerpt passage from Parallel search results supporting this claim."
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
    failed_categories: list[str] = Field(
        default_factory=list,
        description="List of categories where Parallel search failed or yielded no results."
    )
    category_errors: dict[str, str] = Field(
        default_factory=dict,
        description="Error messages for any category search that encountered API/network exceptions."
    )


# -----------------------------------------------------------------------------
# Stage 3: Evidence Engine Schemas
# -----------------------------------------------------------------------------

EvidenceStrengthType = Literal["direct", "contextual", "inferred"]


class EvidenceItem(BaseModel):
    """
    Structured evidence item attaching a verified research fact to a specific scene requirement.
    Preserves complete provenance: Scene -> Requirement -> Claim -> Source URL.
    """
    evidence_id: str = Field(
        description="Unique identifier for this evidence attachment, e.g., 'EVID_SCENE2_1'."
    )
    scene_id: str = Field(
        description="ID of the scene this evidence affects."
    )
    requirement_name: str = Field(
        description="The specific production requirement this evidence relates to."
    )
    category: ResearchCategoryType = Field(
        description="The canonical research category."
    )
    claim: str = Field(
        description="Specific factual statement retrieved from research."
    )
    source_url: str = Field(
        description="Exact HTTP(S) URL of the source."
    )
    source_title: str = Field(
        default="",
        description="Title of the source publication or authority."
    )
    source_domain: str = Field(
        default="",
        description="Domain of the source authority."
    )
    evidence_text: str = Field(
        default="",
        description="Supporting excerpt from the source."
    )
    relevance_explanation: str = Field(
        description="Explanation of why this evidence bears on this scene's requirement."
    )
    strength: EvidenceStrengthType = Field(
        default="direct",
        description="Strength of the connection between evidence and requirement."
    )


# -----------------------------------------------------------------------------
# Stage 4: Production Decision Engine Schemas
# -----------------------------------------------------------------------------

DecisionStatusType = Literal["GO", "RISK", "BLOCKED"]


class DecisionFinding(BaseModel):
    """
    Individual rule-based evaluation: Requirement -> Evidence -> Rule -> Consequence.
    Deterministic, auditable, and backed by stored evidence.
    """
    finding_id: str = Field(
        description="Unique ID for this finding, e.g., 'FINDING_SCENE2_CURFEW'."
    )
    scene_id: str = Field(
        description="Scene ID evaluated."
    )
    requirement_name: str = Field(
        description="The requirement under evaluation."
    )
    rule_name: str = Field(
        description="Name of the deterministic production rule that evaluated this requirement."
    )
    rule_description: str = Field(
        description="Human-readable description of the production rule."
    )
    consequence: DecisionStatusType = Field(
        description="Consequence of the rule: GO, RISK, or BLOCKED."
    )
    reason: str = Field(
        description="Specific operational or legal rationale explaining the consequence."
    )
    supporting_evidence: list[EvidenceItem] = Field(
        default_factory=list,
        description="List of verified evidence items that triggered or justified this finding."
    )


# -----------------------------------------------------------------------------
# Stage 5: Rewrite Strategist Schemas
# -----------------------------------------------------------------------------

RewriteStrategyType = Literal[
    "timing_shift",
    "location_swap",
    "technical_rewrite",
    "procedural_mitigation",
]


class ProductionAlternative(BaseModel):
    """
    Concrete production alternative proposing an actionable rewrite or schedule modification.
    Preserves cinematic intent while eliminating the identified blocking constraint.
    """
    alternative_id: str = Field(
        description="Unique identifier, e.g., 'ALT_SCENE2_1'."
    )
    title: str = Field(
        description="Concise descriptive title, e.g., 'Dawn Shoreline Foot Pursuit'."
    )
    strategy_type: RewriteStrategyType = Field(
        description="Category of strategic change: timing_shift, location_swap, technical_rewrite, procedural_mitigation."
    )
    cinematic_intent_preserved: str = Field(
        description="How the artistic, tonal, and dramatic intent of the scene is kept intact."
    )
    constraint_removed: str = Field(
        description="The specific production constraint, rule, or curfew eliminated by this change."
    )
    production_mechanism_change: str = Field(
        description="Concrete change in crew, gear, permit type, or schedule."
    )
    estimated_impact: str = Field(
        description="One-line practical impact on shoot feasibility, lead time, or risk."
    )
    rewritten_scene_excerpt: str = Field(
        description="Concrete screenplay draft showing the rewritten slugline, action, and key dialogue."
    )


class SceneRewritePackage(BaseModel):
    """Container for alternatives generated by Stage 5 for a single scene."""
    scene_id: str
    alternatives: list[ProductionAlternative] = Field(
        default_factory=list,
        description="2 to 3 concrete production alternatives."
    )


# -----------------------------------------------------------------------------
# End-to-End Production Plan (Frontend Ready)
# -----------------------------------------------------------------------------

class SceneProductionDecision(BaseModel):
    """Complete production assessment for a single scene."""
    scene_id: str
    heading: str
    interior_exterior: Literal["INT", "EXT", "INT/EXT"]
    time_of_day: Literal["DAY", "NIGHT", "DUSK", "DAWN"]
    setting: str
    requirements: list[str]
    shoot_implications: str
    decision: DecisionStatusType = Field(
        description="Final deterministic verdict for this scene: GO, RISK, or BLOCKED."
    )
    decision_summary: str = Field(
        description="High-level production summary explaining the verdict."
    )
    findings: list[DecisionFinding] = Field(
        default_factory=list,
        description="Detailed rule-by-rule findings with attached evidence."
    )
    attached_evidence: list[EvidenceItem] = Field(
        default_factory=list,
        description="All evidence items grounded in this scene."
    )
    alternatives: list[ProductionAlternative] = Field(
        default_factory=list,
        description="Actionable alternatives (populated only if RISK or BLOCKED)."
    )


class ProductionPlan(BaseModel):
    """The master production plan returned by CutLine."""
    project_title: str
    location: str
    shoot_window: str
    budget: float
    production_type: Optional[str] = Field(
        default="Independent Feature",
        description="Production scale category (e.g., 'Independent Feature', 'Commercial', 'Student / Micro-Budget')."
    )
    crew_size: Optional[str] = Field(
        default="Medium (11-30 crew)",
        description="Estimated crew footprint tier."
    )
    overall_decision: DecisionStatusType = Field(
        description="Worst-case roll-up: BLOCKED if any scene blocked; RISK if any scene risky; else GO."
    )
    decision_counts: dict[str, int] = Field(
        description="Count of scenes by status: {'GO': n, 'RISK': n, 'BLOCKED': n}."
    )
    scenes: list[SceneProductionDecision] = Field(
        description="Chronological scene assessments."
    )
    all_evidence: list[EvidenceItem] = Field(
        description="Complete list of all attached evidence across all scenes."
    )
    research_stats: dict[str, int] = Field(
        description="Summary of facts retrieved per category."
    )
    failed_categories: list[str] = Field(
        default_factory=list,
        description="Categories where Parallel search yielded no results or encountered an error."
    )
    category_errors: dict[str, str] = Field(
        default_factory=dict,
        description="Error details for failed searches if any."
    )
    execution_steps: list[str] = Field(
        default_factory=list,
        description="Pipeline execution telemetry trace."
    )


# Backward-compatible request and response
class Phase1Request(BaseModel):
    """Payload for production planning request."""
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
    production_type: Optional[str] = Field(
        default="Independent Feature",
        description="Production scale category (e.g., 'Independent Feature', 'Commercial', 'Student / Micro-Budget')."
    )
    crew_size: Optional[str] = Field(
        default="Medium (11-30 crew)",
        description="Estimated crew footprint tier."
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


PipelineRequest = Phase1Request
PipelineResponse = ProductionPlan

