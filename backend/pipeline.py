"""
CutLine Master Pipeline Orchestrator
Coordinates all 5 deterministic stages:
Stage 1: Screenplay Analyzer (Gemini via google-genai)
Stage 2: Parallel Research Agent (Official parallel-web SDK across 5 categories)
Stage 3: Evidence Engine (Requirement -> Evidence semantic matching)
Stage 4: Production Decision Engine (Deterministic Python rule evaluation)
Stage 5: Rewrite Strategist (Gemini production-aware rewrites for RISK/BLOCKED scenes)
"""

import logging
from typing import Callable, Optional

from backend.schemas import (
    PipelineRequest,
    ProductionPlan,
    Phase1Request,
    Phase1Response,
    ScreenplayAnalysisResult,
    ResearchResult,
    DecisionStatusType,
)
from backend.services.gemini_analyzer import analyze_screenplay
from backend.services.parallel_researcher import run_parallel_research
from backend.services.evidence_engine import build_complete_evidence_map
from backend.services.decision_engine import run_decision_engine
from backend.services.rewrite_strategist import run_rewrite_strategist

logger = logging.getLogger("cutline.pipeline")


def run_complete_pipeline(
    request: PipelineRequest,
    step_callback: Optional[Callable[[str], None]] = None,
) -> ProductionPlan:
    """
    Executes the complete 5-stage CutLine production-planning pipeline.
    """
    execution_steps: list[str] = []

    def log_step(msg: str):
        execution_steps.append(msg)
        logger.info(msg)
        if step_callback:
            step_callback(msg)

    # -------------------------------------------------------------------------
    # STAGE 1: SCREENPLAY ANALYSIS (Gemini)
    # -------------------------------------------------------------------------
    log_step("STAGE 1: SCREENPLAY BREAKDOWN (Gemini 3.6 Flash via google-genai)")
    log_step(f"Analyzing screenplay ({len(request.screenplay)} characters)...")

    screenplay_result: ScreenplayAnalysisResult = analyze_screenplay(request.screenplay)
    log_step(
        f"Screenplay parsed: '{screenplay_result.title}' with {screenplay_result.total_scenes} distinct scenes."
    )

    location_types = list(
        {scene.setting for scene in screenplay_result.scenes if scene.setting}
    )

    # -------------------------------------------------------------------------
    # STAGE 2: PARALLEL WEB RESEARCH (Official parallel-web SDK)
    # -------------------------------------------------------------------------
    log_step(f"STAGE 2: PARALLEL WEB RESEARCH (Targeting: {request.location})")

    def parallel_progress(category: str, current: int, total: int):
        log_step(
            f"Parallel search [{current}/{total}]: '{category}' for {request.location}"
        )

    research_result: ResearchResult = run_parallel_research(
        location=request.location,
        shoot_start_date=request.shoot_start_date,
        shoot_end_date=request.shoot_end_date,
        location_types=location_types,
        progress_callback=parallel_progress,
    )

    log_step(
        f"Parallel research complete: {research_result.total_facts} verified facts retrieved across 5 categories."
    )

    # -------------------------------------------------------------------------
    # STAGE 3: EVIDENCE ENGINE
    # -------------------------------------------------------------------------
    log_step("STAGE 3: EVIDENCE ENGINE (Mapping scene requirements to verified evidence)")
    evidence_by_scene, all_evidence = build_complete_evidence_map(
        scenes=screenplay_result.scenes,
        research_facts=research_result.facts,
    )
    log_step(
        f"Evidence Engine linked {len(all_evidence)} evidence items to {len(screenplay_result.scenes)} scenes."
    )

    # -------------------------------------------------------------------------
    # STAGE 4: PRODUCTION DECISION ENGINE (Deterministic Python Rules)
    # -------------------------------------------------------------------------
    log_step("STAGE 4: PRODUCTION DECISION ENGINE (Evaluating deterministic rules)")
    scene_decisions = run_decision_engine(
        scenes=screenplay_result.scenes,
        evidence_by_scene=evidence_by_scene,
    )

    # Compute overall decision counts
    decision_counts = {"GO": 0, "RISK": 0, "BLOCKED": 0}
    for d in scene_decisions:
        decision_counts[d.decision] = decision_counts.get(d.decision, 0) + 1

    overall_decision: DecisionStatusType
    if decision_counts["BLOCKED"] > 0:
        overall_decision = "BLOCKED"
    elif decision_counts["RISK"] > 0:
        overall_decision = "RISK"
    else:
        overall_decision = "GO"

    log_step(
        f"Decision Engine complete. Overall Verdict: {overall_decision} "
        f"(GO: {decision_counts['GO']}, RISK: {decision_counts['RISK']}, BLOCKED: {decision_counts['BLOCKED']})"
    )

    # -------------------------------------------------------------------------
    # STAGE 5: REWRITE STRATEGIST (Gemini - RISK/BLOCKED Scenes Only)
    # -------------------------------------------------------------------------
    flagged_scenes_count = decision_counts["RISK"] + decision_counts["BLOCKED"]
    if flagged_scenes_count > 0:
        log_step(
            f"STAGE 5: REWRITE STRATEGIST (Generating alternatives for {flagged_scenes_count} flagged scene(s))"
        )
        scene_decisions = run_rewrite_strategist(
            decisions=scene_decisions,
            location=request.location,
        )
        log_step("Rewrite Strategist complete: actionable alternatives generated.")
    else:
        log_step("STAGE 5: REWRITE STRATEGIST skipped (All scenes cleared as GO).")

    log_step("Pipeline execution complete. Master production plan assembled.")

    return ProductionPlan(
        project_title=screenplay_result.title,
        location=request.location,
        shoot_window=f"{request.shoot_start_date} to {request.shoot_end_date}",
        budget=request.budget,
        overall_decision=overall_decision,
        decision_counts=decision_counts,
        scenes=scene_decisions,
        all_evidence=all_evidence,
        research_stats=research_result.category_counts,
        failed_categories=research_result.failed_categories,
        category_errors=research_result.category_errors,
        execution_steps=execution_steps,
    )


# Backward-compatible wrapper for Phase 1 verification
def run_phase1_pipeline(
    request: Phase1Request,
    step_callback: Optional[Callable[[str], None]] = None,
) -> Phase1Response:
    """Executes Stages 1 and 2 for Phase 1 testing."""
    execution_steps: list[str] = []

    def log_step(msg: str):
        execution_steps.append(msg)
        logger.info(msg)
        if step_callback:
            step_callback(msg)

    log_step("STAGE 1: SCREENPLAY ANALYSIS (Gemini google-genai)")
    screenplay_result = analyze_screenplay(request.screenplay)
    location_types = list({s.setting for s in screenplay_result.scenes if s.setting})

    log_step("STAGE 2: PARALLEL WEB RESEARCH")
    research_result = run_parallel_research(
        location=request.location,
        shoot_start_date=request.shoot_start_date,
        shoot_end_date=request.shoot_end_date,
        location_types=location_types,
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
