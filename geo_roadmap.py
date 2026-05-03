import re

from analyzer import ask_ai


ROADMAP_COLUMNS = [
    "Priority",
    "Query Intent",
    "Content Asset",
    "Target Association",
    "Competitor / Market Signal",
    "Evidence Needed",
    "Expected Metric Impact",
    "Suggested Timing",
]

GENERIC_CONTENT_ASSETS = {
    "comparison page for top products",
    "faq page on product benefits",
    "review collection initiative",
    "evidence-building page on ingredients",
    "local recommendations resource hub",
    "premium skincare product guide",
    "audience-specific recommendations guide",
    "alternatives comparison page",
    "marketing campaign",
    "brand awareness campaign",
    "landing page",
}

HEALTH_ADJACENT_TERMS = (
    "skin",
    "skincare",
    "beauty",
    "wellness",
    "medical",
    "clinic",
    "health",
    "derma",
    "cosmetic",
)


def _dataframe_preview(df, max_rows=40):
    if df is None:
        return "No data provided."

    if hasattr(df, "empty") and df.empty:
        return "No data provided."

    if hasattr(df, "head") and hasattr(df, "to_string"):
        return df.head(max_rows).to_string(index=False)

    return str(df)


def _brand_intelligence_preview(brand_intelligence):
    if not brand_intelligence:
        return "No Brand Intelligence output provided."

    return f"""
Recommendation Drivers:
{brand_intelligence.get("recommendation_drivers", "")}

AI-Inferred Target Brand Understanding:
{brand_intelligence.get("target_brand_understanding", "")}

Positioning Gap Analysis:
{brand_intelligence.get("positioning_gap_analysis", "")}
""".strip()


def normalize_text(value):
    return " ".join(str(value or "").strip().lower().split())


def contains_tracked_brand(value, tracked_competitors):
    normalized_value = normalize_text(value)
    for competitor in tracked_competitors or []:
        normalized_competitor = normalize_text(competitor)
        if normalized_competitor and normalized_competitor in normalized_value:
            return competitor
    return None


def _is_health_adjacent_category(category):
    normalized_category = normalize_text(category)
    return any(term in normalized_category for term in HEALTH_ADJACENT_TERMS)


def sanitize_claim_safety(text, category):
    if not _is_health_adjacent_category(category):
        return str(text)

    replacements = [
        (
            r"published studies demonstrating product effectiveness",
            "substantiated evidence or consumer study documentation",
        ),
        (
            r"clinical validations",
            "expert validation and claims support documentation",
        ),
        (
            r"clinical trials",
            "claims support documentation, only where substantiated and compliant",
        ),
        (
            r"clinical efficacy",
            "substantiated product evidence",
        ),
        (
            r"clinically effective",
            "evidence-supported",
        ),
        (
            r"prove effectiveness",
            "support product claims",
        ),
        (
            r"medical-grade claims",
            "professional-grade positioning, where substantiated",
        ),
    ]

    sanitized = str(text)
    for pattern, replacement in replacements:
        sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)

    return sanitized


def is_generic_content_asset(asset):
    normalized_asset = normalize_text(asset)
    if normalized_asset in GENERIC_CONTENT_ASSETS:
        return True

    generic_patterns = [
        "comparison page for top products",
        "faq page on product benefits",
        "review collection initiative",
        "evidence-building page on ingredients",
        "local recommendations resource hub",
        "alternatives comparison page",
    ]

    return any(pattern in normalized_asset for pattern in generic_patterns)


def rewrite_generic_content_asset(
    asset,
    brand,
    market,
    category,
    audience,
    query_intent,
    competitor_signal,
):
    normalized_asset = normalize_text(asset)
    tracked_competitor = None
    competitor_match = re.search(
        r"([A-Z][A-Za-z0-9.&'-]+(?:\s+[A-Z][A-Za-z0-9.&'-]+)*)",
        str(competitor_signal or ""),
    )
    if competitor_match:
        tracked_competitor = competitor_match.group(1)

    if "comparison page" in normalized_asset:
        if tracked_competitor:
            return f"{brand} vs {tracked_competitor} Comparison Page for {market} Consumers"
        return f"{brand} vs Top {category.title()} Comparison Page for {market} Consumers"

    if "faq page on product benefits" in normalized_asset:
        return f"{brand} Product Benefits FAQ for {audience.title()} in {market}"

    if "review collection initiative" in normalized_asset:
        return f"{brand} {market} Customer Review Collection Page"

    if "evidence-building page on ingredients" in normalized_asset:
        return f"{brand} Ingredient Evidence & Product Selection Page"

    if "local recommendations resource hub" in normalized_asset:
        return f"{market} Local {category.title()} Recommendations Resource Hub Featuring {brand}"

    if "audience-specific recommendations guide" in normalized_asset:
        return f"{audience.title()} Guide to {brand} Product Fit"

    if "alternatives comparison page" in normalized_asset:
        return f"{brand} Alternatives Comparison Page for {market} {category.title()} Consumers"

    if normalized_asset == "landing page":
        return f"{brand} {market} {query_intent} Landing Page"

    if normalized_asset == "marketing campaign":
        return f"{brand} {market} {query_intent} Content Hub"

    if normalized_asset == "brand awareness campaign":
        return f"{brand} Brand Proof & Review Page for {market}"

    return asset


def _normalize_competitor_signal_cell(value, tracked_competitors):
    text = str(value or "").strip()
    if not text:
        return text

    if "(Tracked competitor)" in text or "(AI-discovered market signal)" in text:
        return text

    tracked_brand = contains_tracked_brand(text, tracked_competitors)
    if tracked_brand:
        return f"{text} (Tracked competitor)"

    return text


def sanitize_geo_roadmap_markdown(
    roadmap_md,
    brand,
    market,
    category,
    audience,
    tracked_competitors,
):
    lines = str(roadmap_md or "").splitlines()
    sanitized_lines = []

    for index, line in enumerate(lines):
        if not line.strip().startswith("|"):
            sanitized_lines.append(sanitize_claim_safety(line, category))
            continue

        parts = [part.strip() for part in line.split("|")[1:-1]]
        if index < 2 or len(parts) != len(ROADMAP_COLUMNS):
            sanitized_lines.append(sanitize_claim_safety(line, category))
            continue

        query_intent = parts[1]
        content_asset = parts[2]
        competitor_signal = parts[4]
        evidence_needed = parts[5]
        expected_metric_impact = parts[6]

        if is_generic_content_asset(content_asset):
            parts[2] = rewrite_generic_content_asset(
                content_asset,
                brand,
                market,
                category,
                audience,
                query_intent,
                competitor_signal,
            )

        parts[4] = _normalize_competitor_signal_cell(
            competitor_signal,
            tracked_competitors,
        )
        parts[5] = sanitize_claim_safety(evidence_needed, category)
        parts[6] = sanitize_claim_safety(expected_metric_impact, category)

        sanitized_lines.append("| " + " | ".join(parts) + " |")

    return "\n".join(sanitized_lines)


def build_geo_content_roadmap_prompt(
    brand,
    category,
    market,
    audience,
    competitors,
    summary_df,
    detailed_df,
    brand_intelligence,
    query_intent_categories,
):
    columns = " | ".join(ROADMAP_COLUMNS)

    return f"""
You are creating a GEO Content Roadmap for a consulting deliverable.

This is a strategic execution plan. It is not part of visibility scoring, share of voice, or benchmark calculations.

Target Brand:
{brand}

Category:
{category}

Market:
{market}

Audience:
{audience}

Tracked Competitors:
{", ".join(competitors)}

Query Intent Categories:
{", ".join(query_intent_categories)}

Summary Data:
{_dataframe_preview(summary_df)}

Detailed Prompt-Level Data:
{_dataframe_preview(detailed_df)}

Brand Intelligence:
{_brand_intelligence_preview(brand_intelligence)}

Task:
Create an actionable GEO Content Roadmap that links query intent, content assets, trust signals, competitor or market signals, evidence needs, and expected metric impact.

Return only a markdown table with these exact columns:
{columns}

Rules:
- Use concise consulting-ready wording.
- Include 6 to 8 roadmap rows maximum.
- Tie each row to a query intent or strategic opportunity.
- Every row must have a distinct content asset.
- Do not repeat the same asset under different wording.
- Every Content Asset must be a specific publishable title.
- Every Content Asset must include at least one of: target brand, market, query intent, competitor name, audience segment, or a concrete use case.
- Generic assets are forbidden.
- Every Content Asset must be a publishable page, article, guide, landing page, comparison page, FAQ, evidence page, review program page, event recap, or resource hub.
- Content Asset should name a distinct content asset that is concrete, execution-oriented, and publishable, such as a landing page, comparison page, FAQ, review collection initiative, event recap page, or evidence-building page.
- Avoid vague assets such as marketing campaign, online engagement, or brand awareness campaign unless paired with a specific page or content asset.
- Do not use vague/internal strategy assets such as "Luxury branding strategy page", "comparison page for top products", or "landing page for local clinics" unless rewritten as a concrete publishable asset.
- Generic assets are forbidden, including "Comparison Page for Top Products", "FAQ Page on Product Benefits", "Review Collection Initiative", "Evidence-Building Page on Ingredients", "Local Recommendations Resource Hub", "Premium skincare product guide", "Audience-specific recommendations guide", "Alternatives comparison page", "Marketing campaign", "Brand awareness campaign", or "Landing page" unless rewritten with a specific brand, topic, use case, or market.
- Evidence Needed must be concrete and should describe proof points such as customer reviews, Wi-Fi speed proof, outlet availability, location photos, customer survey quotes, local press mentions, Google reviews, comparison table data, expert input, or AI-citable sources.
- Evidence Needed must be concrete and safe.
- Prefer customer reviews, professional testimonials, expert quotes, clinic partner mentions, ingredient documentation, claims support documentation, consumer study, comparison table data, local press mentions, Google reviews, customer survey quotes, or substantiated before/after evidence.
- Avoid unsupported wording such as clinical trials, clinical efficacy, published studies, prove effectiveness, or medical-grade claims unless framed as only where substantiated and compliant.
- Expected Metric Impact must reference one or more benchmark metrics: total mentions, average visibility score, prompts visible, share of voice, query intent visibility, or target-brand association.
- Intended benchmark influence should use benchmark metrics such as total_mentions, average_visibility_score, prompts_visible, share_of_voice_percent, query intent visibility, or target-brand association.
- Do not claim guaranteed metric improvement. Phrase impact as intended benchmark influence.
- Expected Metric Impact must use the phrase "Intended benchmark influence:" and must not reference conversion rate, session duration, sales, or increase by X%.
- Suggested Timing must use only these values: 30 Days, 60 Days, 90 Days, or Next Benchmark Cycle.
- No calendar quarters, past dates, or specific years. Do not use timing such as Q2 2024, Q3 2024, 2025, or 2026.
- If query intent coverage is limited, such as a Quick Test Mode run or a small number of query intent categories, make the roadmap directional and avoid implying broad market coverage beyond what was tested.
- For skincare, health-adjacent, or regulated-ish categories, avoid recommending unsupported clinical or medical claims.
- Do not tell the brand to conduct clinical trials as a default action.
- Prefer third-party evidence, expert validation, professional review, ingredient documentation, consumer study, substantiated before/after evidence, or clinic partner testimonial.
- Only use clinical-study claims if substantiated and compliant.
- If a competitor or market signal is named, label tracked competitors as "(Tracked competitor)" and non-tracked brands as "(AI-discovered market signal)".
- Do not imply AI-discovered market signals are included in scoring.
- Do not invent unsupported facts.
- Do not make unsupported performance promises.
- Do not create or modify scores.
- Do not include narrative before or after the table.
""".strip()


def generate_geo_content_roadmap(
    brand,
    category,
    market,
    audience,
    competitors,
    summary_df,
    detailed_df,
    brand_intelligence,
    query_intent_categories,
    report_language="English",
):
    prompt = build_geo_content_roadmap_prompt(
        brand=brand,
        category=category,
        market=market,
        audience=audience,
        competitors=competitors,
        summary_df=summary_df,
        detailed_df=detailed_df,
        brand_intelligence=brand_intelligence,
        query_intent_categories=query_intent_categories,
    )

    roadmap_md = ask_ai(prompt, report_language)

    return sanitize_geo_roadmap_markdown(
        roadmap_md,
        brand=brand,
        market=market,
        category=category,
        audience=audience,
        tracked_competitors=competitors,
    )
