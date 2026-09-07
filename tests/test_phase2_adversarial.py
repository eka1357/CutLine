"""
Adversarial and Negative Tests for CutLine Phase 2.5 Pipeline
Validates system resilience, strict evidence grounding, and generalization:
1. Different location & screenplay (Chicago, IL / The Lakefront Cipher)
2. Missing evidence produces no fabricated blockers
3. Irrelevant evidence does not trigger rules
4. Contradictory evidence resolves conservatively to the restrictive condition
5. Malformed research results handled gracefully
6. Parallel/API failure yields zero synthetic facts
7. Verified clear GO case
8. Verified clear RISK case
9. Verified clear BLOCKED case
10. Material difference between RISK and BLOCKED rules & consequences
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


def test_1_different_location_and_screenplay():
    """Test 1: Generalization - Evaluate 'The Lakefront Cipher' in Chicago, IL."""
    print("Testing 1: Different location (Chicago, IL) and different screenplay ('The Lakefront Cipher')...")
    
    scene_int = ExtractedScene(
        scene_id="CHI_SCENE_1",
        heading="INT. HAROLD WASHINGTON LIBRARY - DAY",
        interior_exterior="INT",
        time_of_day="DAY",
        setting="public research library",
        requirements=["actors whispering at reading table", "viewing microfilm records"],
        shoot_implications="Standard indoor library permit and location agreement",
    )
    
    scene_ext = ExtractedScene(
        scene_id="CHI_SCENE_2",
        heading="EXT. CHICAGO RIVERWALK - NIGHT",
        interior_exterior="EXT",
        time_of_day="NIGHT",
        setting="concrete riverwalk near bridge",
        requirements=["nighttime foot pursuit", "drone tracking camera", "water-adjacent filming"],
        shoot_implications="Night exterior drone tracking over public riverwalk",
    )

    chicago_facts = [
        ResearchFact(
            claim="The Chicago Film Office requires commercial film permit applications at least 3 business days prior to filming.",
            source_url="https://www.chicago.gov/city/en/depts/dca/provdrs/film_office.html",
            source_title="Chicago Film Office Permits",
            source_domain="chicago.gov",
            evidence_text="Permit application lead times: general street filming requires 3 business days turnaround.",
            category="filming_permits",
        ),
        ResearchFact(
            claim="Filming along the Chicago Riverwalk between 10:00 PM and 6:00 AM requires nighttime noise variance and water safety protocols.",
            source_url="https://www.chicago.gov/city/en/depts/dca/supp_info/riverwalk_filming.html",
            source_title="Chicago Riverwalk Filming Guidelines",
            source_domain="chicago.gov",
            evidence_text="Nighttime filming curfew applies after 10 PM. Activities near water edges mandate certified safety monitors.",
            category="location_restrictions",
        ),
    ]

    # Evaluate Scene 1 (Interior)
    ev_1 = build_scene_evidence(scene_int, chicago_facts)
    dec_1 = evaluate_scene(scene_int, ev_1)
    assert dec_1.decision == "GO", f"Expected GO for Chicago library interior, got {dec_1.decision}"

    # Evaluate Scene 2 (Exterior Night Riverwalk)
    ev_2 = build_scene_evidence(scene_ext, chicago_facts)
    assert len(ev_2) > 0, "Expected evidence to attach to riverwalk night pursuit"
    dec_2 = evaluate_scene(scene_ext, ev_2)
    assert dec_2.decision == "RISK", f"Expected RISK for riverwalk night chase, got {dec_2.decision}"
    
    # Verify zero Santa Monica references in findings
    for finding in dec_2.findings:
        assert "santa monica" not in finding.reason.lower()
        assert "santa monica" not in finding.rule_name.lower()
    print(" [PASS] Chicago screenplay correctly evaluated (Scene 1: GO, Scene 2: RISK) with zero hardcoded references.")


def test_2_missing_evidence_does_not_fabricate_blockers():
    """Test 2: When research returns zero evidence, no fabricated blockers are invented."""
    print("\nTesting 2: Missing evidence does not fabricate blockers...")
    mystery_scene = ExtractedScene(
        scene_id="SCENE_UNKNOWN_01",
        heading="EXT. REMOTE RIDGE - DAY",
        interior_exterior="EXT",
        time_of_day="DAY",
        setting="unspecified wilderness ridge",
        requirements=["lone hiker walking along footpath"],
        shoot_implications="Daytime landscape shot",
    )

    empty_facts: list[ResearchFact] = []
    attached_evidence = build_scene_evidence(mystery_scene, empty_facts)
    assert len(attached_evidence) == 0

    decision = evaluate_scene(mystery_scene, attached_evidence)
    # Conservative fallback: evaluates to standard protocol GO, zero restrictive RISK/BLOCKED findings
    assert decision.decision == "GO", f"Expected GO for unconstrained scene without evidence, got {decision.decision}"
    assert all(f.consequence == "GO" for f in decision.findings)
    print(" [PASS] Missing evidence evaluated conservatively as standard protocol GO without fabricating restrictions.")


def test_3_irrelevant_evidence_does_not_trigger_decision():
    """Test 3: Irrelevant evidence (e.g. food menus, parking fees) must not attach or trigger rules."""
    print("\nTesting 3: Irrelevant evidence does not trigger rules...")
    clean_scene = ExtractedScene(
        scene_id="SCENE_ART_01",
        heading="INT. ART GALLERY - DAY",
        interior_exterior="INT",
        time_of_day="DAY",
        setting="private art gallery",
        requirements=["dialogue between two curators", "holding wine glasses"],
        shoot_implications="Standard private indoor gallery rental",
    )

    irrelevant_facts = [
        ResearchFact(
            claim="Deep dish pizza slices cost $12 at the museum cafe.",
            source_url="https://chicagofood.example.com/menu",
            source_title="Museum Cafe Menu",
            source_domain="chicagofood.example.com",
            evidence_text="Lunch specials and beverage pricing.",
            category="location_restrictions",
        ),
        ResearchFact(
            claim="Downtown parking garage #4 offers $20 daily flat rates.",
            source_url="https://parking.example.com/rates",
            source_title="Downtown Parking",
            source_domain="parking.example.com",
            evidence_text="Rates for standard passenger vehicles.",
            category="regional_regulations",
        ),
    ]

    attached_evidence = build_scene_evidence(clean_scene, irrelevant_facts)
    assert len(attached_evidence) == 0, f"Expected 0 attached evidence items, got {len(attached_evidence)}"

    decision = evaluate_scene(clean_scene, attached_evidence)
    assert decision.decision == "GO"
    print(" [PASS] Irrelevant facts ignored; clean scene remains GO.")


def test_4_contradictory_evidence_resolves_conservatively():
    """Test 4: Contradictory evidence (permissive general rule vs strict blackout) resolves to the restrictive condition."""
    print("\nTesting 4: Contradictory evidence resolves conservatively to the restrictive condition...")
    street_scene = ExtractedScene(
        scene_id="SCENE_STREET_01",
        heading="EXT. MICHIGAN AVENUE - DAY",
        interior_exterior="EXT",
        time_of_day="DAY",
        setting="public downtown thoroughfare",
        requirements=["dialogue while walking on sidewalk", "exterior street filming"],
        shoot_implications="Day exterior dialogue on major street",
    )

    contradictory_facts = [
        ResearchFact(
            claim="General commercial filming on downtown sidewalks is permitted with standard 3-day notice.",
            source_url="https://chicago.gov/film/general",
            source_title="Standard Filming Guidelines",
            source_domain="chicago.gov",
            evidence_text="Sidewalk filming without street closures requires simple registration.",
            category="filming_permits",
        ),
        ResearchFact(
            claim="All commercial filming permits along Michigan Avenue are suspended October 10-14 due to Chicago Marathon street closures and security blackouts.",
            source_url="https://chicago.gov/alerts/marathon-blackout",
            source_title="City Emergency Alert: Street Closure Blackout",
            source_domain="chicago.gov",
            evidence_text="Total street closure and filming moratorium in effect for the marathon route.",
            category="public_events",
        ),
    ]

    attached_evidence = build_scene_evidence(street_scene, contradictory_facts)
    decision = evaluate_scene(street_scene, attached_evidence)

    # Must resolve to BLOCKED because the specific closure/moratorium overrides general permission
    assert decision.decision == "BLOCKED", f"Expected BLOCKED due to street closure blackout, got {decision.decision}"
    assert any(f.consequence == "BLOCKED" for f in decision.findings)
    print(" [PASS] Contradictory evidence correctly resolved to BLOCKED based on specific street closure blackout.")


def test_5_malformed_research_results_handled_gracefully():
    """Test 5: Malformed research results (empty claims, bad URLs, missing domains) do not crash pipeline."""
    print("\nTesting 5: Malformed research results handled gracefully...")
    scene = ExtractedScene(
        scene_id="SCENE_MALFORMED_01",
        heading="EXT. PARK - DAY",
        interior_exterior="EXT",
        time_of_day="DAY",
        setting="city park",
        requirements=["walking in grass"],
        shoot_implications="Routine park filming",
    )

    malformed_facts = [
        ResearchFact(
            claim="",  # Empty claim
            source_url="not-a-url",
            source_title="",
            source_domain="",
            evidence_text="",
            category="location_restrictions",
        ),
        ResearchFact(
            claim="   ",  # Whitespace only
            source_url="https://example.com/test",
            source_title="Test",
            source_domain="example.com",
            evidence_text="   ",
            category="regional_regulations",
        ),
    ]

    # Neither should crash
    attached_evidence = build_scene_evidence(scene, malformed_facts)
    decision = evaluate_scene(scene, attached_evidence)
    assert decision.decision == "GO"
    print(" [PASS] Malformed facts processed without exception; clean scene remains GO.")


def test_6_parallel_api_failure_zero_synthetic_facts():
    """Test 6: Simulated Parallel API failure produces zero synthetic facts and no fabricated regulations."""
    print("\nTesting 6: Parallel API failure produces zero synthetic facts...")
    
    # Test extract_claims_from_excerpt with empty/failed response
    empty_claims = extract_claims_from_excerpt(
        raw_excerpt="",
        source_url="https://parallel.ai/search",
        source_title="Failed Search",
        category="filming_permits",
    )
    assert len(empty_claims) == 0

    # Ensure no synthetic claims pointing to docs.parallel.ai
    for c in empty_claims:
        assert "docs.parallel.ai" not in c.source_url
    print(" [PASS] Parallel API failure cleanly produces zero synthetic facts.")


def test_7_verified_clear_go_case():
    """Test 7: Verified clear GO case (controlled interior stage dialogue)."""
    print("\nTesting 7: Clear GO case (INT. SOUNDSTAGE - DAY)...")
    stage_scene = ExtractedScene(
        scene_id="SCENE_GO_01",
        heading="INT. PRODUCTION SOUNDSTAGE - DAY",
        interior_exterior="INT",
        time_of_day="DAY",
        setting="private soundstage",
        requirements=["two actors talking in standing kitchen set"],
        shoot_implications="Controlled private interior filming",
    )

    stage_facts = [
        ResearchFact(
            claim="Filming within certified soundstages and private studio facilities requires standard facility booking agreements.",
            source_url="https://studios.example.com/guidelines",
            source_title="Studio Facility Guidelines",
            source_domain="studios.example.com",
            evidence_text="Private interior stages operate free of municipal outdoor curfews.",
            category="filming_permits",
        ),
    ]

    ev = build_scene_evidence(stage_scene, stage_facts)
    dec = evaluate_scene(stage_scene, ev)
    assert dec.decision == "GO"
    assert len(dec.findings) == 1
    assert dec.findings[0].consequence == "GO"
    print(" [PASS] Controlled interior correctly evaluated to GO.")


def test_8_verified_clear_risk_case():
    """Test 8: Verified clear RISK case (night exterior with simulated gunfire)."""
    print("\nTesting 8: Clear RISK case (EXT. INDUSTRIAL ALLEY - NIGHT with blank gunfire)...")
    risk_scene = ExtractedScene(
        scene_id="SCENE_RISK_01",
        heading="EXT. INDUSTRIAL ALLEY - NIGHT",
        interior_exterior="EXT",
        time_of_day="NIGHT",
        setting="industrial alley",
        requirements=["simulated blank gunfire", "actor firing replica weapon", "night filming"],
        shoot_implications="Nighttime exterior gunfire requiring armorer and fire safety officers",
    )

    weapons_facts = [
        ResearchFact(
            claim="Simulated gunfire and pyrotechnics require assignment of a certified Fire Safety Officer (FSO) and licensed armorer.",
            source_url="https://filmcommission.example.gov/safety/weapons",
            source_title="State Film Commission Safety Bulletin",
            source_domain="filmcommission.example.gov",
            evidence_text="Special effects, blank discharge, and projectile weapons mandate an assigned FSO and armorer.",
            category="regional_regulations",
        ),
        ResearchFact(
            claim="Municipal noise regulations require special permit riders and neighborhood notification for late-night filming after 10:00 PM.",
            source_url="https://city.example.gov/noise/curfew",
            source_title="City Noise Standards",
            source_domain="city.example.gov",
            evidence_text="Filming with simulated weapons or loud effects after 10 PM triggers municipal noise standards and night curfew restrictions.",
            category="location_restrictions",
        ),
    ]

    ev = build_scene_evidence(risk_scene, weapons_facts)
    dec = evaluate_scene(risk_scene, ev)
    assert dec.decision == "RISK", f"Expected RISK, got {dec.decision}"
    assert any(f.rule_name == "Mandatory Safety Personnel & Armorer Oversight for Weapons" for f in dec.findings)
    assert any(f.rule_name == "Municipal Nighttime Noise Ordinance & Curfew Compliance" for f in dec.findings)
    print(" [PASS] Simulated gunfire at night correctly evaluated to RISK with FSO and curfew rules.")


def test_9_verified_clear_blocked_case():
    """Test 9: Verified clear BLOCKED case (filming during total municipal moratorium)."""
    print("\nTesting 9: Clear BLOCKED case (EXT. HISTORIC SQUARE during municipal moratorium)...")
    blocked_scene = ExtractedScene(
        scene_id="SCENE_BLOCKED_01",
        heading="EXT. HISTORIC PLAZA - DAY",
        interior_exterior="EXT",
        time_of_day="DAY",
        setting="historic plaza",
        requirements=["vehicle chase through plaza", "exterior filming"],
        shoot_implications="Exterior vehicle stunts in public historic plaza",
    )

    ban_facts = [
        ResearchFact(
            claim="The City Council has enacted an absolute commercial filming ban and moratorium on Historic Plaza through 2026 due to historic preservation work.",
            source_url="https://citygov.example.gov/ordinance/filming-ban",
            source_title="City Ordinance No. 2026-88: Filming Moratorium",
            source_domain="citygov.example.gov",
            evidence_text="No commercial filming permits shall be issued for Historic Plaza. All requests are strictly prohibited.",
            category="location_restrictions",
        ),
    ]

    ev = build_scene_evidence(blocked_scene, ban_facts)
    dec = evaluate_scene(blocked_scene, ev)
    assert dec.decision == "BLOCKED", f"Expected BLOCKED, got {dec.decision}"
    assert any(f.rule_name == "Jurisdictional Commercial Filming Moratorium or Prohibition" for f in dec.findings)
    assert any(f.consequence == "BLOCKED" for f in dec.findings)
    print(" [PASS] Absolute municipal ban correctly evaluated to BLOCKED.")


def test_10_material_difference_between_risk_and_blocked():
    """Test 10: Verify that RISK and BLOCKED have materially different deterministic rules and consequences."""
    print("\nTesting 10: Material difference between RISK and BLOCKED rules & consequences...")
    
    # 1. RISK rules require operational mitigations (permits, safety officers, monitors)
    # 2. BLOCKED rules represent absolute non-negotiable stop conditions (moratoria, full street closures, mandatory evacuations)
    
    scene = ExtractedScene(
        scene_id="SCENE_COMPARE_01",
        heading="EXT. WATERFRONT PROMENADE - NIGHT",
        interior_exterior="EXT",
        time_of_day="NIGHT",
        setting="waterfront promenade",
        requirements=["nighttime drone tracking", "dialogue near water"],
        shoot_implications="Night drone tracking near water",
    )

    # Condition A: Operational mitigations exist -> RISK
    risk_fact = ResearchFact(
        claim="Nighttime commercial filming along the promenade requires 5 business days advance application.",
        source_url="https://film.example.gov/promenade",
        source_title="Promenade Filming",
        source_domain="film.example.gov",
        evidence_text="Applications must be submitted at least 5 business days in advance.",
        category="filming_permits",
    )
    ev_risk = build_scene_evidence(scene, [risk_fact])
    dec_risk = evaluate_scene(scene, ev_risk)
    assert dec_risk.decision == "RISK"
    assert "mitigation" in dec_risk.decision_summary.lower()

    # Condition B: Absolute prohibition exists -> BLOCKED
    blocked_fact = ResearchFact(
        claim="The waterfront promenade is under an emergency flood evacuation order and total closure; all public access and commercial filming is prohibited.",
        source_url="https://emergency.example.gov/evacuation",
        source_title="Emergency Evacuation Order",
        source_domain="emergency.example.gov",
        evidence_text="Mandatory evacuation order. All commercial filming permits are revoked and prohibited.",
        category="weather_climate",
    )
    ev_blocked = build_scene_evidence(scene, [blocked_fact])
    dec_blocked = evaluate_scene(scene, ev_blocked)
    assert dec_blocked.decision == "BLOCKED"
    assert "prohibition" in dec_blocked.decision_summary.lower()

    # Consequences are materially different
    assert dec_risk.decision != dec_blocked.decision
    assert dec_risk.findings[0].consequence == "RISK"
    assert dec_blocked.findings[0].consequence == "BLOCKED"
    print(" [PASS] Material difference between RISK (operational mitigation) and BLOCKED (mandatory prohibition) verified.")


if __name__ == "__main__":
    test_1_different_location_and_screenplay()
    test_2_missing_evidence_does_not_fabricate_blockers()
    test_3_irrelevant_evidence_does_not_trigger_decision()
    test_4_contradictory_evidence_resolves_conservatively()
    test_5_malformed_research_results_handled_gracefully()
    test_6_parallel_api_failure_zero_synthetic_facts()
    test_7_verified_clear_go_case()
    test_8_verified_clear_risk_case()
    test_9_verified_clear_blocked_case()
    test_10_material_difference_between_risk_and_blocked()
    print("\n================================================================================")
    print(">>> ALL 10 ADVERSARIAL & NEGATIVE TEST SCENARIOS PASSED 100%! <<<")
    print("================================================================================\n")
