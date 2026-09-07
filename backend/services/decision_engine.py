"""
Stage 4: Production Decision Engine
Deterministic, inspectable rule engine that evaluates scene requirements against verified evidence.
Strictly follows the contract:
Requirement -> Evidence -> Rule -> Consequence (GO / RISK / BLOCKED).
Zero numeric scores, zero confidence percentages.
"""

import logging
from typing import Optional

from backend.schemas import (
    ExtractedScene,
    EvidenceItem,
    DecisionFinding,
    SceneProductionDecision,
    DecisionStatusType,
)

logger = logging.getLogger("cutline.decision_engine")


def evaluate_night_noise_curfew(
    scene: ExtractedScene,
    attached_evidence: list[EvidenceItem],
) -> Optional[DecisionFinding]:
    """
    Evaluates exterior nighttime noise ordinance and curfew constraints.
    """
    if scene.interior_exterior != "EXT" or scene.time_of_day not in ("NIGHT", "DUSK"):
        return None

    noise_evidence = [
        ev for ev in attached_evidence
        if any(term in ev.evidence_text.lower() for term in ["noise", "curfew", "chapter 4.12", "ordinance", "night"])
    ]

    if not noise_evidence:
        return None

    return DecisionFinding(
        finding_id=f"FINDING_{scene.scene_id}_NOISE_CURFEW",
        scene_id=scene.scene_id,
        requirement_name=f"exterior night filming at {scene.setting}",
        rule_name="Municipal Nighttime Noise Ordinance & Curfew Compliance",
        rule_description=(
            "Commercial filming during late-night hours on public property is governed by municipal noise "
            "thresholds and sound curfews, requiring specialized variances and neighborhood notification."
        ),
        consequence="RISK",
        reason=(
            f"Verified evidence from {noise_evidence[0].source_domain} documents municipal noise standards "
            f"(e.g. Santa Monica Municipal Code Chapter 4.12). Filming at {scene.time_of_day} on a public {scene.setting} "
            f"exceeds standard hours and requires formal after-hours variance approval."
        ),
        supporting_evidence=noise_evidence,
    )


def evaluate_special_effects_weapons(
    scene: ExtractedScene,
    attached_evidence: list[EvidenceItem],
) -> Optional[DecisionFinding]:
    """
    Evaluates pyrotechnic, blank gunfire, and weapon safety regulations.
    """
    req_text = " ".join(scene.requirements).lower()
    is_weapon_scene = any(
        term in req_text for term in ["gunfire", "blank", "weapon", "pyrotechnic", "muzzle", "revolver"]
    )
    if not is_weapon_scene:
        return None

    weapons_evidence = [
        ev for ev in attached_evidence
        if any(term in ev.evidence_text.lower() for term in ["fire safety officer", "fso", "special effects", "pyrotechnic", "safety"])
    ]

    if not weapons_evidence:
        return None

    return DecisionFinding(
        finding_id=f"FINDING_{scene.scene_id}_WEAPONS_SAFETY",
        scene_id=scene.scene_id,
        requirement_name="simulated gunfire / blank rounds discharge",
        rule_name="State Fire Safety Officer & Armorer Mandate for Weapons",
        rule_description=(
            "Simulated weapon discharge, pyrotechnics, and blank firing require dedicated "
            "licensed armorer oversight and certified Fire Safety Officer (FSO) assignments."
        ),
        consequence="RISK",
        reason=(
            f"Verified evidence from {weapons_evidence[0].source_domain} mandates that projectile effects "
            f"and gunfire warrant assignment of a Fire Safety Officer (FSO) and strict Cal/OSHA safety protocols."
        ),
        supporting_evidence=weapons_evidence,
    )


def evaluate_pier_structural_limits(
    scene: ExtractedScene,
    attached_evidence: list[EvidenceItem],
) -> Optional[DecisionFinding]:
    """
    Evaluates pier/boardwalk structural load, cabling, and ballast rules.
    """
    if "pier" not in scene.setting.lower():
        return None

    pier_evidence = [
        ev for ev in attached_evidence
        if any(term in ev.evidence_text.lower() for term in ["ballast", "deck", "pacpark", "cabling", "plywood"])
    ]

    if not pier_evidence:
        return None

    return DecisionFinding(
        finding_id=f"FINDING_{scene.scene_id}_PIER_LOAD",
        scene_id=scene.scene_id,
        requirement_name=f"heavy rigging / staging on {scene.setting}",
        rule_name="Pier Deck Structural Load & Ballast Regulation",
        rule_description=(
            "Pier authorities prohibit deck drilling and enforce strict ballast weighting limits "
            "using water containers on plywood distribution to protect historical timber decking."
        ),
        consequence="RISK",
        reason=(
            f"Verified evidence from {pier_evidence[0].source_domain} states that large staging and equipment "
            f"must utilize approved water container ballast and distribution decking rather than standard penetration rigging."
        ),
        supporting_evidence=pier_evidence,
    )


def evaluate_permit_deadline(
    scene: ExtractedScene,
    attached_evidence: list[EvidenceItem],
) -> Optional[DecisionFinding]:
    """
    Evaluates municipal permit application lead-time requirements for public shoots.
    """
    if scene.interior_exterior != "EXT":
        return None

    permit_evidence = [
        ev for ev in attached_evidence
        if any(term in ev.evidence_text.lower() for term in ["5 business days", "application", "film santa monica", "turnaround", "lead time"])
    ]

    if not permit_evidence:
        return None

    return DecisionFinding(
        finding_id=f"FINDING_{scene.scene_id}_PERMIT_LEAD_TIME",
        scene_id=scene.scene_id,
        requirement_name=f"commercial filming permit for {scene.setting}",
        rule_name="Mandatory Municipal Permit Lead-Time Threshold",
        rule_description=(
            "Municipal film offices require applications and inter-agency coordination (police, fire) "
            "submitted well in advance of the first shoot day."
        ),
        consequence="RISK",
        reason=(
            f"Verified evidence from {permit_evidence[0].source_domain} specifies applications must be submitted "
            f"at least 5 business days prior to filming with fire department notification. Compacting this timeline risks permit refusal."
        ),
        supporting_evidence=permit_evidence,
    )


def evaluate_environmental_weather_hazard(
    scene: ExtractedScene,
    attached_evidence: list[EvidenceItem],
) -> Optional[DecisionFinding]:
    """
    Evaluates weather, tide, and high surf advisories.
    """
    req_text = (" ".join(scene.requirements) + " " + scene.setting).lower()
    if not any(term in req_text for term in ["water", "tide", "surf", "ocean", "pier"]):
        return None

    weather_evidence = [
        ev for ev in attached_evidence
        if any(term in ev.evidence_text.lower() for term in ["high surf", "coastal flood", "advisory", "tide", "gust", "swell"])
    ]

    if not weather_evidence:
        return None

    return DecisionFinding(
        finding_id=f"FINDING_{scene.scene_id}_TIDAL_SURF",
        scene_id=scene.scene_id,
        requirement_name="coastal tide and shoreline safety",
        rule_name="Coastal Marine High Surf & Tidal Hazard Advisory",
        rule_description=(
            "Active coastal advisories and strong tidal surges near pilings introduce "
            "physical actor and equipment hazards during water-adjacent filming."
        ),
        consequence="RISK",
        reason=(
            f"Verified evidence from {weather_evidence[0].source_domain} documents active coastal high surf/flood advisories "
            f"during this window, which threatens nighttime safety on wet, algae-slick pier planks."
        ),
        supporting_evidence=weather_evidence,
    )


def evaluate_standard_interior(
    scene: ExtractedScene,
    attached_evidence: list[EvidenceItem],
    other_findings: list[DecisionFinding],
) -> Optional[DecisionFinding]:
    """
    Evaluates low-risk, standard interior scenes where no blocking or high-friction rules fired.
    """
    if scene.interior_exterior != "INT":
        return None

    # If any other rule triggered a risk or blocker, do not evaluate as standard GO
    if any(f.consequence in ("RISK", "BLOCKED") for f in other_findings):
        return None

    return DecisionFinding(
        finding_id=f"FINDING_{scene.scene_id}_CONTROLLED_INT",
        scene_id=scene.scene_id,
        requirement_name=f"interior shoot at {scene.setting}",
        rule_name="Controlled Interior Standard Production Feasibility",
        rule_description=(
            "Private interior filming without hazardous pyrotechnics, street closures, or public curfews "
            "operates within standard commercial production parameters."
        ),
        consequence="GO",
        reason=(
            f"Controlled interior filming in a {scene.setting} is free of municipal noise curfew restrictions, "
            f"ocean hazards, or structural deck limitations. Routine private location agreement and standard interior permit suffice."
        ),
        supporting_evidence=attached_evidence,
    )


def evaluate_scene(
    scene: ExtractedScene,
    attached_evidence: list[EvidenceItem],
) -> SceneProductionDecision:
    """
    Deterministically evaluates all rules for a single scene.
    Outputs exactly one of: GO, RISK, BLOCKED.
    Never outputs a numeric score or percentage.
    """
    findings: list[DecisionFinding] = []

    # Run deterministic rule evaluators
    evaluators = [
        evaluate_night_noise_curfew,
        evaluate_special_effects_weapons,
        evaluate_pier_structural_limits,
        evaluate_permit_deadline,
        evaluate_environmental_weather_hazard,
    ]

    for evaluator in evaluators:
        res = evaluator(scene, attached_evidence)
        if res:
            findings.append(res)

    # If no risk/blocker findings on an interior scene, check standard interior rule
    int_finding = evaluate_standard_interior(scene, attached_evidence, findings)
    if int_finding:
        findings.append(int_finding)

    # Determine overall scene verdict
    if any(f.consequence == "BLOCKED" for f in findings):
        verdict: DecisionStatusType = "BLOCKED"
        summary = f"Scene {scene.scene_id} ({scene.heading}) is BLOCKED by municipal or safety prohibitions."
    elif any(f.consequence == "RISK" for f in findings):
        verdict = "RISK"
        risk_count = sum(1 for f in findings if f.consequence == "RISK")
        summary = f"Scene {scene.scene_id} ({scene.heading}) carries {risk_count} operational RISK constraint(s) requiring mitigation."
    else:
        verdict = "GO"
        summary = f"Scene {scene.scene_id} ({scene.heading}) is cleared as GO under standard production protocols."

    logger.info(f"Decision Engine evaluated {scene.scene_id}: {verdict} ({len(findings)} findings)")

    return SceneProductionDecision(
        scene_id=scene.scene_id,
        heading=scene.heading,
        interior_exterior=scene.interior_exterior,
        time_of_day=scene.time_of_day,
        setting=scene.setting,
        requirements=scene.requirements,
        shoot_implications=scene.shoot_implications,
        decision=verdict,
        decision_summary=summary,
        findings=findings,
        attached_evidence=attached_evidence,
        alternatives=[],  # Populated downstream by Stage 5 Rewrite Strategist
    )


def run_decision_engine(
    scenes: list[ExtractedScene],
    evidence_by_scene: dict[str, list[EvidenceItem]],
) -> list[SceneProductionDecision]:
    """
    Evaluates all scenes deterministically against their attached evidence.
    """
    decisions: list[SceneProductionDecision] = []
    for scene in scenes:
        scene_evidence = evidence_by_scene.get(scene.scene_id, [])
        dec = evaluate_scene(scene, scene_evidence)
        decisions.append(dec)
    return decisions
