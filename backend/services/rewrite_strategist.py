"""
Stage 5: Rewrite Strategist
Calls Gemini (google-genai SDK) ONLY for RISK and BLOCKED scenes to propose
2-3 concrete, production-aware alternatives that preserve cinematic intent
while eliminating the blocking constraint.
"""

import logging
from google import genai
from google.genai import types

from backend.config import GEMINI_API_KEY, DEFAULT_GEMINI_MODEL, FALLBACK_GEMINI_MODELS
from backend.schemas import (
    SceneProductionDecision,
    ProductionAlternative,
    SceneRewritePackage,
)

logger = logging.getLogger("cutline.rewrite_strategist")


REWRITE_SYSTEM_PROMPT = """
You are CutLine's elite Production Rewrite Strategist and Line Producer.
Your goal is to save productions from real-world legal, scheduling, and safety disasters.

You will be given a screenplay scene that has been flagged as RISK or BLOCKED by CutLine's
evidence engine based on real municipal rules, noise curfews, tide hazards, or permit lead-times.

Your job is NOT to write generic creative prose. Your job is to propose 2 to 3 CONCRETE,
PRODUCTION-AWARE ALTERNATIVES that:
1. Preserve the director's cinematic, dramatic, and tonal intent (the thrill, stakes, visual punch).
2. Remove or bypass the specific blocking production constraint (curfew, blank gunfire, wave hazards).
3. Specify the exact production mechanism change (crew, camera rig, time, or location swap).
4. Provide a concrete rewritten screenplay draft excerpt (slugline, action, dialogue) demonstrating the fix.

Output must adhere strictly to the JSON schema.
"""


def generate_scene_alternatives(
    decision: SceneProductionDecision,
    location: str,
) -> list[ProductionAlternative]:
    """
    Generates 2-3 production-aware alternatives for a RISK or BLOCKED scene using Gemini.
    Never runs for GO scenes.
    """
    if decision.decision == "GO":
        return []

    client = genai.Client(api_key=GEMINI_API_KEY)

    # Format findings and evidence into a clear briefing for Gemini
    findings_brief = []
    for f in decision.findings:
        evidence_citations = [f"- {e.claim} (Source: {e.source_domain})" for e in f.supporting_evidence]
        citations_str = "\n".join(evidence_citations) if evidence_citations else "None"
        findings_brief.append(
            f"RULE TRIGGERED: {f.rule_name} [{f.consequence}]\n"
            f"REASON: {f.reason}\n"
            f"SUPPORTING EVIDENCE:\n{citations_str}"
        )
    findings_text = "\n\n".join(findings_brief)

    user_prompt = f"""
TARGET LOCATION: {location}
AFFECTED SCENE: {decision.scene_id} — {decision.heading}
SETTING: {decision.setting}
INTERIOR/EXTERIOR: {decision.interior_exterior} | TIME: {decision.time_of_day}
REQUIREMENTS: {', '.join(decision.requirements)}

FLAGGED PRODUCTION CONSTRAINTS & EVIDENCE:
{findings_text}

Generate 2 to 3 distinct strategic alternatives:
- One Timing/Schedule Shift (e.g. dawn/dusk blue hour instead of midnight curfew)
- One Technical/Mechanics Rewrite (e.g. camera crane or gimbal on deck instead of drone; replica weapon + VFX flash instead of live blanks)
- One Location Swap (e.g. private marina/dock instead of public boardwalk)

Ensure each alternative includes a concrete screenplay excerpt.
"""

    models_to_try = [DEFAULT_GEMINI_MODEL] + [
        m for m in FALLBACK_GEMINI_MODELS if m != DEFAULT_GEMINI_MODEL
    ]

    for model_name in models_to_try:
        try:
            logger.info(f"Generating rewrite alternatives for {decision.scene_id} using {model_name}")
            response = client.models.generate_content(
                model=model_name,
                contents=f"{REWRITE_SYSTEM_PROMPT}\n\n{user_prompt}",
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=SceneRewritePackage,
                    temperature=0.3,
                ),
            )

            package = SceneRewritePackage.model_validate_json(response.text)
            logger.info(
                f"Generated {len(package.alternatives)} alternatives for {decision.scene_id}"
            )
            return package.alternatives

        except Exception as e:
            logger.warning(f"Rewrite strategist failed with model {model_name}: {e}")

    logger.error(f"Failed to generate alternatives for {decision.scene_id} across all models")
    return []


def run_rewrite_strategist(
    decisions: list[SceneProductionDecision],
    location: str,
) -> list[SceneProductionDecision]:
    """
    Runs the Rewrite Strategist across all scenes, modifying decisions in-place with alternatives.
    Only queries Gemini for RISK/BLOCKED scenes.
    """
    updated_decisions: list[SceneProductionDecision] = []

    for dec in decisions:
        if dec.decision in ("RISK", "BLOCKED"):
            alternatives = generate_scene_alternatives(dec, location=location)
            dec.alternatives = alternatives
        else:
            dec.alternatives = []
        updated_decisions.append(dec)

    return updated_decisions
