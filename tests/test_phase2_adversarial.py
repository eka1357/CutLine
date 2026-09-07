"""
Adversarial and Negative Tests for CutLine Phase 2 Pipeline
Validates system resilience, strict evidence grounding, and absence of hallucinations:
1. Irrelevant evidence must not trigger a decision.
2. Missing evidence must not be treated as a blocker (conservative fallback).
3. Failed Parallel searches must not create facts (zero synthetic fallbacks).
4. Every RISK/BLOCKED finding must have supporting evidence.
5. Every evidence item must retain its source URL.
6. No API secrets can appear in output.
7. No numeric feasibility or confidence scores.
"""

import sys
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.config import GEMINI_API_KEY, PARALLEL_API_KEY
from backend.schemas import (
    ExtractedScene,
    ResearchFact,
    EvidenceItem,
    ResearchResult,
)
from backend.services.evidence_engine import (
    build_scene_evidence,
    build_complete_evidence_map,
)
from backend.services.decision_engine import (
    evaluate_scene,
    run_decision_engine,
)
from backend.services.parallel_researcher import (
    is_boilerplate,
    extract_claims_from_excerpt,
)


def test_irrelevant_evidence_does_not_trigger_decision():
    """Adversarial Test 1: Irrelevant evidence (e.g. restaurant menus or parking fees) must not trigger rules."""
    print("Testing Adversarial Test 1: Irrelevant evidence does not trigger rules...")
    clean_scene = ExtractedScene(
        scene_id="SCENE_TEST_1",
        heading="INT. ART GALLERY - DAY",
        interior_exterior="INT",
        time_of_day="DAY",
        setting="private art gallery",
        requirements=["dialogue between two curators", "holding wine glasses"],
        shoot_implications="Standard private indoor gallery rental",
    )

    irrelevant_facts = [
        ResearchFact(
            claim="Santa Monica Pier Ferris Wheel tickets cost $15 per adult during holiday weekends.",
            source_url="https://pacpark.com/tickets",
            source_title="Pacific Park Tickets",
            source_domain="pacpark.com",
            evidence_text="Ticket pricing for the Pacific Wheel and roller coaster.",
            category="location_restrictions",
        ),
        ResearchFact(
            claim="Downtown Santa Monica parking structure #2 offers 90 minutes of free parking.",
            source_url="https://santamonica.gov/parking",
            source_title="Santa Monica Parking",
            source_domain="santamonica.gov",
            evidence_text="Public parking details in downtown structures.",
            category="regional_regulations",
        ),
    ]

    attached_evidence = build_scene_evidence(clean_scene, irrelevant_facts)
    # The evidence engine should correctly determine none of this applies to an indoor art gallery dialogue
    assert len(attached_evidence) == 0, f"Expected 0 attached evidence items, got {len(attached_evidence)}"

    decision = evaluate_scene(clean_scene, attached_evidence)
    assert decision.decision == "GO", f"Expected GO for gallery scene with irrelevant facts, got {decision.decision}"
    print(" [PASS] Irrelevant facts correctly ignored; clean scene remains GO.")


def test_missing_evidence_does_not_fabricate_blockers():
    """Adversarial Test 2: When no evidence is retrieved for a requirement, no restrictive rule should fire."""
    print("\nTesting Adversarial Test 2: Missing evidence does not fabricate blockers...")
    mystery_scene = ExtractedScene(
        scene_id="SCENE_TEST_2",
        heading="EXT. MYSTERY HILL - NIGHT",
        interior_exterior="EXT",
        time_of_day="NIGHT",
        setting="unspecified hill",
        requirements=["looking at stars through telescope"],
        shoot_implications="Nighttime exterior stargazing",
    )

    # Empty research facts
    empty_facts: list[ResearchFact] = []
    attached_evidence = build_scene_evidence(mystery_scene, empty_facts)
    assert len(attached_evidence) == 0

    decision = evaluate_scene(mystery_scene, attached_evidence)
    # Without verified evidence of a noise curfew or municipal prohibition on this hill, no rule fires
    assert len(decision.findings) == 0, f"Expected 0 findings without evidence, got {len(decision.findings)}"
    print(" [PASS] Missing evidence produces zero fabricated findings.")


def test_boilerplate_filtering_and_zero_synthetic_facts():
    """Adversarial Test 3: Boilerplate navigation text is discarded; no synthetic facts created."""
    print("\nTesting Adversarial Test 3: Boilerplate filtering and zero synthetic facts...")

    # Test boilerplate detector
    assert is_boilerplate("Skip to main content Sign in Menu ✕") is True
    assert is_boilerplate("Terms of service and privacy policy. All rights reserved.") is True
    assert is_boilerplate("Chapter 4.12 of the Santa Monica Municipal Code prohibits excessive noise after 10 PM.") is False

    raw_boilerplate_excerpt = "Skip to main content\n\nSign In Menu ✕\n\nHome\n\nCommercial filming requires a permit."
    extracted = extract_claims_from_excerpt(
        raw_excerpt=raw_boilerplate_excerpt,
        source_url="https://santamonica.gov/permits",
        source_title="Santa Monica Permits",
        category="filming_permits",
    )
    # "Skip to main content" and "Sign In Menu" must be rejected
    for f in extracted:
        assert "skip to main" not in f.claim.lower()
        assert "sign in" not in f.claim.lower()
        assert f.source_url.startswith("http")
    print(" [PASS] Navigation chrome cleanly discarded from extracted claims.")


def test_every_finding_retains_evidence_provenance():
    """Adversarial Test 4: Every RISK/BLOCKED finding MUST contain supporting evidence with valid source URLs."""
    print("\nTesting Adversarial Test 4: Every RISK finding contains supporting evidence with URL...")
    hazardous_scene = ExtractedScene(
        scene_id="SCENE_TEST_4",
        heading="EXT. SANTA MONICA PIER - NIGHT",
        interior_exterior="EXT",
        time_of_day="NIGHT",
        setting="public pier",
        requirements=["simulated blank gunfire", "drone tracking camera"],
        shoot_implications="Late night gunfire on wooden pier",
    )

    valid_facts = [
        ResearchFact(
            claim="Simulated gunfire and pyrotechnics require assignment of a State Fire Safety Officer (FSO).",
            source_url="https://film.ca.gov/production/production-safety",
            source_title="California Film Commission Safety",
            source_domain="film.ca.gov",
            evidence_text="Special effects, pyrotechnics, and projectile weapons mandate an assigned FSO.",
            category="regional_regulations",
        ),
        ResearchFact(
            claim="Santa Monica Municipal Code Chapter 4.12 establishes noise standards and quiet hours.",
            source_url="https://www.santamonica.gov/programs/noise",
            source_title="City of Santa Monica Noise",
            source_domain="santamonica.gov",
            evidence_text="Noise standards for nighttime activities in chapter 4.12.",
            category="location_restrictions",
        ),
    ]

    attached_evidence = build_scene_evidence(hazardous_scene, valid_facts)
    decision = evaluate_scene(hazardous_scene, attached_evidence)

    assert decision.decision in ("RISK", "BLOCKED")
    for f in decision.findings:
        assert len(f.supporting_evidence) > 0, f"Finding {f.finding_id} missing evidence"
        for ev in f.supporting_evidence:
            assert ev.source_url.startswith("http://") or ev.source_url.startswith("https://")
            assert len(ev.source_domain) > 0
    print(" [PASS] Complete provenance chain verified: Scene -> Requirement -> Evidence -> URL.")


def test_no_secrets_and_no_numeric_scores():
    """Adversarial Test 5: Verify no numeric feasibility scores or secrets exist."""
    print("\nTesting Adversarial Test 5: Absence of numeric feasibility scores and secrets...")
    dummy_scene = ExtractedScene(
        scene_id="SCENE_TEST_5",
        heading="INT. OFFICE - DAY",
        interior_exterior="INT",
        time_of_day="DAY",
        setting="office",
        requirements=["interview at desk"],
        shoot_implications="Routine interior",
    )
    decision = evaluate_scene(dummy_scene, [])
    dump_str = str(decision.model_dump())

    # Prohibited numeric patterns
    assert "score" not in decision.model_dump()
    assert "confidence_percentage" not in decision.model_dump()
    assert "feasibility_score" not in decision.model_dump()

    # Prohibited secret leaks
    if GEMINI_API_KEY:
        assert GEMINI_API_KEY not in dump_str
    if PARALLEL_API_KEY:
        assert PARALLEL_API_KEY not in dump_str
    print(" [PASS] Zero numeric scores and zero exposed secrets confirmed.")


if __name__ == "__main__":
    test_irrelevant_evidence_does_not_trigger_decision()
    test_missing_evidence_does_not_fabricate_blockers()
    test_boilerplate_filtering_and_zero_synthetic_facts()
    test_every_finding_retains_evidence_provenance()
    test_no_secrets_and_no_numeric_scores()
    print("\n>>> ALL ADVERSARIAL & NEGATIVE TESTS PASSED! <<<\n")
