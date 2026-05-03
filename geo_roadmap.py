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
- Every Content Asset must be a publishable page, article, guide, landing page, comparison page, FAQ, evidence page, review program page, event recap, or resource hub.
- Content Asset should name a distinct content asset that is concrete, execution-oriented, and publishable, such as a landing page, comparison page, FAQ, review collection initiative, event recap page, or evidence-building page.
- Avoid vague assets such as marketing campaign, online engagement, or brand awareness campaign unless paired with a specific page or content asset.
- Do not use vague/internal strategy assets such as "Luxury branding strategy page", "comparison page for top products", or "landing page for local clinics" unless rewritten as a concrete publishable asset.
- Evidence Needed must be concrete and should describe proof points such as customer reviews, Wi-Fi speed proof, outlet availability, location photos, customer survey quotes, local press mentions, Google reviews, comparison table data, expert input, or AI-citable sources.
- Expected Metric Impact must reference one or more benchmark metrics: total mentions, average visibility score, prompts visible, share of voice, query intent visibility, or target-brand association.
- Intended benchmark influence should use benchmark metrics such as total_mentions, average_visibility_score, prompts_visible, share_of_voice_percent, query intent visibility, or target-brand association.
- Do not claim guaranteed metric improvement. Phrase impact as intended benchmark influence.
- Suggested Timing must use only these values: 30 Days, 60 Days, 90 Days, or Next Benchmark Cycle.
- No calendar quarters, past dates, or specific years. Do not use timing such as Q2 2024, Q3 2024, 2025, or 2026.
- If query intent coverage is limited, such as a Quick Test Mode run or a small number of query intent categories, make the roadmap directional and avoid implying broad market coverage beyond what was tested.
- For skincare, health-adjacent, or regulated-ish categories, avoid recommending unsupported clinical or medical claims.
- Do not tell the brand to conduct clinical trials as a default action.
- Prefer third-party evidence, expert validation, professional review, ingredient documentation, consumer study, substantiated before/after evidence, or clinic partner testimonial.
- Only use clinical-study claims if substantiated and compliant.
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

    return ask_ai(prompt, report_language)
