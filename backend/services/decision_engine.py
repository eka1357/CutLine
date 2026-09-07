"""
Stage 4: Production Decision Engine
Deterministic, inspectable rule engine that evaluates scene requirements against verified evidence.
Strictly follows the contract:
Requirement -> Evidence -> Rule -> Consequence (GO / RISK / BLOCKED).
Zero numeric scores, zero confidence percentages.
Fully generalized across any city, region, or screenplay.
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


def deduplicate_evidence(evidence_list: list[EvidenceItem]) -> list[EvidenceItem]:
    """Helper to deduplicate evidence items by source URL for clean finding presentation."""
    seen_urls = set()
    unique = []
    for ev in evidence_list:
        if ev.source_url not in seen_urls:
            seen_urls.add(ev.source_url)
            unique.append(ev)
    return unique


# -----------------------------------------------------------------------------
# DETERMINISTIC BLOCKED RULES (Material Legal, Jurisdictional, or Physical Halts)
# -----------------------------------------------------------------------------

def evaluate_absolute_prohibition(
    scene: ExtractedScene,
    attached_evidence: list[EvidenceItem],
) -> Optional[DecisionFinding]:
    """
    Evaluates evidence for explicit legal moratoria or absolute prohibitions (BLOCKED).
    """
    prohibition_evidence = [
        ev for ev in attached_evidence
        if any(
            phrase in ev.evidence_text.lower()
            for phrase in [
                "strictly prohibited",
                "filming moratorium",
                "no commercial filming",
                "prohibited without exception",
                "closed to all production",
                "no-fly zone",
            ]
        )
    ]

    if not prohibition_evidence:
        return None

    prohibition_evidence = deduplicate_evidence(prohibition_evidence)
    primary_ev = prohibition_evidence[0]

    return DecisionFinding(
        finding_id=f"FINDING_{scene.scene_id}_PROHIBITION",
        scene_id=scene.scene_id,
        requirement_name=f"commercial filming at {scene.setting}",
        rule_name="Jurisdictional Commercial Filming Moratorium or Prohibition",
        rule_description=(
            "Commercial production activity or specified flight operations are legally banned "
            "under local jurisdictional statute without standard variance avenues."
        ),
        consequence="BLOCKED",
        reason=(
            f"Evidence from {primary_ev.source_domain} documents an explicit moratorium or legal prohibition: "
            f"'{primary_ev.claim[:180]}...'. Production cannot proceed as written at this location."
        ),
        supporting_evidence=prohibition_evidence,
    )


def evaluate_event_street_closure_blackout(
    scene: ExtractedScene,
    attached_evidence: list[EvidenceItem],
) -> Optional[DecisionFinding]:
    """
    Evaluates total access denial caused by city festivals, marathons, or street closures (BLOCKED / RISK).
    """
    if scene.interior_exterior != "EXT":
        return None

    closure_evidence = [
        ev for ev in attached_evidence
        if any(
            phrase in ev.evidence_text.lower()
            for phrase in [
                "street closure",
                "road closure",
                "closed to all traffic",
                "parade route",
                "marathon route",
            ]
        )
    ]

    if not closure_evidence:
        return None

    closure_evidence = deduplicate_evidence(closure_evidence)
    primary_ev = closure_evidence[0]

    # If the evidence explicitly mentions street/road closure on public route during the window
    return DecisionFinding(
        finding_id=f"FINDING_{scene.scene_id}_EVENT_CLOSURE",
        scene_id=scene.scene_id,
        requirement_name=f"public exterior filming at {scene.setting}",
        rule_name="Municipal Event Street Closure & Access Blackout",
        rule_description=(
            "Permitted public events, major parades, or civic festivals that mandate complete street closures "
            "prevent commercial production access and vehicle staging."
        ),
        consequence="BLOCKED",
        reason=(
            f"Evidence from {primary_ev.source_domain} documents an active street or venue closure during this window: "
            f"'{primary_ev.claim[:180]}...'. Physical access and standard traffic control are unavailable."
        ),
        supporting_evidence=closure_evidence,
    )


def evaluate_severe_weather_hazard(
    scene: ExtractedScene,
    attached_evidence: list[EvidenceItem],
) -> Optional[DecisionFinding]:
    """
    Evaluates extreme environmental closures, gale warnings, or evacuations (BLOCKED).
    """
    severe_evidence = [
        ev for ev in attached_evidence
        if any(
            term in ev.evidence_text.lower()
            for term in [
                "mandatory evacuation",
                "gale warning",
                "hurricane warning",
                "blizzard warning",
                "tsunami warning",
                "harbor closed",
            ]
        )
    ]

    if not severe_evidence:
        return None

    severe_evidence = deduplicate_evidence(severe_evidence)
    primary_ev = severe_evidence[0]

    return DecisionFinding(
        finding_id=f"FINDING_{scene.scene_id}_SEVERE_WEATHER_BLOCK",
        scene_id=scene.scene_id,
        requirement_name=f"exterior production in {scene.setting}",
        rule_name="Severe Environmental Hazard & Mandatory Closure Order",
        rule_description=(
            "Declared severe weather emergencies, gale warnings, or mandatory evacuation zones "
            "legally and physically suspend outdoor commercial production operations."
        ),
        consequence="BLOCKED",
        reason=(
            f"Evidence from {primary_ev.source_domain} documents extreme weather hazard: '{primary_ev.claim[:180]}...'. "
            f"Outdoor filming cannot safely or legally proceed."
        ),
        supporting_evidence=severe_evidence,
    )


# -----------------------------------------------------------------------------
# DETERMINISTIC RISK RULES (Operational Friction, Mandatory Permits, Personnel)
# -----------------------------------------------------------------------------

def evaluate_night_noise_curfew(
    scene: ExtractedScene,
    attached_evidence: list[EvidenceItem],
) -> Optional[DecisionFinding]:
    """
    Evaluates exterior nighttime noise ordinance and curfew constraints (RISK).
    """
    if scene.interior_exterior != "EXT" or scene.time_of_day not in ("NIGHT", "DUSK"):
        return None

    noise_evidence = [
        ev for ev in attached_evidence
        if any(
            term in ev.evidence_text.lower()
            for term in ["noise", "curfew", "ordinance", "night", "quiet hours", "sound standard"]
        )
    ]

    if not noise_evidence:
        return None

    noise_evidence = deduplicate_evidence(noise_evidence)
    primary_ev = noise_evidence[0]

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
            f"Verified evidence from {primary_ev.source_domain} documents municipal noise standards or curfews. "
            f"Filming during {scene.time_of_day} hours at a public {scene.setting} "
            f"requires formal after-hours variance permits and neighborhood notification."
        ),
        supporting_evidence=noise_evidence,
    )


def evaluate_special_effects_weapons(
    scene: ExtractedScene,
    attached_evidence: list[EvidenceItem],
) -> Optional[DecisionFinding]:
    """
    Evaluates pyrotechnic, blank gunfire, and weapon safety regulations (RISK).
    """
    req_text = " ".join(scene.requirements).lower()
    is_weapon_scene = any(
        term in req_text for term in ["gunfire", "blank", "weapon", "pyrotechnic", "muzzle", "revolver", "firearm"]
    )
    if not is_weapon_scene:
        return None

    weapons_evidence = [
        ev for ev in attached_evidence
        if any(
            term in ev.evidence_text.lower()
            for term in ["fire safety officer", "fso", "special effects", "pyrotechnic", "armorer", "safety protocol"]
        )
    ]

    if not weapons_evidence:
        return None

    weapons_evidence = deduplicate_evidence(weapons_evidence)
    primary_ev = weapons_evidence[0]

    return DecisionFinding(
        finding_id=f"FINDING_{scene.scene_id}_WEAPONS_SAFETY",
        scene_id=scene.scene_id,
        requirement_name="simulated gunfire / blank rounds discharge",
        rule_name="Mandatory Safety Personnel & Armorer Oversight for Weapons",
        rule_description=(
            "Simulated weapon discharge, pyrotechnics, and blank firing require dedicated "
            "licensed armorer oversight and certified Fire Safety Officer (FSO) assignments."
        ),
        consequence="RISK",
        reason=(
            f"Verified evidence from {primary_ev.source_domain} mandates that projectile special effects "
            f"and gunfire require licensed armorer supervision and designated safety officers."
        ),
        supporting_evidence=weapons_evidence,
    )


def evaluate_structural_load_limits(
    scene: ExtractedScene,
    attached_evidence: list[EvidenceItem],
) -> Optional[DecisionFinding]:
    """
    Evaluates pier, bridge, or historical structure load, cabling, and ballast rules (RISK).
    """
    setting_lower = scene.setting.lower()
    is_structural = any(term in setting_lower for term in ["pier", "bridge", "boardwalk", "dock"])
    if not is_structural:
        return None

    structural_evidence = [
        ev for ev in attached_evidence
        if any(
            term in ev.evidence_text.lower()
            for term in ["ballast", "deck", "load", "cabling", "plywood", "weight", "structural"]
        )
    ]

    if not structural_evidence:
        return None

    structural_evidence = deduplicate_evidence(structural_evidence)
    primary_ev = structural_evidence[0]

    return DecisionFinding(
        finding_id=f"FINDING_{scene.scene_id}_STRUCTURAL_LOAD",
        scene_id=scene.scene_id,
        requirement_name=f"heavy rigging / staging on {scene.setting}",
        rule_name="Historic Structure Load & Ballast Weighting Regulation",
        rule_description=(
            "Local authorities prohibit ground/deck penetration and enforce ballast weighting limits "
            "to protect timber decking or historic structural surfaces."
        ),
        consequence="RISK",
        reason=(
            f"Verified evidence from {primary_ev.source_domain} states that large equipment and staging "
            f"must utilize non-penetrating ballast distribution and approved surface protection."
        ),
        supporting_evidence=structural_evidence,
    )


def evaluate_permit_deadline(
    scene: ExtractedScene,
    attached_evidence: list[EvidenceItem],
) -> Optional[DecisionFinding]:
    """
    Evaluates municipal permit application lead-time requirements for public shoots (RISK).
    """
    if scene.interior_exterior != "EXT":
        return None

    permit_evidence = [
        ev for ev in attached_evidence
        if any(
            term in ev.evidence_text.lower()
            for term in ["business days", "deadline", "application", "turnaround", "lead time", "advance notice"]
        )
    ]

    if not permit_evidence:
        return None

    permit_evidence = deduplicate_evidence(permit_evidence)
    primary_ev = permit_evidence[0]

    return DecisionFinding(
        finding_id=f"FINDING_{scene.scene_id}_PERMIT_LEAD_TIME",
        scene_id=scene.scene_id,
        requirement_name=f"commercial filming permit for {scene.setting}",
        rule_name="Mandatory Municipal Permit Lead-Time Threshold",
        rule_description=(
            "Municipal film offices require applications and inter-agency coordination (police, fire) "
            "submitted in advance of the first shoot day."
        ),
        consequence="RISK",
        reason=(
            f"Verified evidence from {primary_ev.source_domain} specifies commercial applications must be submitted "
            f"in advance with municipal authority review. Compacting turnaround risks permit denial."
        ),
        supporting_evidence=permit_evidence,
    )


def evaluate_environmental_weather_hazard(
    scene: ExtractedScene,
    attached_evidence: list[EvidenceItem],
) -> Optional[DecisionFinding]:
    """
    Evaluates coastal surf, tidal surge, and weather advisories (RISK).
    """
    req_text = (" ".join(scene.requirements) + " " + scene.setting).lower()
    if not any(term in req_text for term in ["water", "tide", "surf", "ocean", "pier", "river"]):
        return None

    weather_evidence = [
        ev for ev in attached_evidence
        if any(
            term in ev.evidence_text.lower()
            for term in ["high surf", "coastal flood", "advisory", "swell", "tide surge", "wind gust"]
        )
    ]

    if not weather_evidence:
        return None

    weather_evidence = deduplicate_evidence(weather_evidence)
    primary_ev = weather_evidence[0]

    return DecisionFinding(
        finding_id=f"FINDING_{scene.scene_id}_TIDAL_SURF",
        scene_id=scene.scene_id,
        requirement_name="water and shoreline production safety",
        rule_name="Marine High Surf & Tidal Surge Advisory",
        rule_description=(
            "Active coastal advisories and tidal surges near structures introduce "
            "physical actor and equipment hazards during water-adjacent filming."
        ),
        consequence="RISK",
        reason=(
            f"Verified evidence from {primary_ev.source_domain} documents active marine/tidal advisories "
            f"during this window, requiring water safety crews and non-slip precautions."
        ),
        supporting_evidence=weather_evidence,
    )


# -----------------------------------------------------------------------------
# DETERMINISTIC GO RULES (Standard Production Clearance)
# -----------------------------------------------------------------------------

def evaluate_standard_interior(
    scene: ExtractedScene,
    attached_evidence: list[EvidenceItem],
    other_findings: list[DecisionFinding],
) -> Optional[DecisionFinding]:
    """
    Evaluates low-risk, controlled interior scenes where no blocking or high-friction rules fired (GO).
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
            f"street closures, or outdoor structural limitations. Standard private location agreement applies."
        ),
        supporting_evidence=attached_evidence,
    )


def evaluate_unconstrained_exterior(
    scene: ExtractedScene,
    attached_evidence: list[EvidenceItem],
    other_findings: list[DecisionFinding],
) -> Optional[DecisionFinding]:
    """
    Evaluates exterior scenes where no restrictive rules fired and no local prohibitions were found (GO).
    """
    if scene.interior_exterior != "EXT":
        return None

    if any(f.consequence in ("RISK", "BLOCKED") for f in other_findings):
        return None

    evidence_note = (
        "Retrieved evidence indicates no active moratoria, festival closures, or nighttime curfew conflicts."
        if attached_evidence
        else "No localized moratoria or severe hazards identified in retrieved evidence; standard permitting protocols apply."
    )

    return DecisionFinding(
        finding_id=f"FINDING_{scene.scene_id}_UNCONSTRAINED_EXT",
        scene_id=scene.scene_id,
        requirement_name=f"exterior filming at {scene.setting}",
        rule_name="Standard Exterior Commercial Production Protocol",
        rule_description=(
            "Exterior filming location without conflicting local moratoria, active street closures, "
            "or severe weather advisories operates under standard municipal permitting."
        ),
        consequence="GO",
        reason=(
            f"{evidence_note} Standard commercial filming permits and daytime production protocols apply for {scene.setting}."
        ),
        supporting_evidence=attached_evidence,
    )


# -----------------------------------------------------------------------------
# MASTER SCENE EVALUATOR
# -----------------------------------------------------------------------------

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

    # Priority 1: Check BLOCKED rules
    block_evaluators = [
        evaluate_absolute_prohibition,
        evaluate_event_street_closure_blackout,
        evaluate_severe_weather_hazard,
    ]
    for evaluator in block_evaluators:
        res = evaluator(scene, attached_evidence)
        if res:
            findings.append(res)

    # Priority 2: Check RISK rules
    risk_evaluators = [
        evaluate_night_noise_curfew,
        evaluate_special_effects_weapons,
        evaluate_structural_load_limits,
        evaluate_permit_deadline,
        evaluate_environmental_weather_hazard,
    ]
    for evaluator in risk_evaluators:
        res = evaluator(scene, attached_evidence)
        if res:
            findings.append(res)

    # Priority 3: Check GO rules (only if no RISK or BLOCKED findings)
    if not findings:
        if scene.interior_exterior == "INT":
            int_res = evaluate_standard_interior(scene, attached_evidence, findings)
            if int_res:
                findings.append(int_res)
        else:
            ext_res = evaluate_unconstrained_exterior(scene, attached_evidence, findings)
            if ext_res:
                findings.append(ext_res)

    # Determine overall scene verdict
    if any(f.consequence == "BLOCKED" for f in findings):
        verdict: DecisionStatusType = "BLOCKED"
        blocked_count = sum(1 for f in findings if f.consequence == "BLOCKED")
        summary = f"Scene {scene.scene_id} ({scene.heading}) is BLOCKED by {blocked_count} mandatory prohibition(s)."
    elif any(f.consequence == "RISK" for f in findings):
        verdict = "RISK"
        risk_count = sum(1 for f in findings if f.consequence == "RISK")
        summary = f"Scene {scene.scene_id} ({scene.heading}) carries {risk_count} operational RISK constraint(s) requiring mitigation."
    else:
        verdict = "GO"
        summary = f"Scene {scene.scene_id} ({scene.heading}) is cleared as GO under standard commercial production protocols."

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
