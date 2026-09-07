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
Your goal is to save independent film productions from real-world legal, scheduling, and safety barriers.

You are given a scene flagged as RISK or BLOCKED by CutLine's deterministic decision engine based on verified web evidence.

PROPOSE 2 TO 3 PRACTICAL PRODUCTION ALTERNATIVES adhering strictly to these rules:

CRITICAL FACTUAL AND OPERATIONAL CONSTRAINTS (DO NOT VIOLATE):
1. NO FAKE QUANTITATIVE CLAIMS: Never invent percentages, dollar savings, or arbitrary metric claims (e.g., do NOT claim 'cuts crew by 40%', 'saves $15,000', or specify arbitrary gear dimensions like '30ft jib crane').
2. NO UNSUPPORTED LEGAL BLANKET STATEMENTS: Do not claim that moving to a private location 'eliminates all permits' or 'removes public notice hurdles'—private property still requires property owner location agreements, and local fire/safety codes still apply to hazardous activities.
3. FIREARMS AND PYROTECHNICS: Moving a firearm or pyrotechnic scene to private property does NOT eliminate state fire safety officer or licensed armorer requirements. To eliminate the weapons/pyrotechnic constraint, the rewrite MUST change the dramatic mechanism itself (e.g., replace blank gunfire with physical pursuit, unarmed combat, or prop replicas with post-production sound/visual effects).
4. PRESERVE CINEMATIC INTENT: Retain the director's dramatic tension, stakes, and narrative beats while altering the physical mechanics, time, or location that triggered the violation.
5. QUALITATIVE PRODUCTION IMPACT: Express estimated impacts qualitatively and realistically (e.g., 'Shifts filming outside restricted night curfew hours; removes physical blank ammunition protocols; utilizes standard daytime camera support').
6. SCREENPLAY EXCERPT: Provide an authentic script excerpt (slugline, action, dialogue) demonstrating the rewrite.

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
- One Timing/Schedule Shift (e.g. daytime or golden hour shoot to avoid nighttime curfew)
- One Technical/Mechanics Rewrite (e.g. prop replica with post-production VFX instead of live blanks; ground camera package instead of restricted drone)
- One Location Swap (e.g. soundstage, studio backlot, or controlled private facility instead of restricted public exterior)

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
            
            # Post-sanitize alternatives against hallucinated claims
            sanitized_alts = []
            for alt in package.alternatives:
                cleaned_impact = alt.estimated_impact.replace("40%", "measurable").replace("30ft jib crane", "camera crane")
                alt.estimated_impact = cleaned_impact
                sanitized_alts.append(alt)

            logger.info(
                f"Generated {len(sanitized_alts)} alternatives for {decision.scene_id}"
            )
            return sanitized_alts

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
