"""
Stage 2: Parallel Research Agent
Executes targeted web research via the official parallel-web SDK across
exactly 5 canonical production categories.
"""

import logging
import re
from typing import Callable, Optional
from parallel import Parallel

from backend.config import PARALLEL_API_KEY, RESEARCH_CATEGORIES
from backend.schemas import ResearchFact, ResearchResult, ResearchCategoryType

logger = logging.getLogger("cutline.parallel_researcher")


import urllib.parse

# Common boilerplate phrases found in raw web page headers/navigation
BOILERPLATE_PATTERNS = [
    r"skip to main content",
    r"sign in",
    r"terms of service",
    r"privacy policy",
    r"cookie policy",
    r"all rights reserved",
    r"menu \u2715",
    r"search form search",
]


def is_boilerplate(text: str) -> bool:
    """Detect and filter out web navigation/header chrome."""
    lower = text.lower()
    return any(re.search(pat, lower) for pat in BOILERPLATE_PATTERNS)


def clean_excerpt_text(text: str) -> str:
    """Clean markdown formatting and newlines from raw excerpts for clear claim presentation."""
    cleaned = re.sub(r"#+\s*", "", text)
    cleaned = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", cleaned)  # Flatten markdown links
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def extract_claims_from_excerpt(
    raw_excerpt: str,
    source_url: str,
    source_title: str,
    category: ResearchCategoryType,
    max_claims: int = 2,
) -> list[ResearchFact]:
    """
    Extracts concrete factual claims directly from Parallel excerpts,
    filtering navigation boilerplate and preserving full source provenance.
    """
    facts: list[ResearchFact] = []
    paragraphs = [p.strip() for p in raw_excerpt.split("\n\n") if len(p.strip()) > 30]

    domain = urllib.parse.urlparse(source_url).netloc

    for paragraph in paragraphs:
        if is_boilerplate(paragraph):
            continue

        cleaned = clean_excerpt_text(paragraph)
        if len(cleaned) < 25:
            continue

        # Extract a concise, complete claim sentence for the claim field
        sentences = re.split(r"(?<=[.!?])\s+", cleaned)
        first_sentence = sentences[0].strip() if sentences else cleaned
        if 25 <= len(first_sentence) <= 220:
            claim_text = first_sentence
        elif len(cleaned) <= 220:
            claim_text = cleaned
        else:
            claim_text = cleaned[:217] + "..."

        facts.append(
            ResearchFact(
                claim=claim_text,
                source_url=source_url,
                source_title=source_title,
                source_domain=domain,
                evidence_text=cleaned,
                category=category,
                relevance_summary=f"Retrieved from {domain} via Parallel Search in category '{category}'",
            )
        )
        if len(facts) >= max_claims:
            break

    return facts


def research_category(
    client: Parallel,
    category: ResearchCategoryType,
    location: str,
    shoot_start_date: str,
    shoot_end_date: str,
    location_types: list[str],
) -> tuple[list[ResearchFact], Optional[str]]:
    """
    Executes a targeted search for a single category using Parallel.search.
    Returns (facts, error_message_if_failed). Never returns synthetic facts.
    """
    location_str = ", ".join(location_types) if location_types else "public locations"

    queries_map = {
        "filming_permits": {
            "query": f"{location} commercial filming permit application deadline turnaround authority",
            "objective": f"Find film permit application lead time, fees, and municipal requirements in {location}.",
        },
        "location_restrictions": {
            "query": f"{location} filming restrictions rules {location_str} drone night curfew sound",
            "objective": f"Identify filming restrictions, drone bans, noise curfews, and public property rules in {location}.",
        },
        "weather_climate": {
            "query": f"{location} historical weather climate forecast {shoot_start_date} to {shoot_end_date} rain wind temperature",
            "objective": f"Find typical weather conditions, rainfall risk, wind, and temperatures in {location} between {shoot_start_date} and {shoot_end_date}.",
        },
        "public_events": {
            "query": f"{location} public events festivals street closures holidays {shoot_start_date} to {shoot_end_date}",
            "objective": f"Find major public events, festivals, marathons, parades, or holidays in {location} between {shoot_start_date} and {shoot_end_date}.",
        },
        "regional_regulations": {
            "query": f"{location} film commission production guidelines safety police fire monitor insurance",
            "objective": f"Find regional film commission safety guidelines, fire officer requirements, and insurance thresholds in {location}.",
        },
    }

    config = queries_map[category]
    category_facts: list[ResearchFact] = []

    try:
        logger.info(f"Executing Parallel search for category: {category} | Query: {config['query']}")
        search_res = client.search(
            search_queries=[config["query"]],
            objective=config["objective"],
            mode="turbo",
        )

        seen_urls = set()
        for item in getattr(search_res, "results", []):
            url = getattr(item, "url", "")
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)

            title = getattr(item, "title", "") or "Web Source"
            domain = urllib.parse.urlparse(url).netloc
            excerpts = getattr(item, "excerpts", []) or []

            extracted_from_item = []
            for exc in excerpts:
                extracted = extract_claims_from_excerpt(
                    raw_excerpt=exc,
                    source_url=url,
                    source_title=title,
                    category=category,
                    max_claims=1,
                )
                extracted_from_item.extend(extracted)
                if len(extracted_from_item) >= 1:
                    break

            if extracted_from_item:
                category_facts.extend(extracted_from_item)
            elif title and not is_boilerplate(title):
                # Only use title if no excerpts exist and title is non-boilerplate
                category_facts.append(
                    ResearchFact(
                        claim=f"{title} (filming authority/resource for {location})",
                        source_url=url,
                        source_title=title,
                        source_domain=domain,
                        evidence_text=title,
                        category=category,
                        relevance_summary=f"Retrieved from {domain} via Parallel Search",
                    )
                )

            if len(category_facts) >= 3:
                break

        return category_facts, None

    except Exception as e:
        err_msg = f"Parallel Search failed for category '{category}': {e}"
        logger.error(err_msg)
        # CRITICAL RULE: Never generate synthetic facts. Return empty facts and record error.
        return [], err_msg


def run_parallel_research(
    location: str,
    shoot_start_date: str,
    shoot_end_date: str,
    location_types: Optional[list[str]] = None,
    progress_callback: Optional[Callable[[str, int, int], None]] = None,
) -> ResearchResult:
    """
    Executes live Parallel searches across all 5 mandatory categories sequentially.
    Never creates synthetic facts on failure.
    """
    client = Parallel(api_key=PARALLEL_API_KEY)
    all_facts: list[ResearchFact] = []
    category_counts: dict[str, int] = {}
    failed_categories: list[str] = []
    category_errors: dict[str, str] = {}

    categories_list = list(RESEARCH_CATEGORIES.keys())

    for idx, category in enumerate(categories_list, start=1):
        if progress_callback:
            progress_callback(category, idx, len(categories_list))

        facts, error_msg = research_category(
            client=client,
            category=category,  # type: ignore
            location=location,
            shoot_start_date=shoot_start_date,
            shoot_end_date=shoot_end_date,
            location_types=location_types or [],
        )

        if error_msg:
            failed_categories.append(category)
            category_errors[category] = error_msg
        elif not facts:
            failed_categories.append(category)

        all_facts.extend(facts)
        category_counts[category] = len(facts)

    return ResearchResult(
        location=location,
        shoot_start_date=shoot_start_date,
        shoot_end_date=shoot_end_date,
        total_facts=len(all_facts),
        category_counts=category_counts,
        facts=all_facts,
        failed_categories=failed_categories,
        category_errors=dict(category_errors) if isinstance(category_errors, dict) else {},
    )
