"""
Stage 3: Evidence Engine
Semantically connects individual screenplay scene requirements to verified Parallel research facts.
Preserves the unbroken provenance chain:
Scene -> Requirement -> Evidence -> Source URL.
"""

import logging
import re
from typing import Optional

from backend.schemas import (
    ExtractedScene,
    ResearchFact,
    EvidenceItem,
    EvidenceStrengthType,
)

logger = logging.getLogger("cutline.evidence_engine")


# Semantic concept profiles linking production domains to evidence patterns
SEMANTIC_PROFILES = {
    "drone_airspace": {
        "requirement_keywords": [r"\bdrone\b", r"\buav\b", r"\baerial\b", r"\bquadcopter\b"],
        "evidence_keywords": [r"\bdrone\b", r"\bcommercial filming\b", r"\bpublic property\b", r"\bfaa\b", r"\bairspace\b", r"\bpermit\b"],
        "min_evidence_matches": 1,
        "default_strength": "direct",
        "explanation": "Evidence establishes municipal/airspace filming rules governing unmanned aerial systems and public property capture.",
    },
    "night_curfew_noise": {
        "requirement_keywords": [r"\bnight\b", r"\bcurfew\b", r"\blighting\b", r"\bnoise\b", r"\b1:30\b", r"\blate\b"],
        "evidence_keywords": [r"\bnoise\b", r"\bcurfew\b", r"\bordinance\b", r"\bchapter 4\.12\b", r"\bnight\b", r"\bhours\b", r"\bquiet\b"],
        "min_evidence_matches": 2,
        "default_strength": "direct",
        "explanation": "Evidence establishes local noise standards and curfew restrictions affecting late-night exterior production.",
    },
    "pyrotechnics_and_weapons": {
        "requirement_keywords": [r"\bgunfire\b", r"\bblank\b", r"\bweapon\b", r"\bexplos\w*\b", r"\bpyro\w*\b", r"\bmuzzle\b", r"\bsidearm\b", r"\brevolver\b"],
        "evidence_keywords": [r"\bspecial effects\b", r"\bpyrotechnic\w*\b", r"\bfire safety officer\b", r"\bfso\b", r"\bfire\b", r"\bpolice\b", r"\bsafety\b", r"\bcal/osha\b"],
        "min_evidence_matches": 1,
        "default_strength": "direct",
        "explanation": "Evidence mandates dedicated safety personnel (Fire Safety Officer / Armorer) for simulated weapon discharges and special effects.",
    },
    "pier_structural_deck_limits": {
        "requirement_keywords": [r"\bpier\b", r"\bdeck\b", r"\bplank\b", r"\bboardwalk\b", r"\bcrane\b", r"\brig\b"],
        "evidence_keywords": [r"\bballast\b", r"\bdeck\b", r"\bpier\b", r"\bpacpark\b", r"\bamusement park\b", r"\bcabling\b", r"\bplywood\b", r"\bload\b"],
        "min_evidence_matches": 2,
        "default_strength": "direct",
        "explanation": "Evidence specifies structural deck load, ballast containment, and cabling limitations on the wooden pier structure.",
    },
    "marine_weather_tidal_hazard": {
        "requirement_keywords": [r"\bwater\b", r"\btide\b", r"\bsurf\b", r"\bocean\b", r"\bwave\b", r"\bcoastal\b"],
        "evidence_keywords": [r"\bcoastal flood\b", r"\bhigh surf\b", r"\badvisory\b", r"\bswell\b", r"\bwind\b", r"\bgust\b", r"\btide\b", r"\bfog\b"],
        "min_evidence_matches": 1,
        "default_strength": "direct",
        "explanation": "Evidence documents coastal marine advisories and tide surges hazardous to shoreline and under-pier activity.",
    },
    "public_event_conflict": {
        "requirement_keywords": [r"\bpublic\b", r"\bexterior\b", r"\bstreet\b", r"\bpier\b", r"\bchase\b"],
        "evidence_keywords": [r"\bfarmers market\b", r"\bclosure\b", r"\bfestival\b", r"\bparade\b", r"\bcelebration\b", r"\bworld cup\b", r"\bcoast\b"],
        "min_evidence_matches": 1,
        "default_strength": "contextual",
        "explanation": "Evidence identifies public festivals, markets, or municipal street closures that conflict with production logistics.",
    },
    "municipal_permit_timeline": {
        "requirement_keywords": [r"\bpermit\b", r"\bmunicipal\b", r"\bpublic\b", r"\bclearance\b"],
        "evidence_keywords": [r"\b5 business days\b", r"\bapplication\b", r"\bportal\b", r"\bfilmsantamonica\b", r"\bturnaround\b", r"\blead time\b"],
        "min_evidence_matches": 1,
        "default_strength": "direct",
        "explanation": "Evidence establishes official municipal filing deadlines and agency notification turnaround timelines.",
    },
}


def matches_profile(
    scene: ExtractedScene,
    requirement_str: str,
    fact: ResearchFact,
    profile_name: str,
) -> Optional[tuple[EvidenceStrengthType, str]]:
    """
    Evaluates whether a specific fact semantically supports a scene requirement
    under the specified profile rules.
    """
    profile = SEMANTIC_PROFILES[profile_name]
    req_combined = f"{requirement_str} {scene.setting} {scene.interior_exterior} {scene.time_of_day} {scene.shoot_implications}".lower()
    evidence_combined = f"{fact.claim} {fact.evidence_text} {fact.source_title}".lower()

    # Step 1: Check requirement relevance
    req_matched = any(
        re.search(pat, req_combined) for pat in profile["requirement_keywords"]
    )
    if not req_matched:
        return None

    # Step 2: Check evidence text matches
    matched_ev_count = sum(
        1 for pat in profile["evidence_keywords"] if re.search(pat, evidence_combined)
    )
    if matched_ev_count < profile["min_evidence_matches"]:
        return None

    strength: EvidenceStrengthType = profile.get("default_strength", "direct")  # type: ignore
    return strength, profile["explanation"]


def build_scene_evidence(
    scene: ExtractedScene,
    research_facts: list[ResearchFact],
) -> list[EvidenceItem]:
    """
    Maps research facts to a scene's individual requirements.
    Never manufactures evidence. Every item retains its source URL and domain.
    """
    scene_evidence: list[EvidenceItem] = []
    seen_urls: set[str] = set()
    evidence_counter = 1

    # Combine explicit requirements with setting/environmental implications
    requirements_to_check = list(scene.requirements)
    if scene.interior_exterior == "EXT":
        requirements_to_check.append(f"exterior location filming at {scene.setting}")
    if scene.time_of_day in ("NIGHT", "DUSK"):
        requirements_to_check.append(f"night filming schedule ({scene.time_of_day})")

    for req in requirements_to_check:
        for fact in research_facts:
            if fact.source_url in seen_urls:
                continue

            for profile_name in SEMANTIC_PROFILES:
                match_result = matches_profile(scene, req, fact, profile_name)
                if match_result:
                    strength, explanation = match_result
                    seen_urls.add(fact.source_url)

                    evidence_item = EvidenceItem(
                        evidence_id=f"EVID_{scene.scene_id}_{evidence_counter}",
                        scene_id=scene.scene_id,
                        requirement_name=req,
                        category=fact.category,
                        claim=fact.claim,
                        source_url=fact.source_url,
                        source_title=fact.source_title,
                        source_domain=fact.source_domain,
                        evidence_text=fact.evidence_text or fact.claim,
                        relevance_explanation=explanation,
                        strength=strength,
                    )
                    scene_evidence.append(evidence_item)
                    evidence_counter += 1
                    break  # Matched one profile for this fact

    logger.info(
        f"Evidence Engine attached {len(scene_evidence)} verified evidence items to {scene.scene_id}"
    )
    return scene_evidence


def build_complete_evidence_map(
    scenes: list[ExtractedScene],
    research_facts: list[ResearchFact],
) -> tuple[dict[str, list[EvidenceItem]], list[EvidenceItem]]:
    """
    Builds the complete evidence map across all scenes.
    Returns (map_by_scene_id, all_evidence_flat).
    """
    by_scene: dict[str, list[EvidenceItem]] = {}
    flat_all: list[EvidenceItem] = []

    for scene in scenes:
        evidence_list = build_scene_evidence(scene, research_facts)
        by_scene[scene.scene_id] = evidence_list
        flat_all.extend(evidence_list)

    return by_scene, flat_all
