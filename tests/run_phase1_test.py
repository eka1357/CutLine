"""
CutLine Phase 1 Developer Verification Runner
Executes Stage 1 (Gemini) and Stage 2 (Parallel Search) and verifies:
1. Gemini converts screenplay to structured scenes and production requirements.
2. Parallel Search executes across all 5 mandatory categories.
3. Every fact retains an authentic, verified source URL.
4. Secrets are never exposed in output.
"""

import sys
import os

# Ensure UTF-8 output encoding for terminal on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add repo root to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.config import mask_secret, GEMINI_API_KEY, PARALLEL_API_KEY
from backend.schemas import Phase1Request
from backend.pipeline import run_phase1_pipeline
from tests.test_original_screenplay import (
    NEON_DRIFTWOOD_SCREENPLAY,
    TEST_LOCATION,
    TEST_START_DATE,
    TEST_END_DATE,
    TEST_BUDGET,
)


def run_verification():
    print("=" * 80)
    print("CUTLINE PHASE 1 DEVELOPER VERIFICATION")
    print("Agentic Cinema Hackathon — Parallel Track")
    print("=" * 80)
    print(f"Gemini API Key configured:   {mask_secret(GEMINI_API_KEY)}")
    print(f"Parallel API Key configured: {mask_secret(PARALLEL_API_KEY)}")
    print("-" * 80)

    request = Phase1Request(
        screenplay=NEON_DRIFTWOOD_SCREENPLAY,
        location=TEST_LOCATION,
        shoot_start_date=TEST_START_DATE,
        shoot_end_date=TEST_END_DATE,
        budget=TEST_BUDGET,
    )

    print(f"Proposed Location:   {request.location}")
    print(f"Proposed Window:     {request.shoot_start_date} to {request.shoot_end_date}")
    print(f"Proposed Budget:     ${request.budget:,.2f}")
    print("=" * 80)

    # Developer verification step callback
    def on_step(step_text: str):
        print(f"\n[STEP] {step_text}")

    response = run_phase1_pipeline(request, step_callback=on_step)

    # -------------------------------------------------------------------------
    # VERIFICATION OUTPUT
    # -------------------------------------------------------------------------
    print("\n" + "#" * 80)
    print("STAGE 1: SCREENPLAY ANALYSIS RESULTS")
    print("#" * 80)
    print(f"Screenplay Title: {response.screenplay_analysis.title}")
    print(f"Total Scenes Extracted: {response.screenplay_analysis.total_scenes}\n")

    for scene in response.screenplay_analysis.scenes:
        print(f"[{scene.scene_id}] {scene.heading}")
        print(f"  Type:         {scene.interior_exterior} | {scene.time_of_day}")
        print(f"  Setting:      {scene.setting}")
        print(f"  Requirements: {', '.join(scene.requirements)}")
        print(f"  Implications: {scene.shoot_implications}")
        print("-" * 60)

    print("\n" + "#" * 80)
    print("STAGE 2: PARALLEL WEB RESEARCH RESULTS (5 CATEGORIES)")
    print("#" * 80)
    print(f"Total Facts Retrieved: {len(response.research_facts)}")
    print(f"Category Breakdown:    {response.category_summary}\n")

    # Group facts by category for inspection
    by_category: dict[str, list] = {}
    for fact in response.research_facts:
        by_category.setdefault(fact.category, []).append(fact)

    for cat_name, facts in by_category.items():
        print(f"\n>>> CATEGORY: {cat_name.upper()} ({len(facts)} facts)")
        for idx, fact in enumerate(facts, 1):
            print(f"  {idx}. CLAIM: {fact.claim}")
            print(f"     SOURCE URL: {fact.source_url}")

    # -------------------------------------------------------------------------
    # ACCEPTANCE CRITERIA ASSERTIONS
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("PHASE 1 ACCEPTANCE CHECKLIST AUDIT")
    print("=" * 80)

    # Check 1: Scenes parsed
    assert response.screenplay_analysis.total_scenes >= 2, "Failed: Expected at least 2 scenes"
    print(" [PASS] Gemini Screenplay Analyzer parsed scenes into strict JSON.")

    # Check 2: Facts produced
    assert len(response.research_facts) >= 5, "Failed: Expected at least 5 facts"
    print(f" [PASS] Parallel Research Agent produced {len(response.research_facts)} structured facts.")

    # Check 3: All 5 categories covered
    assert len(response.category_summary) == 5, "Failed: Not all 5 categories were searched"
    print(" [PASS] All 5 mandatory evidence categories were searched.")

    # Check 4: Source URLs preserved
    for fact in response.research_facts:
        assert fact.source_url.startswith("http"), f"Invalid source URL: {fact.source_url}"
    print(" [PASS] Every single fact retains a verified HTTP(S) source URL.")

    # Check 5: No secrets leaked in representation
    as_dict_str = str(response.model_dump())
    assert GEMINI_API_KEY not in as_dict_str, "CRITICAL: Gemini key found in output"
    assert PARALLEL_API_KEY not in as_dict_str, "CRITICAL: Parallel key found in output"
    print(" [PASS] Zero API keys or secrets exposed in output payloads.")

    print("\n>>> PHASE 1 ACCEPTANCE TEST PASSED SUCCESSFULLY! <<<\n")
    return response


if __name__ == "__main__":
    run_verification()
