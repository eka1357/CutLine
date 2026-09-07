"""
CutLine Pipeline Orchestrator (Phase 1)
Executes Stage 1 Screenplay Analysis (Gemini) followed by Stage 2 Parallel Research.
"""

import logging
from typing import Callable, Optional

from backend.schemas import (
    Phase1Request,
    Phase1Response,
    ScreenplayAnalysisResult,
    ResearchResult,
)
from backend.services.gemini_analyzer import analyze_screenplay
from backend.services.parallel_researcher import run_parallel_research

logger = logging.getLogger("cutline.pipeline")


def run_phase1_pipeline(
    request: Phase1Request,
    step_callback: Optional[Callable[[str], None]] = None,
) -> Phase1Response:
    """
    Runs Phase 1:
    1. Gemini Screenplay Breakdown -> structured scenes & requirements
    2. Parallel Web Research across exactly 5 categories
    """
    execution_steps: list[str] = []

    def log_step(msg: str):
        execution_steps.append(msg)
        logger.info(msg)
        if step_callback:
            step_callback(msg)

    # -------------------------------------------------------------------------
    # STAGE 1: SCREENPLAY ANALYSIS (GEMINI)
    # -------------------------------------------------------------------------
    log_step("STAGE 1: SCREENPLAY ANALYSIS (Gemini google-genai)")
    log_step(f"Parsing screenplay ({len(request.screenplay)} chars)...")

    screenplay_result: ScreenplayAnalysisResult = analyze_screenplay(request.screenplay)
    log_step(
        f"Screenplay analyzed: '{screenplay_result.title}' with {screenplay_result.total_scenes} scenes."
    )

    # Extract distinct location types to guide targeted Parallel queries
    location_types = list(
        {scene.setting for scene in screenplay_result.scenes if scene.setting}
    )

    # -------------------------------------------------------------------------
    # STAGE 2: PARALLEL RESEARCH AGENT (parallel-web)
    # -------------------------------------------------------------------------
    log_step(f"STAGE 2: PARALLEL WEB RESEARCH (Targeting: {request.location})")

    def parallel_progress(category: str, current: int, total: int):
        log_step(
            f"PARALLEL SEARCH CATEGORY {current}/{total}: '{category}' for {request.location}"
        )

    research_result: ResearchResult = run_parallel_research(
        location=request.location,
        shoot_start_date=request.shoot_start_date,
        shoot_end_date=request.shoot_end_date,
        location_types=location_types,
        progress_callback=parallel_progress,
    )

    log_step(
        f"Parallel research complete: {research_result.total_facts} structured facts retrieved across 5 categories."
    )

    return Phase1Response(
        status="success",
        location=request.location,
        shoot_window=f"{request.shoot_start_date} to {request.shoot_end_date}",
        budget=request.budget,
        screenplay_analysis=screenplay_result,
        research_facts=research_result.facts,
        category_summary=research_result.category_counts,
        execution_steps=execution_steps,
    )
