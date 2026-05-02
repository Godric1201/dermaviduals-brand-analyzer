import re

from analyzer import ask_ai


def build_competitor_suggestion_prompt(
    brand,
    category,
    market,
    audience,
    existing_competitors=None,
    max_suggestions=8,
):
    existing_competitors = existing_competitors or []
    existing_text = "None provided"
    if existing_competitors:
        existing_text = "\n".join(f"- {item}" for item in existing_competitors)

    return f"""
You are helping configure an AI visibility benchmark.

Suggest up to {max_suggestions} relevant benchmark competitors for the target brand.

Target Brand:
{brand}

Category:
{category}

Market:
{market}

Audience:
{audience}

Existing tracked competitors:
{existing_text}

Rules:
- Return one competitor per line.
- Do not include explanations, numbering, bullets, or extra commentary.
- Do not include duplicates.
- Do not include the target brand.
- Do not repeat existing tracked competitors.
- Suggestions are candidates only and are not automatically included in scoring.
""".strip()


def parse_competitor_suggestions(
    text,
    existing_competitors=None,
    max_suggestions=8,
):
    existing_competitors = existing_competitors or []
    excluded = {
        str(item).strip().lower()
        for item in existing_competitors
        if str(item).strip()
    }
    seen = set()
    suggestions = []

    for line in str(text).splitlines():
        cleaned = line.strip()
        cleaned = re.sub(r"^(?:[-*•]\s*|\d+[\.)]\s*)", "", cleaned).strip()

        if not cleaned:
            continue

        key = cleaned.lower()
        if key in excluded or key in seen:
            continue

        seen.add(key)
        suggestions.append(cleaned)

        if len(suggestions) >= max_suggestions:
            break

    return suggestions


def suggest_competitors_with_ai(
    brand,
    category,
    market,
    audience,
    existing_competitors=None,
    max_suggestions=8,
    answer_language="English",
):
    existing_competitors = existing_competitors or []
    prompt = build_competitor_suggestion_prompt(
        brand=brand,
        category=category,
        market=market,
        audience=audience,
        existing_competitors=existing_competitors,
        max_suggestions=max_suggestions,
    )
    result = ask_ai(prompt, answer_language)
    excluded = [brand] + list(existing_competitors)

    return parse_competitor_suggestions(
        result,
        existing_competitors=excluded,
        max_suggestions=max_suggestions,
    )
