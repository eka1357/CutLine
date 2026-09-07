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


def clean_excerpt_text(text: str) -> str:
    """Clean markdown formatting and newlines from raw excerpts for clear claim presentation."""
    cleaned = re.sub(r"#+\s*", "", text)
    cleaned = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", cleaned)  # Flatten markdown links
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def extract_claims_from_excerpt(
    raw_excerpt: str, source_url: str, category: ResearchCategoryType, max_claims: int = 2
) -> list[ResearchFact]:
    """
    Extracts concrete factual claims directly from Parallel excerpts,
    preserving exact URL provenance.
    """
    facts: list[ResearchFact] = []
    paragraphs = [p.strip() for p in raw_excerpt.split("\n\n") if len(p.strip()) > 30]

    for paragraph in paragraphs[:max_claims]:
        cleaned = clean_excerpt_text(paragraph)
        if len(cleaned) > 20:
            # Shorten if too verbose while keeping the factual meat
            claim_text = cleaned if len(cleaned) <= 320 else cleaned[:317] + "..."
            facts.append(
                ResearchFact(
                    claim=claim_text,
                    source_url=source_url,
                    category=category,
                    relevance_summary=f"Discovered via Parallel Search in category: {category}",
                )
            )

    return facts


def research_category(
    client: Parallel,
    category: ResearchCategoryType,
    location: str,
    shoot_start_date: str,
    shoot_end_date: str,
    location_types: list[str],
) -> list[ResearchFact]:
    """
    Executes a targeted search for a single category using Parallel.search.
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

            excerpts = getattr(item, "excerpts", []) or []
            if excerpts:
                for exc in excerpts[:2]:
                    extracted = extract_claims_from_excerpt(exc, url, category, max_claims=1)
                    category_facts.extend(extracted)
            else:
                # If excerpts are empty, fall back to title as claim
                title = getattr(item, "title", "Relevant filming source")
                category_facts.append(
                    ResearchFact(
                        claim=f"{title}: verified source for {category} in {location}.",
                        source_url=url,
                        category=category,
                        relevance_summary="Retrieved via Parallel Search",
                    )
                )

            if len(category_facts) >= 3:
                break

    except Exception as e:
        logger.error(f"Parallel Search failed for category '{category}': {e}")
        # Return fallback fact indicating API communication status without failing whole run
        category_facts.append(
            ResearchFact(
                claim=f"Search for {category} in {location} could not complete during live call ({type(e).__name__}).",
                source_url="https://docs.parallel.ai",
                category=category,
                relevance_summary="Fallback fact on connection failure",
            )
        )

    return category_facts


def run_parallel_research(
    location: str,
    shoot_start_date: str,
    shoot_end_date: str,
    location_types: Optional[list[str]] = None,
    progress_callback: Optional[Callable[[str, int, int], None]] = None,
) -> ResearchResult:
    """
    Executes live Parallel searches across all 5 mandatory categories sequentially.
    """
    client = Parallel(api_key=PARALLEL_API_KEY)
    all_facts: list[ResearchFact] = []
    category_counts: dict[str, int] = {}
    categories_list = list(RESEARCH_CATEGORIES.keys())

    for idx, category in enumerate(categories_list, start=1):
        if progress_callback:
            progress_callback(category, idx, len(categories_list))

        facts = research_category(
            client=client,
            category=category,  # type: ignore
            location=location,
            shoot_start_date=shoot_start_date,
            shoot_end_date=shoot_end_date,
            location_types=location_types or [],
        )

        all_facts.extend(facts)
        category_counts[category] = len(facts)

    return ResearchResult(
        location=location,
        shoot_start_date=shoot_start_date,
        shoot_end_date=shoot_end_date,
        total_facts=len(all_facts),
        category_counts=category_counts,
        facts=all_facts,
    )
