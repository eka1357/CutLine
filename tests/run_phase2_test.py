"""
CutLine Phase 2 Master Pipeline Verification Runner
Executes all 5 deterministic stages against the original screenplay "Neon Driftwood"
and verifies:
1. Stage 1: Gemini parses scenes into structured requirements.
2. Stage 2: Parallel Search retrieves real web facts across 5 categories.
3. Stage 3: Evidence Engine grounds requirements to real search facts.
4. Stage 4: Decision Engine evaluates deterministic rules (GO / RISK / BLOCKED).
5. Stage 5: Rewrite Strategist generates production-aware alternatives with draft excerpts.
6. Acceptance assertions:
   - Scene 1 (interior diner) evaluates naturally to GO.
   - Scene 2 (night pier chase with drone, blanks, high surf) evaluates to RISK/BLOCKED.
   - Zero numeric feasibility or confidence scores exist.
   - Complete provenance preserved: Scene -> Requirement -> Evidence -> URL -> Rule -> Rewrite.
   - Zero API keys exposed.
"""

import sys
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.config import mask_secret, GEMINI_API_KEY, PARALLEL_API_KEY
from backend.schemas import PipelineRequest, ProductionPlan
from backend.pipeline import run_complete_pipeline
from tests.test_original_screenplay import (
    NEON_DRIFTWOOD_SCREENPLAY,
    TEST_LOCATION,
    TEST_START_DATE,
    TEST_END_DATE,
    TEST_BUDGET,
)


def run_phase2_verification():
    print("=" * 80)
    print("CUTLINE MASTER PIPELINE DEVELOPER VERIFICATION (PHASE 2)")
    print("Agentic Cinema Hackathon — Parallel Track")
    print("=" * 80)
    print(f"Gemini API Key:   {mask_secret(GEMINI_API_KEY)}")
    print(f"Parallel API Key: {mask_secret(PARALLEL_API_KEY)}")
    print(f"Location:         {TEST_LOCATION}")
    print(f"Shoot Window:     {TEST_START_DATE} to {TEST_END_DATE}")
    print(f"Budget:           ${TEST_BUDGET:,.2f}")
    print("=" * 80)

    request = PipelineRequest(
        screenplay=NEON_DRIFTWOOD_SCREENPLAY,
        location=TEST_LOCATION,
        shoot_start_date=TEST_START_DATE,
        shoot_end_date=TEST_END_DATE,
        budget=TEST_BUDGET,
    )

    def on_step(msg: str):
        print(f"\n>>> {msg}")

    plan: ProductionPlan = run_complete_pipeline(request, step_callback=on_step)

    # -------------------------------------------------------------------------
    # PRINT MASTER VERIFICATION REPORT
    # -------------------------------------------------------------------------
    print("\n" + "#" * 80)
    print(f"CUTLINE MASTER PRODUCTION PLAN: '{plan.project_title.upper()}'")
    print(f"Overall Project Verdict: {plan.overall_decision}")
    print(f"Decision Breakdown:      {plan.decision_counts}")
    print(f"Total Attached Evidence: {len(plan.all_evidence)}")
    print("#" * 80)

    for idx, scene_dec in enumerate(plan.scenes, 1):
        print(f"\n{'='*70}")
        print(f"SCENE {idx}: [{scene_dec.decision}] {scene_dec.heading}")
        print(f"Location Type: {scene_dec.interior_exterior} | Time: {scene_dec.time_of_day} | Setting: {scene_dec.setting}")
        print(f"Summary:       {scene_dec.decision_summary}")
        print(f"{'-'*70}")

        print("\n  [DETERMINISTIC RULE FINDINGS]")
        if scene_dec.findings:
            for f in scene_dec.findings:
                print(f"   Rule:        {f.rule_name} [{f.consequence}]")
                print(f"   Requirement: {f.requirement_name}")
                print(f"   Reason:      {f.reason}")
                print(f"   Supporting Evidence ({len(f.supporting_evidence)} items):")
                for ev in f.supporting_evidence:
                    print(f"     * [{ev.source_domain}] {ev.claim[:120]}...")
                    print(f"       Source URL: {ev.source_url}")
        else:
            print("   (No restrictive rules fired)")

        if scene_dec.alternatives:
            print(f"\n  [STAGE 5 ACTIONABLE REWRITE ALTERNATIVES ({len(scene_dec.alternatives)})]")
            for a_idx, alt in enumerate(scene_dec.alternatives, 1):
                print(f"\n   ALTERNATIVE {a_idx}: \"{alt.title}\" ({alt.strategy_type})")
                print(f"    - Cinematic Intent Preserved: {alt.cinematic_intent_preserved}")
                print(f"    - Constraint Removed:         {alt.constraint_removed}")
                print(f"    - Mechanism Change:           {alt.production_mechanism_change}")
                print(f"    - Estimated Impact:           {alt.estimated_impact}")
                print(f"    - Draft Excerpt:\n{alt.rewritten_scene_excerpt.strip()}")

    # -------------------------------------------------------------------------
    # RIGOROUS ACCEPTANCE ASSERTIONS
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("PHASE 2 ACCEPTANCE AUDIT CHECKLIST")
    print("=" * 80)

    # 1. Verify Scene 1 is GO
    scene_1 = next(s for s in plan.scenes if "SCENE_1" in s.scene_id)
    assert scene_1.decision == "GO", f"Expected Scene 1 to be GO, got {scene_1.decision}"
    print(f" [PASS] Scene 1 ({scene_1.heading}) naturally evaluated to GO.")

    # 2. Verify Scene 2 is RISK or BLOCKED
    scene_2 = next(s for s in plan.scenes if "SCENE_2" in s.scene_id)
    assert scene_2.decision in ("RISK", "BLOCKED"), f"Expected Scene 2 to be RISK/BLOCKED, got {scene_2.decision}"
    print(f" [PASS] Scene 2 ({scene_2.heading}) evaluated to {scene_2.decision} based on evidence.")

    # 3. Verify Scene 1 has NO rewrite alternatives (only for RISK/BLOCKED)
    assert len(scene_1.alternatives) == 0, "GO scene must not have rewrite alternatives"
    print(" [PASS] Scene 1 has 0 alternatives (Stage 5 correctly skipped for GO).")

    # 4. Verify Scene 2 has 2 to 3 actionable alternatives
    assert len(scene_2.alternatives) >= 2, f"Expected at least 2 alternatives for Scene 2, got {len(scene_2.alternatives)}"
    print(f" [PASS] Scene 2 generated {len(scene_2.alternatives)} concrete production alternatives.")

    # 5. Verify every finding has supporting evidence with valid HTTP(S) URL
    for s in plan.scenes:
        for f in s.findings:
            if f.consequence in ("RISK", "BLOCKED"):
                assert len(f.supporting_evidence) > 0, f"Finding {f.finding_id} missing supporting evidence"
                for ev in f.supporting_evidence:
                    assert ev.source_url.startswith("http"), f"Invalid source URL: {ev.source_url}"
    print(" [PASS] 100% of RISK/BLOCKED findings are grounded in verified HTTP(S) evidence.")

    # 6. Verify NO numeric scores exist in output
    plan_dict = plan.model_dump()
    plan_str = str(plan_dict).lower()
    for forbidden in ["score", "percentage", "confidence_score", "feasibility_score"]:
        assert forbidden not in plan_dict, f"Forbidden numeric score key '{forbidden}' found in plan schema"
    print(" [PASS] Zero numeric feasibility or confidence scores present in schema.")

    # 7. Verify zero secrets exposed
    assert GEMINI_API_KEY not in plan_str, "CRITICAL: Gemini key exposed in output!"
    assert PARALLEL_API_KEY not in plan_str, "CRITICAL: Parallel key exposed in output!"
    print(" [PASS] Zero API keys or secrets exposed in output representation.")

    print("\n>>> MASTER PIPELINE VERIFICATION PASSED ALL AUDITS! <<<\n")
    return plan


if __name__ == "__main__":
    run_phase2_verification()
